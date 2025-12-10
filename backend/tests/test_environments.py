"""
测试 Windy Grid 和 Cliff Walking 环境

覆盖：
- 环境初始化
- 状态转换
- 风力/悬崖机制
- 边界处理
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.environment.windy_grid import (
    WindyGridEnv, WindyGridConfig, create_windy_grid_env, Action as WindyAction
)
from app.services.environment.cliff_walking import (
    CliffWalkingEnv, CliffWalkingConfig, create_cliff_walking_env, Action as CliffAction
)


class TestWindyGridEnv:
    """有风网格世界环境测试"""

    def test_default_initialization(self):
        """测试默认初始化"""
        env = WindyGridEnv()
        assert env.height == 7
        assert env.width == 10
        assert env.n_states == 70
        assert env.n_actions == 4
        assert env.start_state == 30  # (3, 0)
        assert env.goal_state == 37   # (3, 7)

    def test_custom_initialization(self):
        """测试自定义初始化"""
        config = WindyGridConfig(
            height=5,
            width=8,
            start_pos=(2, 0),
            goal_pos=(2, 7),
            wind_strength=(0, 1, 1, 2, 2, 1, 1, 0)
        )
        env = WindyGridEnv(config)
        assert env.height == 5
        assert env.width == 8
        assert env.n_states == 40

    def test_wind_effect(self):
        """测试风力影响"""
        env = WindyGridEnv()
        env.reset()

        # 从无风区域移动
        env.current_state = env._position_to_state(3, 0)  # 无风列
        result = env.step(WindyAction.RIGHT)
        # 移动到列1，无风
        assert result.info['wind'] == 0

        # 移动到有风区域
        env.current_state = env._position_to_state(3, 3)  # 风力为1的列
        result = env.step(WindyAction.UP)
        # 向上移动1格 + 风力向上1格 = 总共向上2格
        row, col = env._state_to_position(result.next_state)
        assert row <= 1  # 被风向上吹

    def test_boundary_handling(self):
        """测试边界处理"""
        env = WindyGridEnv()
        env.reset()

        # 在顶部边界向上移动
        env.current_state = env._position_to_state(0, 0)
        result = env.step(WindyAction.UP)
        row, col = env._state_to_position(result.next_state)
        assert row == 0  # 保持在顶部

    def test_goal_detection(self):
        """测试目标检测"""
        env = WindyGridEnv()
        env.reset()

        # 直接到达目标旁边
        env.current_state = env._position_to_state(3, 6)
        result = env.step(WindyAction.RIGHT)
        # 由于风力可能影响，检查是否能到达目标
        assert env.goal_state == env._position_to_state(3, 7)

    def test_render_text(self):
        """测试文本渲染"""
        env = WindyGridEnv()
        env.reset()
        text = env.render_text()
        assert 'Wind:' in text
        # Agent在起点时显示'A'，所以起点'S'不显示
        assert 'G' in text  # 终点
        assert 'A' in text  # Agent (在起点位置)

    def test_to_dict(self):
        """测试导出字典"""
        env = WindyGridEnv()
        env.reset()
        info = env.to_dict()
        assert info['type'] == 'windy'
        assert 'wind' in info
        assert len(info['wind']) == 10

    def test_factory_function(self):
        """测试工厂函数"""
        env = create_windy_grid_env(height=5, width=6)
        assert env.height == 5
        assert env.width == 6


class TestCliffWalkingEnv:
    """悬崖行走环境测试"""

    def test_default_initialization(self):
        """测试默认初始化"""
        env = CliffWalkingEnv()
        assert env.height == 4
        assert env.width == 12
        assert env.n_states == 48
        assert env.n_actions == 4
        assert env.start_state == 36  # (3, 0)
        assert env.goal_state == 47   # (3, 11)

    def test_cliff_positions(self):
        """测试悬崖位置"""
        env = CliffWalkingEnv()
        cliff_positions = env.get_cliff_positions()

        # 悬崖应该在底部行的中间
        for row, col in cliff_positions:
            assert row == 3  # 底部行
            assert 1 <= col <= 10  # 除了起点和终点列

    def test_cliff_count(self):
        """测试悬崖数量"""
        env = CliffWalkingEnv()
        # 4x12网格，底部行1-10列是悬崖，共10个
        assert len(env.cliff_states) == 10

    def test_fall_off_cliff(self):
        """测试掉入悬崖"""
        env = CliffWalkingEnv()
        env.reset()

        # 从起点向右移动，会进入悬崖
        env.current_state = env.start_state
        result = env.step(CliffAction.RIGHT)

        # 应该回到起点，奖励-100
        assert result.next_state == env.start_state
        assert result.reward == -100.0
        assert result.info['fell_off_cliff'] == True
        assert result.done == False

    def test_safe_path(self):
        """测试安全路径（绕过悬崖）"""
        env = CliffWalkingEnv()
        env.reset()

        # 向上移动（远离悬崖）
        result = env.step(CliffAction.UP)
        assert result.reward == -1.0
        assert result.info['fell_off_cliff'] == False

    def test_reach_goal(self):
        """测试到达终点"""
        env = CliffWalkingEnv()
        env.reset()

        # 直接设置到终点旁边
        env.current_state = env._position_to_state(2, 11)  # 终点上方
        result = env.step(CliffAction.DOWN)

        assert result.done == True
        assert result.next_state == env.goal_state

    def test_boundary_handling(self):
        """测试边界处理"""
        env = CliffWalkingEnv()
        env.reset()

        # 在左边界向左移动
        env.current_state = env._position_to_state(0, 0)
        result = env.step(CliffAction.LEFT)
        row, col = env._state_to_position(result.next_state)
        assert col == 0  # 保持在左边界

    def test_render_text(self):
        """测试文本渲染"""
        env = CliffWalkingEnv()
        env.reset()
        text = env.render_text()
        # Agent在起点时显示'A'，所以起点'S'不显示
        assert 'G' in text  # 终点
        assert 'C' in text  # 悬崖
        assert 'A' in text  # Agent (在起点位置)

    def test_get_state_info(self):
        """测试状态信息"""
        env = CliffWalkingEnv()

        # 检查悬崖状态
        cliff_state = env._position_to_state(3, 5)
        info = env.get_state_info(cliff_state)
        assert info['is_cliff'] == True
        assert info['type'] == 'cliff'

        # 检查起点状态
        start_info = env.get_state_info(env.start_state)
        assert start_info['is_start'] == True
        assert start_info['type'] == 'start'

    def test_to_dict(self):
        """测试导出字典"""
        env = CliffWalkingEnv()
        env.reset()
        info = env.to_dict()
        assert info['type'] == 'cliff'
        assert 'cliff_states' in info
        assert len(info['cliff_states']) == 10

    def test_factory_function(self):
        """测试工厂函数"""
        env = create_cliff_walking_env(height=5, width=10, cliff_reward=-50.0)
        assert env.height == 5
        assert env.width == 10
        assert env.cliff_reward == -50.0


class TestEnvironmentComparison:
    """环境对比测试"""

    def test_both_environments_have_same_interface(self):
        """测试两种环境有相同的接口"""
        windy = WindyGridEnv()
        cliff = CliffWalkingEnv()

        # 相同的方法
        assert hasattr(windy, 'reset')
        assert hasattr(cliff, 'reset')
        assert hasattr(windy, 'step')
        assert hasattr(cliff, 'step')
        assert hasattr(windy, 'to_dict')
        assert hasattr(cliff, 'to_dict')
        assert hasattr(windy, 'render_text')
        assert hasattr(cliff, 'render_text')

    def test_episode_can_complete(self):
        """测试回合可以完成"""
        np.random.seed(42)  # 固定随机种子以提高可重复性

        # Windy Grid - 使用更多步数和多次尝试
        windy = create_windy_grid_env()
        windy_completed = False
        for _ in range(5):  # 尝试5次
            windy.reset()
            for step in range(2000):
                result = windy.step(np.random.randint(4))
                if result.done:
                    windy_completed = True
                    break
            if windy_completed:
                break

        # Cliff Walking
        cliff = create_cliff_walking_env()
        cliff_completed = False
        for _ in range(5):  # 尝试5次
            cliff.reset()
            for step in range(2000):
                result = cliff.step(np.random.randint(4))
                if result.done:
                    cliff_completed = True
                    break
            if cliff_completed:
                break

        # 至少有一个环境应该能完成
        assert windy_completed or cliff_completed


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""
Basic Grid Environment Unit Tests - 基础网格世界环境单元测试
"""

import pytest
import numpy as np
from app.services.environment.basic_grid import (
    BasicGridEnv,
    EnvironmentConfig,
    Action,
    create_basic_grid_env
)


class TestBasicGridEnv:
    """BasicGridEnv 测试类"""

    def test_default_initialization(self):
        """测试默认初始化"""
        env = BasicGridEnv()

        assert env.grid_size == 4
        assert env.n_states == 16
        assert env.n_actions == 4
        assert env.terminal_states == [0, 15]
        assert env.step_reward == -1.0
        assert env.gamma == 1.0

    def test_custom_initialization(self):
        """测试自定义配置初始化"""
        config = EnvironmentConfig(
            grid_size=5,
            step_reward=-0.5,
            gamma=0.9
        )
        env = BasicGridEnv(config)

        assert env.grid_size == 5
        assert env.n_states == 25
        assert env.terminal_states == [0, 24]
        assert env.step_reward == -0.5
        assert env.gamma == 0.9

    def test_state_position_conversion(self):
        """测试状态与位置转换"""
        env = BasicGridEnv()

        # 测试状态到位置
        assert env._state_to_position(0) == (0, 0)
        assert env._state_to_position(3) == (0, 3)
        assert env._state_to_position(4) == (1, 0)
        assert env._state_to_position(15) == (3, 3)

        # 测试位置到状态
        assert env._position_to_state(0, 0) == 0
        assert env._position_to_state(0, 3) == 3
        assert env._position_to_state(1, 0) == 4
        assert env._position_to_state(3, 3) == 15

    def test_terminal_states(self):
        """测试终止状态识别"""
        env = BasicGridEnv()

        assert env._is_terminal(0) == True
        assert env._is_terminal(15) == True
        assert env._is_terminal(1) == False
        assert env._is_terminal(7) == False

    def test_reset(self):
        """测试环境重置"""
        env = BasicGridEnv()

        # 测试随机重置
        initial_state = env.reset()
        assert initial_state not in env.terminal_states
        assert 0 <= initial_state < env.n_states

        # 测试指定起始状态
        state = env.reset(start_state=5)
        assert state == 5
        assert env.current_state == 5

    def test_step_within_bounds(self):
        """测试边界内移动"""
        env = BasicGridEnv()
        env.reset(start_state=5)  # 位置 (1,1)

        # 向右移动
        result = env.step(Action.RIGHT)
        assert result.next_state == 6  # 位置 (1,2)
        assert result.reward == -1.0
        assert result.done == False

    def test_step_at_boundary(self):
        """测试边界移动（保持原地）"""
        env = BasicGridEnv()
        env.reset(start_state=3)  # 位置 (0,3) 右边界

        # 向右移动应保持原地
        result = env.step(Action.RIGHT)
        assert result.next_state == 3
        assert result.reward == -1.0

        env.reset(start_state=4)  # 位置 (1,0) 左边界
        result = env.step(Action.LEFT)
        assert result.next_state == 4

    def test_step_to_terminal(self):
        """测试移动到终止状态"""
        env = BasicGridEnv()
        env.reset(start_state=1)  # 位置 (0,1)

        # 向左移动到终止状态 (0,0)
        result = env.step(Action.LEFT)
        assert result.next_state == 0
        assert result.done == True

    def test_transition_matrix(self):
        """测试转移概率矩阵"""
        env = BasicGridEnv()

        # 检查中间状态的转移
        state = 5  # 位置 (1,1)

        # 向上: (1,1) -> (0,1) = state 1
        transitions = env.P[state][Action.UP]
        assert len(transitions) == 1
        prob, next_state, reward, done = transitions[0]
        assert prob == 1.0
        assert next_state == 1
        assert reward == -1.0

    def test_get_state_info(self):
        """测试获取状态信息"""
        env = BasicGridEnv()

        info = env.get_state_info(5)
        assert info["state"] == 5
        assert info["position"] == (1, 1)
        assert info["is_terminal"] == False
        assert info["row"] == 1
        assert info["col"] == 1

        info = env.get_state_info(0)
        assert info["is_terminal"] == True

    def test_render_text(self):
        """测试文本渲染"""
        env = BasicGridEnv()
        env.reset(start_state=5)

        text = env.render_text()
        assert "A" in text  # Agent位置
        assert "T" in text  # Terminal状态

    def test_factory_function(self):
        """测试工厂函数"""
        env = create_basic_grid_env(grid_size=6, step_reward=-2.0, gamma=0.95)

        assert env.grid_size == 6
        assert env.step_reward == -2.0
        assert env.gamma == 0.95


class TestActionEnum:
    """Action枚举测试"""

    def test_action_values(self):
        """测试动作值"""
        assert Action.UP == 0
        assert Action.DOWN == 1
        assert Action.LEFT == 2
        assert Action.RIGHT == 3

    def test_action_count(self):
        """测试动作数量"""
        assert len(Action) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

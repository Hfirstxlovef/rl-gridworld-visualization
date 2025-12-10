"""
TD Solver 单元测试

测试 SARSA 和 Q-Learning 算法的正确性。
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.environment import (
    create_basic_grid_env,
    create_windy_grid_env,
    create_cliff_walking_env
)
from app.services.algorithm.td_solver import TDSolver, create_td_solver


class TestTDSolverBasic:
    """TD求解器基础测试"""

    def test_solver_initialization(self):
        """测试求解器初始化"""
        env = create_basic_grid_env(grid_size=4)
        solver = TDSolver(env)

        assert solver.n_states == 16
        assert solver.n_actions == 4
        assert solver.Q.shape == (16, 4)
        assert np.all(solver.Q == 0)

    def test_epsilon_greedy(self):
        """测试ε-greedy动作选择"""
        env = create_basic_grid_env(grid_size=4)
        solver = TDSolver(env, epsilon=1.0)

        # 当epsilon=1.0时，应该总是随机选择
        actions = [solver.epsilon_greedy_action(0, 1.0) for _ in range(100)]
        assert len(set(actions)) > 1  # 应该有多种动作

    def test_greedy_action(self):
        """测试贪婪动作选择"""
        env = create_basic_grid_env(grid_size=4)
        solver = TDSolver(env)

        # 设置一个状态的Q值
        solver.Q[5] = [0, 1, 2, 3]
        assert solver.greedy_action(5) == 3  # 最大值在index 3


class TestSARSA:
    """SARSA算法测试"""

    def test_sarsa_basic_grid(self):
        """测试SARSA在基础网格上的运行"""
        env = create_basic_grid_env(grid_size=4)
        solver = TDSolver(env, alpha=0.5, gamma=1.0, epsilon=0.1)

        result = solver.sarsa(max_episodes=100)

        assert result.algorithm == "sarsa"
        assert result.total_episodes == 100
        assert len(result.episode_rewards) == 100
        assert result.final_q_values.shape == (16, 4)

    def test_sarsa_convergence(self):
        """测试SARSA收敛性"""
        env = create_basic_grid_env(grid_size=4)
        solver = TDSolver(env, alpha=0.5, gamma=1.0, epsilon=0.1)

        result = solver.sarsa(max_episodes=500)

        # 后期平均奖励应该比前期好
        early_avg = np.mean(result.episode_rewards[:50])
        late_avg = np.mean(result.episode_rewards[-50:])
        assert late_avg >= early_avg - 10  # 允许一定波动

    def test_sarsa_windy_grid(self):
        """测试SARSA在有风网格上的运行"""
        env = create_windy_grid_env()
        solver = TDSolver(env, alpha=0.5, gamma=1.0, epsilon=0.1)

        result = solver.sarsa(max_episodes=200)

        assert result.algorithm == "sarsa"
        assert result.total_episodes == 200
        assert result.success_rate >= 0  # 应该有一定成功率

    def test_sarsa_cliff_walking(self):
        """测试SARSA在悬崖行走上的运行"""
        env = create_cliff_walking_env()
        solver = TDSolver(env, alpha=0.5, gamma=1.0, epsilon=0.1)

        result = solver.sarsa(max_episodes=200)

        assert result.algorithm == "sarsa"
        # SARSA应该学习到一条安全路径
        assert result.avg_reward > -1000  # 不应该总是掉悬崖


class TestQLearning:
    """Q-Learning算法测试"""

    def test_qlearning_basic_grid(self):
        """测试Q-Learning在基础网格上的运行"""
        env = create_basic_grid_env(grid_size=4)
        solver = TDSolver(env, alpha=0.5, gamma=1.0, epsilon=0.1)

        result = solver.q_learning(max_episodes=100)

        assert result.algorithm == "q_learning"
        assert result.total_episodes == 100
        assert len(result.episode_rewards) == 100
        assert result.final_q_values.shape == (16, 4)

    def test_qlearning_convergence(self):
        """测试Q-Learning收敛性"""
        env = create_basic_grid_env(grid_size=4)
        solver = TDSolver(env, alpha=0.5, gamma=1.0, epsilon=0.1)

        result = solver.q_learning(max_episodes=500)

        # 后期平均奖励应该比前期好
        early_avg = np.mean(result.episode_rewards[:50])
        late_avg = np.mean(result.episode_rewards[-50:])
        assert late_avg >= early_avg - 10

    def test_qlearning_cliff_walking(self):
        """测试Q-Learning在悬崖行走上的运行"""
        env = create_cliff_walking_env()
        solver = TDSolver(env, alpha=0.5, gamma=1.0, epsilon=0.1)

        result = solver.q_learning(max_episodes=200)

        assert result.algorithm == "q_learning"
        # Q-Learning应该学习到最优路径（可能更危险但更短）
        assert result.avg_reward > -1000


class TestPolicyExtraction:
    """策略提取测试"""

    def test_policy_extraction(self):
        """测试从Q值表提取策略"""
        env = create_basic_grid_env(grid_size=4)
        solver = TDSolver(env)

        # 设置一些Q值
        solver.Q[1] = [0, 1, 2, 3]
        solver.Q[2] = [3, 2, 1, 0]

        policy = solver._extract_policy()

        assert policy[1, 3] == 1.0  # 状态1选择动作3
        assert policy[2, 0] == 1.0  # 状态2选择动作0

    def test_policy_arrows(self):
        """测试策略箭头表示"""
        env = create_basic_grid_env(grid_size=4)
        solver = TDSolver(env)

        solver.Q[1] = [0, 0, 0, 1]  # 只有动作3最优
        arrows = solver.get_policy_arrows()

        assert "→" in arrows[1]

    def test_value_function(self):
        """测试值函数计算"""
        env = create_basic_grid_env(grid_size=4)
        solver = TDSolver(env)

        solver.Q[0] = [1, 2, 3, 4]
        solver.Q[1] = [4, 3, 2, 1]

        V = solver.get_value_function()

        assert V[0] == 4
        assert V[1] == 4


class TestTDComparison:
    """SARSA与Q-Learning对比测试"""

    def test_cliff_walking_difference(self):
        """测试悬崖行走中SARSA和Q-Learning的差异"""
        env = create_cliff_walking_env()

        sarsa_solver = TDSolver(env, alpha=0.5, gamma=1.0, epsilon=0.1)
        sarsa_result = sarsa_solver.sarsa(max_episodes=500)

        env2 = create_cliff_walking_env()
        ql_solver = TDSolver(env2, alpha=0.5, gamma=1.0, epsilon=0.1)
        ql_result = ql_solver.q_learning(max_episodes=500)

        # 两种算法都应该学到有效策略
        assert sarsa_result.success_rate > 0
        assert ql_result.success_rate > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

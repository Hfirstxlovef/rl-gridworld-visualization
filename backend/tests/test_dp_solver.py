"""
DP Solver Unit Tests - 动态规划求解器单元测试
"""

import pytest
import numpy as np
from app.services.environment.basic_grid import BasicGridEnv, EnvironmentConfig
from app.services.algorithm.dp_solver import (
    DPSolver,
    DPAlgorithmType,
    create_dp_solver
)


class TestDPSolver:
    """DPSolver 测试类"""

    @pytest.fixture
    def env(self):
        """创建测试环境"""
        return BasicGridEnv()

    @pytest.fixture
    def solver(self, env):
        """创建测试求解器"""
        return DPSolver(env, gamma=1.0, theta=1e-6)

    def test_initialization(self, solver, env):
        """测试初始化"""
        assert solver.gamma == 1.0
        assert solver.theta == 1e-6
        assert len(solver.V) == env.n_states
        assert solver.policy.shape == (env.n_states, env.n_actions)

    def test_random_policy_initialization(self, solver, env):
        """测试随机策略初始化"""
        # 非终止状态应该是均匀分布
        for state in range(env.n_states):
            if state not in env.terminal_states:
                assert np.allclose(solver.policy[state].sum(), 1.0)
                assert np.allclose(solver.policy[state], 0.25)
            else:
                assert np.allclose(solver.policy[state].sum(), 0.0)

    def test_policy_evaluation(self, solver):
        """测试策略评估"""
        V, records = solver.policy_evaluation()

        # 值函数应该收敛
        assert len(V) == solver.env.n_states

        # 终止状态值应为0
        for ts in solver.env.terminal_states:
            assert V[ts] == 0.0

        # 非终止状态应该有负值（因为 reward=-1）
        for state in range(solver.env.n_states):
            if state not in solver.env.terminal_states:
                assert V[state] < 0

    def test_policy_improvement(self, solver):
        """测试策略改进"""
        # 先进行策略评估
        solver.policy_evaluation()

        # 策略改进
        new_policy, stable = solver.policy_improvement()

        # 策略应该有所改变或保持稳定
        assert new_policy.shape == solver.policy.shape

        # 每个非终止状态应该选择最优动作
        for state in range(solver.env.n_states):
            if state not in solver.env.terminal_states:
                assert new_policy[state].sum() > 0

    def test_policy_iteration(self, solver):
        """测试策略迭代"""
        result = solver.policy_iteration()

        assert result.converged == True
        assert result.total_iterations > 0
        assert result.algorithm == DPAlgorithmType.POLICY_ITERATION

        # 检查最终策略是否合理
        # 对于4x4网格，靠近终止状态的位置应该有明确的最优动作
        assert len(result.final_values) == solver.env.n_states
        assert result.final_policy.shape == (solver.env.n_states, solver.env.n_actions)

    def test_value_iteration(self, solver):
        """测试值迭代"""
        result = solver.value_iteration()

        assert result.converged == True
        assert result.total_iterations > 0
        assert result.algorithm == DPAlgorithmType.VALUE_ITERATION

        # 值函数应该与策略迭代结果相近
        assert len(result.final_values) == solver.env.n_states

    def test_policy_iteration_vs_value_iteration(self, env):
        """测试策略迭代和值迭代结果一致性"""
        solver1 = DPSolver(env, gamma=1.0, theta=1e-8)
        solver2 = DPSolver(env, gamma=1.0, theta=1e-8)

        result1 = solver1.policy_iteration()
        result2 = solver2.value_iteration()

        # 两种方法的最终值函数应该接近
        np.testing.assert_array_almost_equal(
            result1.final_values,
            result2.final_values,
            decimal=4
        )

    def test_get_greedy_action(self, solver):
        """测试贪婪动作获取"""
        solver.policy_iteration()

        # 检查靠近终止状态的位置
        # 状态1 (0,1) 应该向左移动到终止状态 (0,0)
        action = solver.get_greedy_action(1)
        assert action in [0, 1, 2, 3]  # 有效动作

    def test_get_action_values(self, solver):
        """测试动作值获取"""
        solver.policy_iteration()

        q_values = solver.get_action_values(5)
        assert len(q_values) == 4

    def test_policy_arrows(self, solver):
        """测试策略箭头表示"""
        solver.policy_iteration()

        arrows = solver.get_policy_arrows()
        assert len(arrows) == solver.env.n_states

        # 终止状态应该标记为 T
        assert arrows[0] == ["T"]
        assert arrows[15] == ["T"]

        # 非终止状态应该有方向箭头
        for state in range(1, 15):
            assert len(arrows[state]) > 0
            for arrow in arrows[state]:
                assert arrow in ["↑", "↓", "←", "→"]

    def test_render_functions(self, solver):
        """测试渲染函数"""
        solver.policy_iteration()

        value_text = solver.render_value_function()
        assert "T" in value_text
        assert isinstance(value_text, str)

        policy_text = solver.render_policy()
        assert isinstance(policy_text, str)

    def test_discount_factor_effect(self, env):
        """测试折扣因子对结果的影响"""
        solver1 = DPSolver(env, gamma=1.0, theta=1e-6)
        solver2 = DPSolver(env, gamma=0.9, theta=1e-6)

        result1 = solver1.value_iteration()
        result2 = solver2.value_iteration()

        # gamma=0.9 的值函数绝对值应该更小
        assert np.abs(result2.final_values).mean() < np.abs(result1.final_values).mean()

    def test_to_dict(self, solver):
        """测试导出为字典"""
        solver.policy_iteration()

        data = solver.to_dict()
        assert "gamma" in data
        assert "theta" in data
        assert "value_function" in data
        assert "policy" in data
        assert "policy_arrows" in data

    def test_factory_function(self, env):
        """测试工厂函数"""
        solver = create_dp_solver(env, gamma=0.95, theta=1e-4)

        assert solver.gamma == 0.95
        assert solver.theta == 1e-4


class TestDPConvergence:
    """DP收敛性测试"""

    def test_convergence_different_sizes(self):
        """测试不同网格大小的收敛性"""
        for size in [3, 4, 5, 6]:
            config = EnvironmentConfig(grid_size=size)
            env = BasicGridEnv(config)
            solver = DPSolver(env, gamma=1.0, theta=1e-6)

            result = solver.policy_iteration()
            assert result.converged == True

    def test_iteration_records(self):
        """测试迭代记录"""
        env = BasicGridEnv()
        solver = DPSolver(env, gamma=1.0, theta=1e-6)

        result = solver.policy_iteration()

        # 应该有迭代记录
        assert len(solver.history) > 0

        # 检查记录格式
        record = solver.history[0]
        assert hasattr(record, "iteration")
        assert hasattr(record, "state")
        assert hasattr(record, "old_value")
        assert hasattr(record, "new_value")
        assert hasattr(record, "delta")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

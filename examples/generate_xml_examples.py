"""
生成典型XML日志示例

为三种实验类型生成示例XML文件：
1. Basic Gridworld - 策略迭代
2. Windy Gridworld - SARSA
3. Cliff Walking - Q-Learning
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import numpy as np
from datetime import datetime

from app.services.environment.basic_grid import BasicGridEnv, EnvironmentConfig
from app.services.environment.windy_grid import create_windy_grid_env
from app.services.environment.cliff_walking import create_cliff_walking_env
from app.services.algorithm.dp_solver import DPSolver
from app.services.algorithm.td_solver import TDSolver
from app.services.export.xml_exporter import XMLExporter, ExperimentMetadata


def generate_basic_gridworld_example():
    """生成Basic Gridworld示例（策略迭代）"""
    print("=" * 50)
    print("生成 Basic Gridworld 示例 (策略迭代)")
    print("=" * 50)

    # 创建4x4网格环境
    config = EnvironmentConfig(
        grid_size=4,
        step_reward=-1.0,
        terminal_reward=0.0,
        gamma=1.0
    )
    env = BasicGridEnv(config)

    # 创建DP求解器
    solver = DPSolver(env, gamma=1.0, theta=1e-6)

    # 运行策略迭代
    result = solver.policy_iteration()

    print(f"收敛: {result.converged}")
    print(f"策略改进轮数: {result.total_episodes}")
    print(f"总迭代次数: {result.total_iterations}")
    print(f"执行时间: {result.execution_time:.4f}s")

    # 导出XML
    exporter = XMLExporter(output_dir="examples/xml")
    metadata = ExperimentMetadata(
        experiment_id="example-basic-policy-iter",
        experiment_type="basic",
        algorithm="policy_iteration",
        grid_size=4,
        gamma=1.0,
        theta=1e-6,
        step_reward=-1.0
    )

    filepath = exporter.export_basic_gridworld(
        metadata=metadata,
        result=result,
        iterations=solver.history[:50],  # 保留前50条迭代记录
        episodes=result.episode_history
    )

    print(f"导出文件: {filepath}")
    print()

    # 打印值函数
    print("最终值函数:")
    print(solver.render_value_function())

    return filepath


def generate_windy_gridworld_example():
    """生成Windy Gridworld示例（SARSA）"""
    print("=" * 50)
    print("生成 Windy Gridworld 示例 (SARSA)")
    print("=" * 50)

    # 创建Windy环境
    env = create_windy_grid_env()

    # 创建TD求解器
    solver = TDSolver(env, alpha=0.5, gamma=1.0, epsilon=0.1)

    # 运行SARSA
    result = solver.sarsa(max_episodes=200)

    print(f"收敛: {result.converged}")
    print(f"总回合数: {result.total_episodes}")
    print(f"成功率: {result.success_rate:.2%}")
    print(f"平均奖励: {result.avg_reward:.2f}")
    print(f"执行时间: {result.execution_time:.4f}s")

    # 导出XML
    exporter = XMLExporter(output_dir="examples/xml")
    metadata = ExperimentMetadata(
        experiment_id="example-windy-sarsa",
        experiment_type="windy",
        algorithm="sarsa",
        grid_size=10,  # width
        gamma=1.0,
        theta=0.0,
        step_reward=-1.0
    )

    # 为TD算法创建简化的DPResult格式
    from app.services.algorithm.dp_solver import DPResult, DPAlgorithmType
    dp_result = DPResult(
        algorithm=DPAlgorithmType.VALUE_ITERATION,  # 近似
        converged=result.converged,
        total_iterations=result.total_steps,
        total_episodes=result.total_episodes,
        final_values=solver.get_value_function(),
        final_policy=result.final_policy,
        history=[],
        episode_history=[],
        execution_time=result.execution_time
    )

    filepath = exporter.export_basic_gridworld(
        metadata=metadata,
        result=dp_result,
        iterations=[]
    )

    print(f"导出文件: {filepath}")
    print()

    return filepath


def generate_cliff_walking_example():
    """生成Cliff Walking示例（Q-Learning）"""
    print("=" * 50)
    print("生成 Cliff Walking 示例 (Q-Learning)")
    print("=" * 50)

    # 创建Cliff Walking环境
    env = create_cliff_walking_env()

    # 创建TD求解器
    solver = TDSolver(env, alpha=0.5, gamma=1.0, epsilon=0.1)

    # 运行Q-Learning
    result = solver.q_learning(max_episodes=500)

    print(f"收敛: {result.converged}")
    print(f"总回合数: {result.total_episodes}")
    print(f"成功率: {result.success_rate:.2%}")
    print(f"平均奖励: {result.avg_reward:.2f}")
    print(f"执行时间: {result.execution_time:.4f}s")

    # 导出XML
    exporter = XMLExporter(output_dir="examples/xml")
    metadata = ExperimentMetadata(
        experiment_id="example-cliff-qlearning",
        experiment_type="cliff",
        algorithm="q_learning",
        grid_size=12,  # width
        gamma=1.0,
        theta=0.0,
        step_reward=-1.0
    )

    # 为TD算法创建简化的DPResult格式
    from app.services.algorithm.dp_solver import DPResult, DPAlgorithmType
    dp_result = DPResult(
        algorithm=DPAlgorithmType.VALUE_ITERATION,
        converged=result.converged,
        total_iterations=result.total_steps,
        total_episodes=result.total_episodes,
        final_values=solver.get_value_function(),
        final_policy=result.final_policy,
        history=[],
        episode_history=[],
        execution_time=result.execution_time
    )

    filepath = exporter.export_basic_gridworld(
        metadata=metadata,
        result=dp_result,
        iterations=[]
    )

    print(f"导出文件: {filepath}")
    print()

    return filepath


def main():
    """生成所有示例"""
    print("\n" + "=" * 60)
    print("  RL-GridWorld-3D XML日志示例生成器")
    print("=" * 60 + "\n")

    # 确保输出目录存在
    os.makedirs("examples/xml", exist_ok=True)

    # 生成三种示例
    files = []
    files.append(generate_basic_gridworld_example())
    files.append(generate_windy_gridworld_example())
    files.append(generate_cliff_walking_example())

    print("=" * 60)
    print("生成完成! 示例文件:")
    for f in files:
        print(f"  - {f}")
    print("=" * 60)


if __name__ == "__main__":
    main()

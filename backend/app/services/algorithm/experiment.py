"""
Experiment Framework - 算法对比实验框架

用于对比不同算法在相同环境下的表现，
支持SARSA与Q-Learning的对比实验。
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import time

from .td_solver import TDSolver, TDResult, TDAlgorithmType
from .dp_solver import DPSolver, DPResult


@dataclass
class ComparisonResult:
    """算法对比结果"""
    env_name: str
    env_config: Dict
    algorithms: List[str]
    results: Dict[str, Any]  # algorithm_name -> result
    comparison_metrics: Dict[str, Dict[str, float]]  # metric -> {algo: value}
    total_time: float
    winner: Dict[str, str]  # metric -> winning_algorithm


class ExperimentRunner:
    """
    实验运行器

    支持在相同环境下对比多种算法的表现。

    使用示例:
        runner = ExperimentRunner(env)
        result = runner.compare_td_algorithms(
            algorithms=['sarsa', 'q_learning'],
            max_episodes=500,
            num_runs=10
        )
    """

    def __init__(self, env: Any, env_name: str = "GridWorld"):
        """
        初始化实验运行器

        Args:
            env: 环境对象
            env_name: 环境名称
        """
        self.env = env
        self.env_name = env_name

    def compare_td_algorithms(
        self,
        algorithms: List[str] = ['sarsa', 'q_learning'],
        max_episodes: int = 500,
        num_runs: int = 10,
        alpha: float = 0.5,
        gamma: float = 1.0,
        epsilon: float = 0.1,
        verbose: bool = False
    ) -> ComparisonResult:
        """
        对比TD算法

        Args:
            algorithms: 要对比的算法列表
            max_episodes: 每次运行的最大回合数
            num_runs: 重复运行次数
            alpha: 学习率
            gamma: 折扣因子
            epsilon: 探索率
            verbose: 是否打印详细信息

        Returns:
            ComparisonResult: 对比结果
        """
        start_time = time.time()
        results = {}

        for algo in algorithms:
            if verbose:
                print(f"\n运行算法: {algo}")

            algo_results = []
            for run in range(num_runs):
                solver = TDSolver(
                    self.env,
                    alpha=alpha,
                    gamma=gamma,
                    epsilon=epsilon
                )

                if algo == 'sarsa':
                    result = solver.sarsa(
                        max_episodes=max_episodes,
                        verbose=False
                    )
                elif algo == 'q_learning':
                    result = solver.q_learning(
                        max_episodes=max_episodes,
                        verbose=False
                    )
                else:
                    raise ValueError(f"Unknown algorithm: {algo}")

                algo_results.append(result)

                if verbose:
                    print(f"  Run {run + 1}/{num_runs}: "
                          f"Avg Reward = {result.avg_reward:.2f}, "
                          f"Success Rate = {result.success_rate:.2%}")

            results[algo] = {
                'runs': algo_results,
                'avg_reward': np.mean([r.avg_reward for r in algo_results]),
                'std_reward': np.std([r.avg_reward for r in algo_results]),
                'avg_success_rate': np.mean([r.success_rate for r in algo_results]),
                'avg_episode_rewards': np.mean(
                    [r.episode_rewards for r in algo_results], axis=0
                ).tolist(),
                'avg_episode_lengths': np.mean(
                    [r.episode_lengths for r in algo_results], axis=0
                ).tolist()
            }

        # 计算对比指标
        comparison_metrics = {
            'avg_reward': {algo: results[algo]['avg_reward'] for algo in algorithms},
            'std_reward': {algo: results[algo]['std_reward'] for algo in algorithms},
            'success_rate': {algo: results[algo]['avg_success_rate'] for algo in algorithms}
        }

        # 确定每个指标的优胜者
        winner = {
            'avg_reward': max(algorithms, key=lambda a: results[a]['avg_reward']),
            'success_rate': max(algorithms, key=lambda a: results[a]['avg_success_rate']),
            'stability': min(algorithms, key=lambda a: results[a]['std_reward'])
        }

        total_time = time.time() - start_time

        return ComparisonResult(
            env_name=self.env_name,
            env_config=self.env.to_dict() if hasattr(self.env, 'to_dict') else {},
            algorithms=algorithms,
            results=results,
            comparison_metrics=comparison_metrics,
            total_time=total_time,
            winner=winner
        )

    def run_single_experiment(
        self,
        algorithm: str,
        max_episodes: int = 500,
        alpha: float = 0.5,
        gamma: float = 1.0,
        epsilon: float = 0.1,
        record_trajectory: bool = False
    ) -> TDResult:
        """
        运行单次实验

        Args:
            algorithm: 算法名称
            max_episodes: 最大回合数
            alpha: 学习率
            gamma: 折扣因子
            epsilon: 探索率
            record_trajectory: 是否记录轨迹

        Returns:
            TDResult: 实验结果
        """
        solver = TDSolver(
            self.env,
            alpha=alpha,
            gamma=gamma,
            epsilon=epsilon
        )

        if algorithm == 'sarsa':
            return solver.sarsa(
                max_episodes=max_episodes,
                record_trajectory=record_trajectory
            )
        elif algorithm == 'q_learning':
            return solver.q_learning(
                max_episodes=max_episodes,
                record_trajectory=record_trajectory
            )
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    def generate_learning_curves(
        self,
        algorithms: List[str] = ['sarsa', 'q_learning'],
        max_episodes: int = 500,
        num_runs: int = 10,
        window_size: int = 10,
        **kwargs
    ) -> Dict[str, Dict]:
        """
        生成学习曲线数据

        Args:
            algorithms: 算法列表
            max_episodes: 最大回合数
            num_runs: 运行次数
            window_size: 滑动窗口大小

        Returns:
            学习曲线数据
        """
        comparison = self.compare_td_algorithms(
            algorithms=algorithms,
            max_episodes=max_episodes,
            num_runs=num_runs,
            **kwargs
        )

        curves = {}
        for algo in algorithms:
            rewards = np.array(comparison.results[algo]['avg_episode_rewards'])

            # 计算滑动平均
            smoothed = np.convolve(
                rewards,
                np.ones(window_size) / window_size,
                mode='valid'
            )

            curves[algo] = {
                'raw': rewards.tolist(),
                'smoothed': smoothed.tolist(),
                'episodes': list(range(1, len(rewards) + 1)),
                'smoothed_episodes': list(range(window_size, len(rewards) + 1))
            }

        return curves


def run_cliff_walking_comparison(
    max_episodes: int = 500,
    num_runs: int = 10,
    verbose: bool = True
) -> ComparisonResult:
    """
    运行悬崖行走对比实验

    这是一个经典的对比实验，展示SARSA和Q-Learning的行为差异：
    - SARSA (on-policy) 会学习一条更安全但更长的路径
    - Q-Learning (off-policy) 会学习最短路径（沿着悬崖边缘）

    Args:
        max_episodes: 最大回合数
        num_runs: 运行次数
        verbose: 是否打印详细信息

    Returns:
        ComparisonResult: 对比结果
    """
    from ..environment.cliff_walking import create_cliff_walking_env

    env = create_cliff_walking_env()
    runner = ExperimentRunner(env, "CliffWalking")

    if verbose:
        print("=" * 60)
        print("悬崖行走实验 - SARSA vs Q-Learning 对比")
        print("=" * 60)
        print(f"环境: 4×12 网格，底部中间为悬崖")
        print(f"回合数: {max_episodes}, 运行次数: {num_runs}")
        print("=" * 60)

    result = runner.compare_td_algorithms(
        algorithms=['sarsa', 'q_learning'],
        max_episodes=max_episodes,
        num_runs=num_runs,
        alpha=0.5,
        gamma=1.0,
        epsilon=0.1,
        verbose=verbose
    )

    if verbose:
        print("\n" + "=" * 60)
        print("实验结果:")
        print("-" * 60)
        for algo in result.algorithms:
            print(f"\n{algo.upper()}:")
            print(f"  平均奖励: {result.comparison_metrics['avg_reward'][algo]:.2f} "
                  f"± {result.comparison_metrics['std_reward'][algo]:.2f}")
            print(f"  成功率: {result.comparison_metrics['success_rate'][algo]:.2%}")

        print("\n" + "-" * 60)
        print(f"最高奖励: {result.winner['avg_reward']}")
        print(f"最高成功率: {result.winner['success_rate']}")
        print(f"最稳定: {result.winner['stability']}")
        print(f"总耗时: {result.total_time:.2f}秒")
        print("=" * 60)

    return result


def run_windy_gridworld_comparison(
    max_episodes: int = 500,
    num_runs: int = 10,
    verbose: bool = True
) -> ComparisonResult:
    """
    运行有风网格世界对比实验

    Args:
        max_episodes: 最大回合数
        num_runs: 运行次数
        verbose: 是否打印详细信息

    Returns:
        ComparisonResult: 对比结果
    """
    from ..environment.windy_grid import create_windy_grid_env

    env = create_windy_grid_env()
    runner = ExperimentRunner(env, "WindyGridworld")

    if verbose:
        print("=" * 60)
        print("有风网格世界实验 - SARSA vs Q-Learning 对比")
        print("=" * 60)
        print(f"环境: 7×10 网格，部分列有向上的风力")
        print(f"回合数: {max_episodes}, 运行次数: {num_runs}")
        print("=" * 60)

    result = runner.compare_td_algorithms(
        algorithms=['sarsa', 'q_learning'],
        max_episodes=max_episodes,
        num_runs=num_runs,
        alpha=0.5,
        gamma=1.0,
        epsilon=0.1,
        verbose=verbose
    )

    if verbose:
        print("\n" + "=" * 60)
        print("实验结果:")
        print("-" * 60)
        for algo in result.algorithms:
            print(f"\n{algo.upper()}:")
            print(f"  平均奖励: {result.comparison_metrics['avg_reward'][algo]:.2f} "
                  f"± {result.comparison_metrics['std_reward'][algo]:.2f}")
            print(f"  成功率: {result.comparison_metrics['success_rate'][algo]:.2%}")

        print("\n" + "-" * 60)
        print(f"最高奖励: {result.winner['avg_reward']}")
        print(f"总耗时: {result.total_time:.2f}秒")
        print("=" * 60)

    return result

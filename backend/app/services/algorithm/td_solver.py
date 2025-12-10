"""
TD Solver - 时序差分算法求解器

实现 SARSA 和 Q-Learning 算法用于强化学习求解。
支持：
- SARSA (On-policy TD Control)
- Q-Learning (Off-policy TD Control)
- ε-greedy 探索策略
"""

import numpy as np
from enum import Enum
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
import time


class TDAlgorithmType(Enum):
    """TD算法类型"""
    SARSA = "sarsa"
    Q_LEARNING = "q_learning"
    EXPECTED_SARSA = "expected_sarsa"


@dataclass
class EpisodeRecord:
    """单个回合记录"""
    episode: int
    total_reward: float
    steps: int
    start_state: int
    end_state: int
    success: bool
    trajectory: List[Tuple[int, int, float]] = field(default_factory=list)  # (state, action, reward)


@dataclass
class TDResult:
    """TD算法结果"""
    algorithm: str
    converged: bool
    total_episodes: int
    total_steps: int
    execution_time: float
    final_q_values: np.ndarray
    final_policy: np.ndarray
    episode_rewards: List[float]
    episode_lengths: List[int]
    success_rate: float
    avg_reward: float


class TDSolver:
    """
    时序差分算法求解器

    实现SARSA和Q-Learning两种TD控制算法，
    用于求解强化学习问题中的最优策略。

    Attributes:
        env: 环境对象（需要实现reset, step, get_possible_actions方法）
        n_states: 状态数量
        n_actions: 动作数量
        alpha: 学习率
        gamma: 折扣因子
        epsilon: 探索率
        Q: Q值表 (n_states × n_actions)
    """

    def __init__(
        self,
        env: Any,
        alpha: float = 0.5,
        gamma: float = 1.0,
        epsilon: float = 0.1,
        epsilon_decay: float = 1.0,
        min_epsilon: float = 0.01
    ):
        """
        初始化TD求解器

        Args:
            env: 环境对象
            alpha: 学习率
            gamma: 折扣因子
            epsilon: 初始探索率
            epsilon_decay: 探索率衰减因子
            min_epsilon: 最小探索率
        """
        self.env = env
        self.n_states = env.n_states
        self.n_actions = env.n_actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon

        # 初始化Q值表
        self.Q = np.zeros((self.n_states, self.n_actions))

        # 训练记录
        self.episode_records: List[EpisodeRecord] = []

        # 回调函数
        self.episode_callback: Optional[Callable[[EpisodeRecord], None]] = None
        self.step_callback: Optional[Callable[[int, int, int, float, int], None]] = None

    def reset_q_values(self):
        """重置Q值表"""
        self.Q = np.zeros((self.n_states, self.n_actions))
        self.episode_records = []

    def epsilon_greedy_action(self, state: int, current_epsilon: float) -> int:
        """
        ε-greedy动作选择

        Args:
            state: 当前状态
            current_epsilon: 当前探索率

        Returns:
            选择的动作
        """
        if np.random.random() < current_epsilon:
            # 随机探索
            return np.random.randint(self.n_actions)
        else:
            # 贪婪选择
            return int(np.argmax(self.Q[state]))

    def greedy_action(self, state: int) -> int:
        """贪婪动作选择"""
        return int(np.argmax(self.Q[state]))

    def sarsa(
        self,
        max_episodes: int = 500,
        max_steps_per_episode: int = 1000,
        record_trajectory: bool = False,
        verbose: bool = False
    ) -> TDResult:
        """
        SARSA算法 (On-policy TD Control)

        更新公式: Q(S,A) ← Q(S,A) + α[R + γQ(S',A') - Q(S,A)]

        Args:
            max_episodes: 最大回合数
            max_steps_per_episode: 每回合最大步数
            record_trajectory: 是否记录轨迹
            verbose: 是否打印详细信息

        Returns:
            TDResult: 算法结果
        """
        start_time = time.time()
        self.reset_q_values()

        episode_rewards = []
        episode_lengths = []
        success_count = 0
        total_steps = 0
        current_epsilon = self.epsilon

        for episode in range(max_episodes):
            state = self.env.reset()
            action = self.epsilon_greedy_action(state, current_epsilon)

            episode_reward = 0.0
            steps = 0
            trajectory = []
            start_state = state

            for step in range(max_steps_per_episode):
                result = self.env.step(action)
                next_state = result.next_state
                reward = result.reward
                done = result.done

                episode_reward += reward
                steps += 1
                total_steps += 1

                if record_trajectory:
                    trajectory.append((state, action, reward))

                # 选择下一个动作 (SARSA特征: 使用实际执行的下一个动作)
                next_action = self.epsilon_greedy_action(next_state, current_epsilon)

                # SARSA更新
                td_target = reward + self.gamma * self.Q[next_state, next_action] * (1 - done)
                td_error = td_target - self.Q[state, action]
                self.Q[state, action] += self.alpha * td_error

                # 步骤回调
                if self.step_callback:
                    self.step_callback(state, action, next_state, reward, episode)

                if done:
                    break

                state = next_state
                action = next_action

            # 判断是否成功
            success = self.env._is_terminal(self.env.current_state)
            if success:
                success_count += 1

            episode_rewards.append(episode_reward)
            episode_lengths.append(steps)

            # 记录回合
            record = EpisodeRecord(
                episode=episode,
                total_reward=episode_reward,
                steps=steps,
                start_state=start_state,
                end_state=self.env.current_state,
                success=success,
                trajectory=trajectory if record_trajectory else []
            )
            self.episode_records.append(record)

            if self.episode_callback:
                self.episode_callback(record)

            # 衰减探索率
            current_epsilon = max(self.min_epsilon, current_epsilon * self.epsilon_decay)

            if verbose and (episode + 1) % 100 == 0:
                avg_reward = np.mean(episode_rewards[-100:])
                print(f"Episode {episode + 1}: Avg Reward (last 100) = {avg_reward:.2f}")

        execution_time = time.time() - start_time
        success_rate = success_count / max_episodes

        return TDResult(
            algorithm="sarsa",
            converged=True,
            total_episodes=max_episodes,
            total_steps=total_steps,
            execution_time=execution_time,
            final_q_values=self.Q.copy(),
            final_policy=self._extract_policy(),
            episode_rewards=episode_rewards,
            episode_lengths=episode_lengths,
            success_rate=success_rate,
            avg_reward=float(np.mean(episode_rewards))
        )

    def q_learning(
        self,
        max_episodes: int = 500,
        max_steps_per_episode: int = 1000,
        record_trajectory: bool = False,
        verbose: bool = False
    ) -> TDResult:
        """
        Q-Learning算法 (Off-policy TD Control)

        更新公式: Q(S,A) ← Q(S,A) + α[R + γ max_a Q(S',a) - Q(S,A)]

        Args:
            max_episodes: 最大回合数
            max_steps_per_episode: 每回合最大步数
            record_trajectory: 是否记录轨迹
            verbose: 是否打印详细信息

        Returns:
            TDResult: 算法结果
        """
        start_time = time.time()
        self.reset_q_values()

        episode_rewards = []
        episode_lengths = []
        success_count = 0
        total_steps = 0
        current_epsilon = self.epsilon

        for episode in range(max_episodes):
            state = self.env.reset()

            episode_reward = 0.0
            steps = 0
            trajectory = []
            start_state = state

            for step in range(max_steps_per_episode):
                # 选择动作
                action = self.epsilon_greedy_action(state, current_epsilon)

                result = self.env.step(action)
                next_state = result.next_state
                reward = result.reward
                done = result.done

                episode_reward += reward
                steps += 1
                total_steps += 1

                if record_trajectory:
                    trajectory.append((state, action, reward))

                # Q-Learning更新 (使用max Q值，而非实际动作)
                td_target = reward + self.gamma * np.max(self.Q[next_state]) * (1 - done)
                td_error = td_target - self.Q[state, action]
                self.Q[state, action] += self.alpha * td_error

                # 步骤回调
                if self.step_callback:
                    self.step_callback(state, action, next_state, reward, episode)

                if done:
                    break

                state = next_state

            # 判断是否成功
            success = self.env._is_terminal(self.env.current_state)
            if success:
                success_count += 1

            episode_rewards.append(episode_reward)
            episode_lengths.append(steps)

            # 记录回合
            record = EpisodeRecord(
                episode=episode,
                total_reward=episode_reward,
                steps=steps,
                start_state=start_state,
                end_state=self.env.current_state,
                success=success,
                trajectory=trajectory if record_trajectory else []
            )
            self.episode_records.append(record)

            if self.episode_callback:
                self.episode_callback(record)

            # 衰减探索率
            current_epsilon = max(self.min_epsilon, current_epsilon * self.epsilon_decay)

            if verbose and (episode + 1) % 100 == 0:
                avg_reward = np.mean(episode_rewards[-100:])
                print(f"Episode {episode + 1}: Avg Reward (last 100) = {avg_reward:.2f}")

        execution_time = time.time() - start_time
        success_rate = success_count / max_episodes

        return TDResult(
            algorithm="q_learning",
            converged=True,
            total_episodes=max_episodes,
            total_steps=total_steps,
            execution_time=execution_time,
            final_q_values=self.Q.copy(),
            final_policy=self._extract_policy(),
            episode_rewards=episode_rewards,
            episode_lengths=episode_lengths,
            success_rate=success_rate,
            avg_reward=float(np.mean(episode_rewards))
        )

    def _extract_policy(self) -> np.ndarray:
        """从Q值表提取贪婪策略"""
        policy = np.zeros((self.n_states, self.n_actions))
        for state in range(self.n_states):
            best_action = np.argmax(self.Q[state])
            policy[state, best_action] = 1.0
        return policy

    def get_policy_arrows(self) -> Dict[int, List[str]]:
        """获取策略箭头表示"""
        arrow_map = {0: "↑", 1: "↓", 2: "←", 3: "→"}
        policy_arrows = {}

        for state in range(self.n_states):
            q_values = self.Q[state]
            max_q = np.max(q_values)

            # 获取所有最优动作
            best_actions = np.where(np.isclose(q_values, max_q))[0]
            arrows = [arrow_map[a] for a in best_actions]
            policy_arrows[state] = arrows

        return policy_arrows

    def get_value_function(self) -> np.ndarray:
        """从Q值表计算状态值函数 V(s) = max_a Q(s,a)"""
        return np.max(self.Q, axis=1)

    def render_q_table(self, grid_size: Optional[Tuple[int, int]] = None) -> str:
        """渲染Q值表"""
        lines = []
        lines.append("Q-Table:")
        lines.append("-" * 60)

        for state in range(self.n_states):
            q_str = " ".join(f"{q:7.2f}" for q in self.Q[state])
            best_action = np.argmax(self.Q[state])
            arrow = ["↑", "↓", "←", "→"][best_action]
            lines.append(f"S{state:3d}: [{q_str}] -> {arrow}")

        return "\n".join(lines)

    def render_policy(self, height: int, width: int) -> str:
        """渲染策略为网格形式"""
        arrow_map = {0: "↑", 1: "↓", 2: "←", 3: "→"}
        lines = []

        for row in range(height):
            row_str = ""
            for col in range(width):
                state = row * width + col
                best_action = np.argmax(self.Q[state])
                row_str += f" {arrow_map[best_action]} "
            lines.append(row_str)

        return "\n".join(lines)


def create_td_solver(
    env: Any,
    alpha: float = 0.5,
    gamma: float = 1.0,
    epsilon: float = 0.1
) -> TDSolver:
    """
    创建TD求解器

    Args:
        env: 环境对象
        alpha: 学习率
        gamma: 折扣因子
        epsilon: 探索率

    Returns:
        TDSolver实例
    """
    return TDSolver(env, alpha=alpha, gamma=gamma, epsilon=epsilon)

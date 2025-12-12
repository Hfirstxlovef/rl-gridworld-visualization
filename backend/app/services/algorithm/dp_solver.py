"""
Dynamic Programming Solver - 动态规划求解器

实现策略评估（Policy Evaluation）和策略改进（Policy Improvement）
用于求解基础网格世界问题的最优策略和状态值函数。
"""

import numpy as np
from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time

from ..environment.basic_grid import BasicGridEnv, Action


class DPAlgorithmType(str, Enum):
    """DP算法类型"""
    POLICY_EVALUATION = "policy_evaluation"
    POLICY_ITERATION = "policy_iteration"
    VALUE_ITERATION = "value_iteration"


@dataclass
class IterationRecord:
    """单次迭代记录"""
    iteration: int
    state: int
    action: Optional[str]
    old_value: float
    new_value: float
    delta: float
    policy: Optional[List[float]] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class EpisodeRecord:
    """回合记录（用于策略迭代）"""
    episode: int
    policy_stable: bool
    max_delta: float
    value_function: List[float]
    policy: List[List[float]]
    iterations: List[IterationRecord]


@dataclass
class DPResult:
    """DP算法执行结果"""
    algorithm: str
    converged: bool
    total_iterations: int
    total_episodes: int
    final_values: np.ndarray
    final_policy: np.ndarray
    history: List[IterationRecord]
    episode_history: List[EpisodeRecord]
    execution_time: float


class DPSolver:
    """
    动态规划求解器

    实现以下算法：
    1. 策略评估（Policy Evaluation）：给定策略，计算状态值函数
    2. 策略迭代（Policy Iteration）：交替进行策略评估和策略改进
    3. 值迭代（Value Iteration）：直接迭代更新值函数并隐式改进策略

    Attributes:
        env: 网格世界环境
        gamma: 折扣因子
        theta: 收敛阈值
        max_iterations: 最大迭代次数
    """

    def __init__(
        self,
        env: BasicGridEnv,
        gamma: float = 1.0,
        theta: float = 1e-6,
        max_iterations: int = 1000,
        callback: Optional[Callable[[IterationRecord], None]] = None
    ):
        """
        初始化DP求解器

        Args:
            env: 网格世界环境
            gamma: 折扣因子
            theta: 收敛阈值（值函数变化小于此值视为收敛）
            max_iterations: 最大迭代次数
            callback: 每次迭代的回调函数（用于实时更新前端）
        """
        self.env = env
        self.gamma = gamma
        self.theta = theta
        self.max_iterations = max_iterations
        self.callback = callback

        # 初始化值函数和策略
        self.V = np.zeros(env.n_states)
        self.policy = self._init_random_policy()

        # 记录历史
        self.history: List[IterationRecord] = []
        self.episode_history: List[EpisodeRecord] = []

    def _init_random_policy(self) -> np.ndarray:
        """
        初始化等概率随机策略

        Returns:
            策略矩阵 [n_states, n_actions]，每个状态的动作概率分布
        """
        policy = np.ones((self.env.n_states, self.env.n_actions)) / self.env.n_actions
        # 终止状态不需要策略
        for ts in self.env.terminal_states:
            policy[ts] = 0
        return policy

    def _init_deterministic_policy(self) -> np.ndarray:
        """
        初始化确定性策略（所有状态选择第一个动作）

        Returns:
            策略矩阵
        """
        policy = np.zeros((self.env.n_states, self.env.n_actions))
        policy[:, 0] = 1.0
        for ts in self.env.terminal_states:
            policy[ts] = 0
        return policy

    def policy_evaluation(
        self,
        policy: Optional[np.ndarray] = None,
        in_place: bool = True
    ) -> Tuple[np.ndarray, List[IterationRecord]]:
        """
        策略评估 - 计算给定策略下的状态值函数

        实现Bellman期望方程的迭代求解：
        V(s) = Σ_a π(a|s) Σ_{s',r} p(s',r|s,a)[r + γV(s')]

        Args:
            policy: 待评估的策略，默认使用当前策略
            in_place: 是否原地更新（True为异步更新，False为同步更新）

        Returns:
            (收敛后的值函数, 迭代记录列表)
        """
        if policy is None:
            policy = self.policy

        V = self.V.copy()
        records = []
        iteration = 0

        while iteration < self.max_iterations:
            delta = 0
            V_new = V.copy() if not in_place else V

            for state in range(self.env.n_states):
                # 跳过终止状态
                if state in self.env.terminal_states:
                    continue

                old_value = V[state]
                new_value = 0

                # 计算状态值：Σ_a π(a|s) Σ_{s',r} p(s',r|s,a)[r + γV(s')]
                for action in Action:
                    action_prob = policy[state, action]
                    if action_prob == 0:
                        continue

                    for prob, next_state, reward, done in self.env.P[state][action]:
                        new_value += action_prob * prob * (reward + self.gamma * V[next_state])

                if in_place:
                    V[state] = new_value
                else:
                    V_new[state] = new_value

                state_delta = abs(new_value - old_value)
                delta = max(delta, state_delta)

                # 记录迭代信息
                record = IterationRecord(
                    iteration=iteration,
                    state=state,
                    action=None,
                    old_value=old_value,
                    new_value=new_value,
                    delta=state_delta
                )
                records.append(record)
                self.history.append(record)

                if self.callback:
                    self.callback(record)

            if not in_place:
                V = V_new

            iteration += 1

            # 检查收敛
            if delta < self.theta:
                break

        self.V = V
        return V, records

    def policy_improvement(self) -> Tuple[np.ndarray, bool]:
        """
        策略改进 - 基于当前值函数贪婪地改进策略

        对每个状态，选择使得动作值最大的动作：
        π'(s) = argmax_a Σ_{s',r} p(s',r|s,a)[r + γV(s')]

        Returns:
            (改进后的策略, 策略是否稳定)
        """
        policy_stable = True
        new_policy = np.zeros_like(self.policy)

        for state in range(self.env.n_states):
            if state in self.env.terminal_states:
                continue

            # 计算每个动作的价值
            action_values = np.zeros(self.env.n_actions)
            for action in Action:
                for prob, next_state, reward, done in self.env.P[state][action]:
                    action_values[action] += prob * (reward + self.gamma * self.V[next_state])

            # 找出最优动作（可能有多个）
            best_actions = np.where(action_values == action_values.max())[0]

            # 原策略选择的动作
            old_action = np.argmax(self.policy[state])

            # 更新策略为均匀分布在最优动作上
            new_policy[state, best_actions] = 1.0 / len(best_actions)

            # 检查策略是否改变
            if old_action not in best_actions:
                policy_stable = False

        self.policy = new_policy
        return new_policy, policy_stable

    def policy_iteration(self) -> DPResult:
        """
        策略迭代算法

        交替进行策略评估和策略改进，直到策略稳定。

        Returns:
            DPResult: 包含最终值函数、策略和迭代历史
        """
        start_time = time.time()
        episode = 0
        total_iterations = 0

        while episode < self.max_iterations:
            # 策略评估
            V, eval_records = self.policy_evaluation()
            total_iterations += len(eval_records)

            # 策略改进
            new_policy, policy_stable = self.policy_improvement()

            # 记录本轮结果
            max_delta = max(r.delta for r in eval_records) if eval_records else 0
            episode_record = EpisodeRecord(
                episode=episode,
                policy_stable=policy_stable,
                max_delta=max_delta,
                value_function=self.V.tolist(),
                policy=self.policy.tolist(),
                iterations=eval_records
            )
            self.episode_history.append(episode_record)

            episode += 1

            if policy_stable:
                break

        execution_time = time.time() - start_time

        return DPResult(
            algorithm=DPAlgorithmType.POLICY_ITERATION,
            converged=episode < self.max_iterations,
            total_iterations=total_iterations,
            total_episodes=episode,
            final_values=self.V.copy(),
            final_policy=self.policy.copy(),
            history=self.history,
            episode_history=self.episode_history,
            execution_time=execution_time
        )

    def value_iteration(self) -> DPResult:
        """
        值迭代算法

        直接迭代更新值函数，隐式改进策略：
        V(s) = max_a Σ_{s',r} p(s',r|s,a)[r + γV(s')]

        Returns:
            DPResult: 包含最终值函数、策略和迭代历史
        """
        start_time = time.time()
        iteration = 0

        # 保存初始快照（全零值函数）
        initial_policy = np.ones((self.env.n_states, self.env.n_actions)) / self.env.n_actions
        for ts in self.env.terminal_states:
            initial_policy[ts] = 0
        self.episode_history.append(EpisodeRecord(
            episode=0,
            policy_stable=False,
            max_delta=float('inf'),
            value_function=self.V.tolist(),
            policy=initial_policy.tolist(),
            iterations=[]
        ))

        while iteration < self.max_iterations:
            delta = 0

            for state in range(self.env.n_states):
                if state in self.env.terminal_states:
                    continue

                old_value = self.V[state]

                # 计算所有动作的价值并取最大
                action_values = np.zeros(self.env.n_actions)
                for action in Action:
                    for prob, next_state, reward, done in self.env.P[state][action]:
                        action_values[action] += prob * (reward + self.gamma * self.V[next_state])

                new_value = action_values.max()
                self.V[state] = new_value

                state_delta = abs(new_value - old_value)
                delta = max(delta, state_delta)

                # 找出最优动作
                best_action = np.argmax(action_values)

                # 记录迭代信息
                record = IterationRecord(
                    iteration=iteration,
                    state=state,
                    action=self.env.ACTION_NAMES[Action(best_action)],
                    old_value=old_value,
                    new_value=new_value,
                    delta=state_delta
                )
                self.history.append(record)

                if self.callback:
                    self.callback(record)

                # 每个状态更新后保存快照（细粒度动画）
                temp_policy = np.zeros((self.env.n_states, self.env.n_actions))
                for s in range(self.env.n_states):
                    if s not in self.env.terminal_states:
                        action_vals = np.zeros(self.env.n_actions)
                        for a in Action:
                            for prob, ns, r, _ in self.env.P[s][a]:
                                action_vals[a] += prob * (r + self.gamma * self.V[ns])
                        best_acts = np.where(action_vals == action_vals.max())[0]
                        temp_policy[s, best_acts] = 1.0 / len(best_acts)

                self.episode_history.append(EpisodeRecord(
                    episode=len(self.episode_history),
                    policy_stable=False,
                    max_delta=state_delta,
                    value_function=self.V.tolist(),
                    policy=temp_policy.tolist(),
                    iterations=[]
                ))

            iteration += 1

            if delta < self.theta:
                break

        # 从值函数提取确定性策略
        self._extract_policy_from_values()

        execution_time = time.time() - start_time

        return DPResult(
            algorithm=DPAlgorithmType.VALUE_ITERATION,
            converged=iteration < self.max_iterations,
            total_iterations=iteration,  # 迭代轮次数（与max_iterations语义一致）
            total_episodes=iteration,
            final_values=self.V.copy(),
            final_policy=self.policy.copy(),
            history=self.history,
            episode_history=self.episode_history,
            execution_time=execution_time
        )

    def _extract_policy_from_values(self):
        """从值函数提取贪婪策略"""
        self.policy = np.zeros((self.env.n_states, self.env.n_actions))

        for state in range(self.env.n_states):
            if state in self.env.terminal_states:
                continue

            action_values = np.zeros(self.env.n_actions)
            for action in Action:
                for prob, next_state, reward, done in self.env.P[state][action]:
                    action_values[action] += prob * (reward + self.gamma * self.V[next_state])

            best_actions = np.where(action_values == action_values.max())[0]
            self.policy[state, best_actions] = 1.0 / len(best_actions)

    def get_greedy_action(self, state: int) -> int:
        """
        获取给定状态的贪婪动作

        Args:
            state: 状态编号

        Returns:
            最优动作编号
        """
        return np.argmax(self.policy[state])

    def get_state_value(self, state: int) -> float:
        """获取状态值"""
        return self.V[state]

    def get_action_values(self, state: int) -> np.ndarray:
        """
        获取状态-动作值 Q(s,a)

        Args:
            state: 状态编号

        Returns:
            各动作的价值数组
        """
        q_values = np.zeros(self.env.n_actions)
        for action in Action:
            for prob, next_state, reward, done in self.env.P[state][action]:
                q_values[action] += prob * (reward + self.gamma * self.V[next_state])
        return q_values

    def get_policy_arrows(self) -> Dict[int, List[str]]:
        """
        获取策略的箭头表示（用于可视化）

        Returns:
            字典 {state: [最优动作名称列表]}
        """
        arrows = {}
        arrow_map = {
            Action.UP: "↑",
            Action.DOWN: "↓",
            Action.LEFT: "←",
            Action.RIGHT: "→"
        }

        for state in range(self.env.n_states):
            if state in self.env.terminal_states:
                arrows[state] = ["T"]
                continue

            best_actions = np.where(self.policy[state] > 0)[0]
            arrows[state] = [arrow_map[Action(a)] for a in best_actions]

        return arrows

    def render_value_function(self) -> str:
        """
        文本渲染值函数

        Returns:
            值函数的文本表示
        """
        lines = []
        for row in range(self.env.grid_size):
            row_str = ""
            for col in range(self.env.grid_size):
                state = row * self.env.grid_size + col
                if state in self.env.terminal_states:
                    row_str += "  T   "
                else:
                    row_str += f"{self.V[state]:6.2f}"
            lines.append(row_str)
        return "\n".join(lines)

    def render_policy(self) -> str:
        """
        文本渲染策略

        Returns:
            策略的文本表示
        """
        arrows = self.get_policy_arrows()
        lines = []
        for row in range(self.env.grid_size):
            row_str = ""
            for col in range(self.env.grid_size):
                state = row * self.env.grid_size + col
                row_str += " " + "".join(arrows[state]).ljust(4)
            lines.append(row_str)
        return "\n".join(lines)

    def to_dict(self) -> Dict:
        """
        导出求解器状态为字典

        Returns:
            包含值函数、策略等信息的字典
        """
        return {
            "gamma": self.gamma,
            "theta": self.theta,
            "value_function": self.V.tolist(),
            "policy": self.policy.tolist(),
            "policy_arrows": self.get_policy_arrows(),
            "iteration_count": len(self.history)
        }


def create_dp_solver(
    env: BasicGridEnv,
    gamma: float = 1.0,
    theta: float = 1e-6,
    callback: Optional[Callable] = None
) -> DPSolver:
    """
    创建DP求解器的工厂函数

    Args:
        env: 网格世界环境
        gamma: 折扣因子
        theta: 收敛阈值
        callback: 迭代回调函数

    Returns:
        DPSolver实例
    """
    return DPSolver(env, gamma=gamma, theta=theta, callback=callback)

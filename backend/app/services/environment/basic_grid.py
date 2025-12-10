"""
Basic Gridworld Environment - 基础网格世界环境

实现4×4（可扩展）网格世界，用于动态规划算法演示。
根据实验要求：
- 状态集合 S = {0, 1, ..., N²-1}，其中左上角和右下角为终止状态
- 动作空间 A = {up, down, left, right}
- 边缘动作保持原地，奖励为 -1
"""

import numpy as np
from enum import IntEnum
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass, field


class Action(IntEnum):
    """动作枚举"""
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


@dataclass
class StepResult:
    """单步执行结果"""
    next_state: int
    reward: float
    done: bool
    info: Dict = field(default_factory=dict)


@dataclass
class EnvironmentConfig:
    """环境配置"""
    grid_size: int = 4
    step_reward: float = -1.0
    terminal_reward: float = 0.0
    gamma: float = 1.0  # 折扣因子


class BasicGridEnv:
    """
    基础网格世界环境

    实现标准的N×N网格世界，左上角(0,0)和右下角(N-1,N-1)为终止状态。
    智能体在非终止状态执行动作获得-1奖励，到达终止状态获得0奖励并结束。

    Attributes:
        grid_size: 网格大小 (N×N)
        n_states: 状态总数 (N²)
        n_actions: 动作数量 (4)
        terminal_states: 终止状态列表
        current_state: 当前状态
    """

    # 动作对应的移动方向 (row_delta, col_delta)
    ACTION_DELTAS = {
        Action.UP: (-1, 0),
        Action.DOWN: (1, 0),
        Action.LEFT: (0, -1),
        Action.RIGHT: (0, 1)
    }

    ACTION_NAMES = {
        Action.UP: "up",
        Action.DOWN: "down",
        Action.LEFT: "left",
        Action.RIGHT: "right"
    }

    def __init__(self, config: Optional[EnvironmentConfig] = None):
        """
        初始化基础网格世界环境

        Args:
            config: 环境配置，包含网格大小、奖励设置等
        """
        self.config = config or EnvironmentConfig()
        self.grid_size = self.config.grid_size
        self.n_states = self.grid_size ** 2
        self.n_actions = 4

        # 终止状态：左上角和右下角
        self.terminal_states = [0, self.n_states - 1]

        # 奖励设置
        self.step_reward = self.config.step_reward
        self.terminal_reward = self.config.terminal_reward
        self.gamma = self.config.gamma

        # 当前状态
        self.current_state: Optional[int] = None

        # 构建转移概率矩阵 P[s][a] = [(prob, next_state, reward, done), ...]
        self._build_transition_matrix()

    def _state_to_position(self, state: int) -> Tuple[int, int]:
        """
        状态编号转换为网格坐标

        Args:
            state: 状态编号 (0 到 N²-1)

        Returns:
            (row, col) 网格坐标
        """
        row = state // self.grid_size
        col = state % self.grid_size
        return row, col

    def _position_to_state(self, row: int, col: int) -> int:
        """
        网格坐标转换为状态编号

        Args:
            row: 行索引
            col: 列索引

        Returns:
            状态编号
        """
        return row * self.grid_size + col

    def _is_terminal(self, state: int) -> bool:
        """判断是否为终止状态"""
        return state in self.terminal_states

    def _is_valid_position(self, row: int, col: int) -> bool:
        """判断坐标是否在网格内"""
        return 0 <= row < self.grid_size and 0 <= col < self.grid_size

    def _build_transition_matrix(self):
        """
        构建状态转移矩阵

        P[s][a] = [(probability, next_state, reward, done), ...]
        对于确定性环境，每个(s,a)只有一个可能的转移
        """
        self.P = {}

        for state in range(self.n_states):
            self.P[state] = {}

            # 终止状态没有后继转移
            if self._is_terminal(state):
                for action in Action:
                    self.P[state][action] = [(1.0, state, 0.0, True)]
                continue

            row, col = self._state_to_position(state)

            for action in Action:
                delta_row, delta_col = self.ACTION_DELTAS[action]
                new_row = row + delta_row
                new_col = col + delta_col

                # 检查边界，出界则保持原地
                if self._is_valid_position(new_row, new_col):
                    next_state = self._position_to_state(new_row, new_col)
                else:
                    next_state = state  # 保持原地

                # 判断是否到达终止状态
                done = self._is_terminal(next_state)
                reward = self.terminal_reward if done else self.step_reward

                self.P[state][action] = [(1.0, next_state, reward, done)]

    def reset(self, start_state: Optional[int] = None) -> int:
        """
        重置环境

        Args:
            start_state: 指定起始状态，默认随机选择非终止状态

        Returns:
            初始状态
        """
        if start_state is not None:
            self.current_state = start_state
        else:
            # 随机选择一个非终止状态作为起始状态
            non_terminal_states = [s for s in range(self.n_states)
                                   if s not in self.terminal_states]
            self.current_state = np.random.choice(non_terminal_states)

        return self.current_state

    def step(self, action: int) -> StepResult:
        """
        执行动作

        Args:
            action: 动作编号 (0-3)

        Returns:
            StepResult: 包含下一状态、奖励、是否结束等信息
        """
        if self.current_state is None:
            raise ValueError("Environment not initialized. Call reset() first.")

        action = Action(action)
        transitions = self.P[self.current_state][action]

        # 对于确定性环境，只有一个转移
        prob, next_state, reward, done = transitions[0]

        old_state = self.current_state
        self.current_state = next_state

        return StepResult(
            next_state=next_state,
            reward=reward,
            done=done,
            info={
                "old_state": old_state,
                "action": self.ACTION_NAMES[action],
                "old_position": self._state_to_position(old_state),
                "new_position": self._state_to_position(next_state)
            }
        )

    def get_possible_actions(self, state: Optional[int] = None) -> List[Action]:
        """
        获取指定状态的所有可能动作

        Args:
            state: 状态编号，默认为当前状态

        Returns:
            可能动作列表
        """
        if state is None:
            state = self.current_state

        if self._is_terminal(state):
            return []

        return list(Action)

    def get_transition_prob(self, state: int, action: int,
                           next_state: int) -> float:
        """
        获取状态转移概率 P(s'|s,a)

        Args:
            state: 当前状态
            action: 动作
            next_state: 下一状态

        Returns:
            转移概率
        """
        action = Action(action)
        for prob, ns, _, _ in self.P[state][action]:
            if ns == next_state:
                return prob
        return 0.0

    def get_reward(self, state: int, action: int, next_state: int) -> float:
        """
        获取奖励 R(s,a,s')

        Args:
            state: 当前状态
            action: 动作
            next_state: 下一状态

        Returns:
            奖励值
        """
        action = Action(action)
        for prob, ns, reward, _ in self.P[state][action]:
            if ns == next_state:
                return reward
        return 0.0

    def get_state_info(self, state: int) -> Dict:
        """
        获取状态信息

        Args:
            state: 状态编号

        Returns:
            包含位置、是否终止等信息的字典
        """
        row, col = self._state_to_position(state)
        return {
            "state": state,
            "position": (row, col),
            "is_terminal": self._is_terminal(state),
            "row": row,
            "col": col
        }

    def render_text(self) -> str:
        """
        文本形式渲染环境

        Returns:
            环境的文本表示
        """
        lines = []
        for row in range(self.grid_size):
            row_str = ""
            for col in range(self.grid_size):
                state = self._position_to_state(row, col)
                if state == self.current_state:
                    row_str += " A "  # Agent
                elif self._is_terminal(state):
                    row_str += " T "  # Terminal
                else:
                    row_str += f"{state:3d}"
            lines.append(row_str)
        return "\n".join(lines)

    def get_grid_representation(self) -> np.ndarray:
        """
        获取网格的矩阵表示

        Returns:
            N×N矩阵，值为状态编号，终止状态标记为-1
        """
        grid = np.zeros((self.grid_size, self.grid_size), dtype=int)
        for state in range(self.n_states):
            row, col = self._state_to_position(state)
            if self._is_terminal(state):
                grid[row, col] = -1
            else:
                grid[row, col] = state
        return grid

    def to_dict(self) -> Dict:
        """
        将环境配置和状态导出为字典

        Returns:
            环境信息字典
        """
        return {
            "grid_size": self.grid_size,
            "n_states": self.n_states,
            "n_actions": self.n_actions,
            "terminal_states": self.terminal_states,
            "current_state": self.current_state,
            "step_reward": self.step_reward,
            "terminal_reward": self.terminal_reward,
            "gamma": self.gamma
        }


def create_basic_grid_env(
    grid_size: int = 4,
    step_reward: float = -1.0,
    gamma: float = 1.0
) -> BasicGridEnv:
    """
    创建基础网格世界环境的工厂函数

    Args:
        grid_size: 网格大小
        step_reward: 每步奖励（默认-1）
        gamma: 折扣因子

    Returns:
        BasicGridEnv实例
    """
    config = EnvironmentConfig(
        grid_size=grid_size,
        step_reward=step_reward,
        gamma=gamma
    )
    return BasicGridEnv(config)

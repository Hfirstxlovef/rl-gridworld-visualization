"""
Windy Gridworld Environment - 有风网格世界环境

实现 Sutton & Barto 书中的有风网格世界 (Example 6.5)。
- 7×10 网格世界
- 某些列存在向上的风力
- 风力会在智能体移动后额外将其向上推
- 起点 (3,0)，终点 (3,7)
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
class WindyGridConfig:
    """有风网格环境配置"""
    height: int = 7          # 网格高度
    width: int = 10          # 网格宽度
    start_pos: Tuple[int, int] = (3, 0)   # 起点位置 (row, col)
    goal_pos: Tuple[int, int] = (3, 7)    # 终点位置
    step_reward: float = -1.0             # 每步奖励
    goal_reward: float = 0.0              # 到达终点奖励
    # 每列的风力强度 (0表示无风)
    wind_strength: Tuple[int, ...] = (0, 0, 0, 1, 1, 1, 2, 2, 1, 0)


class WindyGridEnv:
    """
    有风网格世界环境

    实现经典的Windy Gridworld，智能体从起点移动到终点，
    部分列存在向上的风力，会在每次移动后额外推动智能体。

    Attributes:
        height: 网格高度
        width: 网格宽度
        n_states: 状态总数
        n_actions: 动作数量
        wind: 每列的风力强度
        start_state: 起始状态
        goal_state: 目标状态
    """

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

    def __init__(self, config: Optional[WindyGridConfig] = None):
        """
        初始化有风网格世界环境

        Args:
            config: 环境配置
        """
        self.config = config or WindyGridConfig()
        self.height = self.config.height
        self.width = self.config.width
        self.n_states = self.height * self.width
        self.n_actions = 4

        # 风力配置
        self.wind = list(self.config.wind_strength)
        if len(self.wind) < self.width:
            self.wind.extend([0] * (self.width - len(self.wind)))

        # 起点和终点
        self.start_pos = self.config.start_pos
        self.goal_pos = self.config.goal_pos
        self.start_state = self._position_to_state(*self.start_pos)
        self.goal_state = self._position_to_state(*self.goal_pos)

        # 奖励设置
        self.step_reward = self.config.step_reward
        self.goal_reward = self.config.goal_reward

        # 当前状态
        self.current_state: Optional[int] = None

        # 构建转移矩阵
        self._build_transition_matrix()

    def _state_to_position(self, state: int) -> Tuple[int, int]:
        """状态编号转换为网格坐标"""
        row = state // self.width
        col = state % self.width
        return row, col

    def _position_to_state(self, row: int, col: int) -> int:
        """网格坐标转换为状态编号"""
        return row * self.width + col

    def _is_terminal(self, state: int) -> bool:
        """判断是否为终止状态"""
        return state == self.goal_state

    def _is_valid_position(self, row: int, col: int) -> bool:
        """判断坐标是否在网格内"""
        return 0 <= row < self.height and 0 <= col < self.width

    def _clip_position(self, row: int, col: int) -> Tuple[int, int]:
        """将坐标限制在网格范围内"""
        row = max(0, min(self.height - 1, row))
        col = max(0, min(self.width - 1, col))
        return row, col

    def _build_transition_matrix(self):
        """构建状态转移矩阵，考虑风力影响"""
        self.P = {}

        for state in range(self.n_states):
            self.P[state] = {}

            # 终止状态
            if self._is_terminal(state):
                for action in Action:
                    self.P[state][action] = [(1.0, state, 0.0, True)]
                continue

            row, col = self._state_to_position(state)

            for action in Action:
                delta_row, delta_col = self.ACTION_DELTAS[action]

                # 执行动作
                new_row = row + delta_row
                new_col = col + delta_col

                # 应用风力（向上推，减少行号）
                wind_effect = self.wind[col] if col < len(self.wind) else 0
                new_row -= wind_effect

                # 限制在边界内
                new_row, new_col = self._clip_position(new_row, new_col)
                next_state = self._position_to_state(new_row, new_col)

                # 判断是否到达终点
                done = self._is_terminal(next_state)
                reward = self.goal_reward if done else self.step_reward

                self.P[state][action] = [(1.0, next_state, reward, done)]

    def reset(self, start_state: Optional[int] = None) -> int:
        """重置环境"""
        if start_state is not None:
            self.current_state = start_state
        else:
            self.current_state = self.start_state
        return self.current_state

    def step(self, action: int) -> StepResult:
        """执行动作"""
        if self.current_state is None:
            raise ValueError("Environment not initialized. Call reset() first.")

        action = Action(action)
        transitions = self.P[self.current_state][action]
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
                "new_position": self._state_to_position(next_state),
                "wind": self.wind[self._state_to_position(old_state)[1]]
            }
        )

    def get_possible_actions(self, state: Optional[int] = None) -> List[Action]:
        """获取可能动作"""
        if state is None:
            state = self.current_state
        if self._is_terminal(state):
            return []
        return list(Action)

    def get_state_info(self, state: int) -> Dict:
        """获取状态信息"""
        row, col = self._state_to_position(state)
        return {
            "state": state,
            "position": (row, col),
            "row": row,
            "col": col,
            "is_terminal": self._is_terminal(state),
            "is_start": state == self.start_state,
            "is_goal": state == self.goal_state,
            "wind": self.wind[col] if col < len(self.wind) else 0
        }

    def render_text(self) -> str:
        """文本渲染"""
        lines = []
        # 风力指示行
        wind_row = " ".join(f"{w:2d}" for w in self.wind[:self.width])
        lines.append(f"Wind: {wind_row}")
        lines.append("-" * (self.width * 3))

        for row in range(self.height):
            row_str = ""
            for col in range(self.width):
                state = self._position_to_state(row, col)
                if state == self.current_state:
                    row_str += " A "
                elif state == self.goal_state:
                    row_str += " G "
                elif state == self.start_state:
                    row_str += " S "
                else:
                    row_str += " . "
            lines.append(row_str)
        return "\n".join(lines)

    def get_grid_representation(self) -> np.ndarray:
        """获取网格矩阵表示"""
        grid = np.zeros((self.height, self.width), dtype=int)
        for state in range(self.n_states):
            row, col = self._state_to_position(state)
            if state == self.goal_state:
                grid[row, col] = -1  # 终点
            elif state == self.start_state:
                grid[row, col] = -2  # 起点
            else:
                grid[row, col] = state
        return grid

    def get_wind_array(self) -> List[int]:
        """获取风力数组"""
        return self.wind[:self.width]

    def to_dict(self) -> Dict:
        """导出环境信息"""
        return {
            "type": "windy",
            "height": self.height,
            "width": self.width,
            "n_states": self.n_states,
            "n_actions": self.n_actions,
            "start_state": self.start_state,
            "goal_state": self.goal_state,
            "start_pos": self.start_pos,
            "goal_pos": self.goal_pos,
            "wind": self.wind[:self.width],
            "current_state": self.current_state,
            "step_reward": self.step_reward,
            "goal_reward": self.goal_reward
        }


def create_windy_grid_env(
    height: int = 7,
    width: int = 10,
    wind_strength: Optional[Tuple[int, ...]] = None
) -> WindyGridEnv:
    """
    创建有风网格世界环境

    Args:
        height: 网格高度
        width: 网格宽度
        wind_strength: 每列风力强度，默认使用标准配置

    Returns:
        WindyGridEnv实例
    """
    config = WindyGridConfig(
        height=height,
        width=width,
        wind_strength=wind_strength or (0, 0, 0, 1, 1, 1, 2, 2, 1, 0)
    )
    return WindyGridEnv(config)

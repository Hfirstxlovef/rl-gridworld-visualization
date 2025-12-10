"""
Cliff Walking Environment - 悬崖行走环境

实现 Sutton & Barto 书中的悬崖行走环境 (Example 6.6)。
- 4×12 网格世界
- 底部一行中间部分是悬崖
- 起点 (3,0)，终点 (3,11)
- 掉入悬崖奖励 -100 并回到起点
- 普通移动奖励 -1
"""

import numpy as np
from enum import IntEnum
from typing import Tuple, List, Dict, Optional, Set
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
class CliffWalkingConfig:
    """悬崖行走环境配置"""
    height: int = 4           # 网格高度
    width: int = 12           # 网格宽度
    start_pos: Tuple[int, int] = (3, 0)    # 起点位置 (左下角)
    goal_pos: Tuple[int, int] = (3, 11)    # 终点位置 (右下角)
    step_reward: float = -1.0              # 普通移动奖励
    cliff_reward: float = -100.0           # 掉入悬崖奖励
    goal_reward: float = 0.0               # 到达终点奖励


class CliffWalkingEnv:
    """
    悬崖行走环境

    经典的强化学习环境，用于对比SARSA和Q-Learning的行为差异。
    - 底部一行（除起点和终点外）是悬崖
    - 掉入悬崖会获得-100奖励并回到起点
    - 普通移动获得-1奖励
    - 到达终点结束

    Attributes:
        height: 网格高度
        width: 网格宽度
        n_states: 状态总数
        n_actions: 动作数量
        cliff_states: 悬崖状态集合
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

    def __init__(self, config: Optional[CliffWalkingConfig] = None):
        """
        初始化悬崖行走环境

        Args:
            config: 环境配置
        """
        self.config = config or CliffWalkingConfig()
        self.height = self.config.height
        self.width = self.config.width
        self.n_states = self.height * self.width
        self.n_actions = 4

        # 起点和终点
        self.start_pos = self.config.start_pos
        self.goal_pos = self.config.goal_pos
        self.start_state = self._position_to_state(*self.start_pos)
        self.goal_state = self._position_to_state(*self.goal_pos)

        # 悬崖位置：底部一行除了起点和终点
        self.cliff_states: Set[int] = set()
        cliff_row = self.height - 1  # 最底部一行
        for col in range(1, self.width - 1):  # 除了第一列和最后一列
            state = self._position_to_state(cliff_row, col)
            self.cliff_states.add(state)

        # 奖励设置
        self.step_reward = self.config.step_reward
        self.cliff_reward = self.config.cliff_reward
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

    def _is_cliff(self, state: int) -> bool:
        """判断是否为悬崖"""
        return state in self.cliff_states

    def _is_valid_position(self, row: int, col: int) -> bool:
        """判断坐标是否在网格内"""
        return 0 <= row < self.height and 0 <= col < self.width

    def _clip_position(self, row: int, col: int) -> Tuple[int, int]:
        """将坐标限制在网格范围内"""
        row = max(0, min(self.height - 1, row))
        col = max(0, min(self.width - 1, col))
        return row, col

    def _build_transition_matrix(self):
        """构建状态转移矩阵"""
        self.P = {}

        for state in range(self.n_states):
            self.P[state] = {}

            # 终止状态
            if self._is_terminal(state):
                for action in Action:
                    self.P[state][action] = [(1.0, state, 0.0, True)]
                continue

            # 悬崖状态（理论上不应该在这里，但为了完整性）
            if self._is_cliff(state):
                for action in Action:
                    self.P[state][action] = [(1.0, self.start_state, self.cliff_reward, False)]
                continue

            row, col = self._state_to_position(state)

            for action in Action:
                delta_row, delta_col = self.ACTION_DELTAS[action]
                new_row = row + delta_row
                new_col = col + delta_col

                # 限制在边界内
                new_row, new_col = self._clip_position(new_row, new_col)
                next_state = self._position_to_state(new_row, new_col)

                # 检查是否掉入悬崖
                if self._is_cliff(next_state):
                    # 掉入悬崖：回到起点，奖励-100
                    self.P[state][action] = [(1.0, self.start_state, self.cliff_reward, False)]
                elif self._is_terminal(next_state):
                    # 到达终点
                    self.P[state][action] = [(1.0, next_state, self.goal_reward, True)]
                else:
                    # 普通移动
                    self.P[state][action] = [(1.0, next_state, self.step_reward, False)]

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

        # 检查是否掉入悬崖
        old_row, old_col = self._state_to_position(old_state)
        new_row, new_col = self._state_to_position(next_state)

        return StepResult(
            next_state=next_state,
            reward=reward,
            done=done,
            info={
                "old_state": old_state,
                "action": self.ACTION_NAMES[action],
                "old_position": (old_row, old_col),
                "new_position": (new_row, new_col),
                "fell_off_cliff": reward == self.cliff_reward
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
            "is_cliff": self._is_cliff(state),
            "type": "cliff" if self._is_cliff(state) else (
                "goal" if self._is_terminal(state) else (
                    "start" if state == self.start_state else "normal"
                )
            )
        }

    def render_text(self) -> str:
        """文本渲染"""
        lines = []
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
                elif self._is_cliff(state):
                    row_str += " C "
                else:
                    row_str += " . "
            lines.append(row_str)
        return "\n".join(lines)

    def get_grid_representation(self) -> np.ndarray:
        """
        获取网格矩阵表示

        返回值含义:
        - 0: 普通状态
        - -1: 终点
        - -2: 起点
        - -3: 悬崖
        """
        grid = np.zeros((self.height, self.width), dtype=int)
        for state in range(self.n_states):
            row, col = self._state_to_position(state)
            if state == self.goal_state:
                grid[row, col] = -1
            elif state == self.start_state:
                grid[row, col] = -2
            elif self._is_cliff(state):
                grid[row, col] = -3
            else:
                grid[row, col] = state
        return grid

    def get_cliff_positions(self) -> List[Tuple[int, int]]:
        """获取所有悬崖位置"""
        return [self._state_to_position(s) for s in self.cliff_states]

    def to_dict(self) -> Dict:
        """导出环境信息"""
        return {
            "type": "cliff",
            "height": self.height,
            "width": self.width,
            "n_states": self.n_states,
            "n_actions": self.n_actions,
            "start_state": self.start_state,
            "goal_state": self.goal_state,
            "start_pos": self.start_pos,
            "goal_pos": self.goal_pos,
            "cliff_states": list(self.cliff_states),
            "current_state": self.current_state,
            "step_reward": self.step_reward,
            "cliff_reward": self.cliff_reward,
            "goal_reward": self.goal_reward
        }


def create_cliff_walking_env(
    height: int = 4,
    width: int = 12,
    cliff_reward: float = -100.0
) -> CliffWalkingEnv:
    """
    创建悬崖行走环境

    Args:
        height: 网格高度
        width: 网格宽度
        cliff_reward: 掉入悬崖的奖励

    Returns:
        CliffWalkingEnv实例
    """
    config = CliffWalkingConfig(
        height=height,
        width=width,
        cliff_reward=cliff_reward
    )
    return CliffWalkingEnv(config)

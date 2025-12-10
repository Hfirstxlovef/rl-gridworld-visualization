"""
Environment Schemas - 环境相关的请求/响应模式
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class EnvironmentType(str, Enum):
    """环境类型"""
    BASIC = "basic"
    WINDY = "windy"
    CLIFF = "cliff"


class AlgorithmType(str, Enum):
    """算法类型"""
    DP = "dp"
    POLICY_ITERATION = "policy_iteration"
    VALUE_ITERATION = "value_iteration"
    SARSA = "sarsa"
    Q_LEARNING = "q_learning"


# ==================== 请求模式 ====================

class EnvironmentCreateRequest(BaseModel):
    """创建环境请求"""
    type: EnvironmentType = Field(default=EnvironmentType.BASIC, description="环境类型")
    grid_size: int = Field(default=4, ge=3, le=20, description="网格大小")
    step_reward: float = Field(default=-1.0, description="每步奖励")
    terminal_reward: float = Field(default=0.0, description="终止奖励")
    gamma: float = Field(default=1.0, ge=0.0, le=1.0, description="折扣因子")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "basic",
                "grid_size": 4,
                "step_reward": -1.0,
                "terminal_reward": 0.0,
                "gamma": 1.0
            }
        }


class EnvironmentUpdateRequest(BaseModel):
    """更新环境请求"""
    grid_size: Optional[int] = Field(None, ge=3, le=20)
    step_reward: Optional[float] = None
    terminal_reward: Optional[float] = None
    gamma: Optional[float] = Field(None, ge=0.0, le=1.0)


class AlgorithmStartRequest(BaseModel):
    """启动算法请求"""
    env_id: str = Field(..., description="环境ID")
    algorithm: AlgorithmType = Field(..., description="算法类型")
    learning_rate: float = Field(default=0.1, ge=0.0, le=1.0, description="学习率 (α)")
    discount_factor: float = Field(default=1.0, ge=0.0, le=1.0, description="折扣因子 (γ)")
    epsilon: float = Field(default=0.1, ge=0.0, le=1.0, description="探索率 (ε)")
    theta: float = Field(default=1e-6, ge=0.0, description="收敛阈值")
    max_iterations: int = Field(default=1000, ge=1, le=100000, description="最大迭代次数")
    max_episodes: int = Field(default=500, ge=1, le=10000, description="最大回合数")

    class Config:
        json_schema_extra = {
            "example": {
                "env_id": "env_001",
                "algorithm": "policy_iteration",
                "learning_rate": 0.1,
                "discount_factor": 1.0,
                "epsilon": 0.1,
                "theta": 1e-6,
                "max_iterations": 1000
            }
        }


class AlgorithmControlRequest(BaseModel):
    """算法控制请求"""
    exp_id: str = Field(..., description="实验ID")
    action: str = Field(..., description="控制动作: pause/resume/stop/step")


# ==================== 响应模式 ====================

class StateInfo(BaseModel):
    """状态信息"""
    state: int
    position: List[int]
    is_terminal: bool
    value: Optional[float] = None
    q_values: Optional[List[float]] = None


class EnvironmentResponse(BaseModel):
    """环境响应"""
    env_id: str
    type: EnvironmentType
    grid_size: int
    n_states: int
    n_actions: int
    terminal_states: List[int]
    step_reward: float
    terminal_reward: float
    gamma: float
    grid: List[List[int]]
    states: List[StateInfo]


class IterationData(BaseModel):
    """迭代数据"""
    iteration: int
    state: int
    action: Optional[str] = None
    old_value: float
    new_value: float
    delta: float
    timestamp: float


class EpisodeData(BaseModel):
    """回合数据"""
    episode: int
    total_steps: int
    total_reward: float
    policy_stable: Optional[bool] = None
    max_delta: float
    value_function: List[float]
    policy: List[List[float]]


class AlgorithmStatusResponse(BaseModel):
    """算法状态响应"""
    exp_id: str
    env_id: str
    algorithm: AlgorithmType
    status: str  # created, running, paused, completed, failed
    progress: float  # 0.0 - 1.0
    current_iteration: int
    current_episode: int
    converged: bool
    execution_time: float


class AlgorithmResultResponse(BaseModel):
    """算法结果响应"""
    exp_id: str
    algorithm: AlgorithmType
    converged: bool
    total_iterations: int
    total_episodes: int
    execution_time: float
    final_values: List[float]
    final_policy: List[List[float]]
    policy_arrows: Dict[str, List[str]]


class ExperimentListResponse(BaseModel):
    """实验列表响应"""
    total: int
    page: int
    page_size: int
    experiments: List[Dict[str, Any]]


class ExperimentDetailResponse(BaseModel):
    """实验详情响应"""
    exp_id: str
    name: str
    type: EnvironmentType
    algorithm: AlgorithmType
    status: str
    config: Dict[str, Any]
    result: Optional[AlgorithmResultResponse] = None
    created_at: str
    updated_at: str


# ==================== WebSocket 消息模式 ====================

class WSIterationUpdate(BaseModel):
    """WebSocket 迭代更新消息"""
    type: str = "iteration_update"
    exp_id: str
    iteration: int
    state: int
    action: Optional[str]
    old_value: float
    new_value: float
    delta: float
    value_function: List[float]
    policy: Optional[List[List[float]]] = None


class WSEpisodeComplete(BaseModel):
    """WebSocket 回合完成消息"""
    type: str = "episode_complete"
    exp_id: str
    episode: int
    total_reward: float
    steps: int
    policy_stable: Optional[bool] = None
    max_delta: float


class WSExperimentComplete(BaseModel):
    """WebSocket 实验完成消息"""
    type: str = "experiment_complete"
    exp_id: str
    converged: bool
    total_iterations: int
    total_episodes: int
    final_values: List[float]
    final_policy: List[List[float]]
    execution_time: float


class WSError(BaseModel):
    """WebSocket 错误消息"""
    type: str = "error"
    code: int
    message: str


# ==================== 通用响应 ====================

class APIResponse(BaseModel):
    """通用API响应"""
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None
    timestamp: str


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int
    message: str
    error_type: str
    timestamp: str

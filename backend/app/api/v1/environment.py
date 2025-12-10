"""
Environment API - 环境管理接口

提供网格世界环境的创建、查询、更新和删除功能。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
import uuid

from ...services.environment.basic_grid import (
    BasicGridEnv,
    EnvironmentConfig,
    create_basic_grid_env
)
from ...services.environment.windy_grid import (
    WindyGridEnv,
    WindyGridConfig,
    create_windy_grid_env
)
from ...services.environment.cliff_walking import (
    CliffWalkingEnv,
    CliffWalkingConfig,
    create_cliff_walking_env
)
from typing import Union

router = APIRouter(prefix="/environment", tags=["Environment"])


class EnvironmentType(str, Enum):
    """环境类型枚举"""
    BASIC = "basic"
    WINDY = "windy"
    CLIFF = "cliff"


class CreateEnvironmentRequest(BaseModel):
    """创建环境请求"""
    type: EnvironmentType = Field(default=EnvironmentType.BASIC, description="环境类型")
    grid_size: int = Field(default=4, ge=3, le=20, description="网格尺寸")
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
    status: str
    created_at: str


class EnvironmentStateResponse(BaseModel):
    """环境状态响应"""
    env_id: str
    grid: List[List[int]]
    current_state: Optional[int]
    agent_position: Optional[List[int]]
    terminal_states: List[int]
    terminal_positions: List[List[int]]
    step_reward: float
    terminal_reward: float


class StateInfoResponse(BaseModel):
    """状态信息响应"""
    state: int
    position: List[int]
    is_terminal: bool
    row: int
    col: int


# 内存存储（后续可改为数据库）
environments: Dict[str, Dict[str, Any]] = {}


def _get_env_instance(env_id: str) -> Union[BasicGridEnv, WindyGridEnv, CliffWalkingEnv]:
    """获取环境实例"""
    if env_id not in environments:
        raise HTTPException(status_code=404, detail=f"Environment {env_id} not found")
    return environments[env_id]["instance"]


def _get_env_grid_size(env) -> int:
    """获取环境网格尺寸（兼容不同环境类型）"""
    if hasattr(env, 'grid_size'):
        return env.grid_size
    elif hasattr(env, 'width'):
        return env.width
    else:
        return int(env.n_states ** 0.5)


def _get_env_terminal_states(env, env_type: EnvironmentType) -> List[int]:
    """获取终止状态列表（兼容不同环境类型）"""
    if env_type == EnvironmentType.BASIC:
        return env.terminal_states
    else:
        return [env.goal_state]


def _get_env_terminal_reward(env, env_type: EnvironmentType) -> float:
    """获取终止奖励（兼容不同环境类型）"""
    if env_type == EnvironmentType.BASIC:
        return env.terminal_reward
    else:
        return env.goal_reward


@router.post("", response_model=EnvironmentResponse)
async def create_environment(request: CreateEnvironmentRequest):
    """
    创建新的 Grid World 环境

    - **type**: 环境类型 (basic/windy/cliff)
    - **grid_size**: 网格尺寸 (3-20)
    - **step_reward**: 每步奖励
    - **terminal_reward**: 终止奖励
    - **gamma**: 折扣因子
    """
    env_id = f"env_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now().isoformat()

    # 创建环境实例
    if request.type == EnvironmentType.BASIC:
        config = EnvironmentConfig(
            grid_size=request.grid_size,
            step_reward=request.step_reward,
            terminal_reward=request.terminal_reward,
            gamma=request.gamma
        )
        env = BasicGridEnv(config)
        grid_size = env.grid_size
        terminal_states = env.terminal_states
        terminal_reward = env.terminal_reward

    elif request.type == EnvironmentType.WINDY:
        # Windy Gridworld: 7x10
        env = create_windy_grid_env()
        grid_size = env.width  # 使用宽度作为主要尺寸
        terminal_states = [env.goal_state]
        terminal_reward = env.goal_reward

    elif request.type == EnvironmentType.CLIFF:
        # Cliff Walking: 4x12
        env = create_cliff_walking_env()
        grid_size = env.width
        terminal_states = [env.goal_state]
        terminal_reward = env.goal_reward

    else:
        raise HTTPException(
            status_code=501,
            detail=f"Environment type '{request.type}' not supported"
        )

    # 存储环境
    environments[env_id] = {
        "instance": env,
        "type": request.type,
        "status": "created",
        "created_at": created_at,
        "config": {
            "grid_size": grid_size,
            "step_reward": request.step_reward,
            "terminal_reward": terminal_reward,
            "gamma": request.gamma
        }
    }

    return EnvironmentResponse(
        env_id=env_id,
        type=request.type,
        grid_size=grid_size,
        n_states=env.n_states,
        n_actions=env.n_actions,
        terminal_states=terminal_states,
        step_reward=env.step_reward,
        terminal_reward=terminal_reward,
        gamma=request.gamma,
        status="created",
        created_at=created_at
    )


@router.get("/{env_id}", response_model=EnvironmentResponse)
async def get_environment(env_id: str):
    """获取环境信息"""
    if env_id not in environments:
        raise HTTPException(status_code=404, detail=f"Environment {env_id} not found")

    env_data = environments[env_id]
    env = env_data["instance"]
    env_type = env_data["type"]

    return EnvironmentResponse(
        env_id=env_id,
        type=env_type,
        grid_size=_get_env_grid_size(env),
        n_states=env.n_states,
        n_actions=env.n_actions,
        terminal_states=_get_env_terminal_states(env, env_type),
        step_reward=env.step_reward,
        terminal_reward=_get_env_terminal_reward(env, env_type),
        gamma=env_data["config"]["gamma"],
        status=env_data["status"],
        created_at=env_data["created_at"]
    )


@router.get("/{env_id}/state", response_model=EnvironmentStateResponse)
async def get_environment_state(env_id: str):
    """获取环境当前状态"""
    env = _get_env_instance(env_id)
    env_data = environments[env_id]
    env_type = env_data["type"]

    # 生成网格表示
    grid = env.get_grid_representation().tolist()

    # 获取终止状态
    terminal_states = _get_env_terminal_states(env, env_type)

    # 获取终止状态的位置
    terminal_positions = [
        list(env._state_to_position(ts)) for ts in terminal_states
    ]

    # 获取当前位置
    agent_position = None
    if env.current_state is not None:
        agent_position = list(env._state_to_position(env.current_state))

    return EnvironmentStateResponse(
        env_id=env_id,
        grid=grid,
        current_state=env.current_state,
        agent_position=agent_position,
        terminal_states=terminal_states,
        terminal_positions=terminal_positions,
        step_reward=env.step_reward,
        terminal_reward=_get_env_terminal_reward(env, env_type)
    )


@router.get("/{env_id}/states", response_model=List[StateInfoResponse])
async def get_all_states(env_id: str):
    """获取所有状态信息"""
    env = _get_env_instance(env_id)

    states = []
    for state in range(env.n_states):
        info = env.get_state_info(state)
        states.append(StateInfoResponse(
            state=info["state"],
            position=list(info["position"]),
            is_terminal=info["is_terminal"],
            row=info["row"],
            col=info["col"]
        ))

    return states


@router.post("/{env_id}/reset")
async def reset_environment(env_id: str, start_state: Optional[int] = None):
    """重置环境到初始状态"""
    env = _get_env_instance(env_id)

    initial_state = env.reset(start_state)
    position = env._state_to_position(initial_state)

    environments[env_id]["status"] = "ready"

    return {
        "status": "reset",
        "env_id": env_id,
        "initial_state": initial_state,
        "position": list(position)
    }


@router.post("/{env_id}/step")
async def step_environment(env_id: str, action: int):
    """
    执行一步动作

    - **action**: 动作编号 (0=上, 1=下, 2=左, 3=右)
    """
    env = _get_env_instance(env_id)

    if env.current_state is None:
        raise HTTPException(
            status_code=400,
            detail="Environment not initialized. Call reset first."
        )

    result = env.step(action)

    return {
        "env_id": env_id,
        "next_state": result.next_state,
        "reward": result.reward,
        "done": result.done,
        "info": result.info
    }


@router.put("/{env_id}")
async def update_environment(env_id: str, request: CreateEnvironmentRequest):
    """更新环境配置（重新创建环境）"""
    if env_id not in environments:
        raise HTTPException(status_code=404, detail=f"Environment {env_id} not found")

    old_data = environments[env_id]

    # 创建新环境
    config = EnvironmentConfig(
        grid_size=request.grid_size,
        step_reward=request.step_reward,
        terminal_reward=request.terminal_reward,
        gamma=request.gamma
    )
    env = BasicGridEnv(config)

    # 更新存储
    environments[env_id] = {
        "instance": env,
        "type": request.type,
        "status": "updated",
        "created_at": old_data["created_at"],
        "config": {
            "grid_size": request.grid_size,
            "step_reward": request.step_reward,
            "terminal_reward": request.terminal_reward,
            "gamma": request.gamma
        }
    }

    return {"status": "updated", "env_id": env_id}


@router.delete("/{env_id}")
async def delete_environment(env_id: str):
    """删除环境"""
    if env_id not in environments:
        raise HTTPException(status_code=404, detail=f"Environment {env_id} not found")

    del environments[env_id]
    return {"status": "deleted", "env_id": env_id}


@router.get("", response_model=List[EnvironmentResponse])
async def list_environments():
    """列出所有环境"""
    result = []
    for env_id, env_data in environments.items():
        env = env_data["instance"]
        env_type = env_data["type"]
        result.append(EnvironmentResponse(
            env_id=env_id,
            type=env_type,
            grid_size=_get_env_grid_size(env),
            n_states=env.n_states,
            n_actions=env.n_actions,
            terminal_states=_get_env_terminal_states(env, env_type),
            step_reward=env.step_reward,
            terminal_reward=_get_env_terminal_reward(env, env_type),
            gamma=env_data["config"]["gamma"],
            status=env_data["status"],
            created_at=env_data["created_at"]
        ))
    return result

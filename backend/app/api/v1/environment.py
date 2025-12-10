"""
Environment API - 环境管理接口
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum

router = APIRouter(prefix="/environment", tags=["Environment"])


class EnvironmentType(str, Enum):
    """环境类型枚举"""
    BASIC = "basic"
    WINDY = "windy"
    CLIFF = "cliff"


class CreateEnvironmentRequest(BaseModel):
    """创建环境请求"""
    type: EnvironmentType = Field(..., description="环境类型")
    grid_size: int = Field(default=4, ge=3, le=20, description="网格尺寸")
    config: Optional[Dict[str, Any]] = Field(default=None, description="额外配置")


class EnvironmentResponse(BaseModel):
    """环境响应"""
    env_id: str
    type: EnvironmentType
    grid_size: int
    config: Dict[str, Any]
    status: str


class EnvironmentStateResponse(BaseModel):
    """环境状态响应"""
    env_id: str
    grid: List[List[int]]
    agent_position: tuple
    terminal_states: List[tuple]
    rewards: Dict[str, float]


# 内存中存储环境实例（后续可改为数据库）
environments: Dict[str, Dict] = {}
env_counter = 0


@router.post("", response_model=EnvironmentResponse)
async def create_environment(request: CreateEnvironmentRequest):
    """
    创建新的 Grid World 环境

    - **type**: 环境类型 (basic/windy/cliff)
    - **grid_size**: 网格尺寸 (3-20)
    - **config**: 额外配置参数
    """
    global env_counter
    env_counter += 1
    env_id = f"env_{env_counter}"

    # 默认配置
    default_config = {
        "step_reward": -1,
        "terminal_reward": 0,
        "gamma": 1.0,
    }

    if request.config:
        default_config.update(request.config)

    env_data = {
        "env_id": env_id,
        "type": request.type,
        "grid_size": request.grid_size,
        "config": default_config,
        "status": "created",
    }

    environments[env_id] = env_data

    return EnvironmentResponse(**env_data)


@router.get("/{env_id}", response_model=EnvironmentResponse)
async def get_environment(env_id: str):
    """获取环境信息"""
    if env_id not in environments:
        raise HTTPException(status_code=404, detail=f"Environment {env_id} not found")

    return EnvironmentResponse(**environments[env_id])


@router.get("/{env_id}/state", response_model=EnvironmentStateResponse)
async def get_environment_state(env_id: str):
    """获取环境当前状态"""
    if env_id not in environments:
        raise HTTPException(status_code=404, detail=f"Environment {env_id} not found")

    env = environments[env_id]
    grid_size = env["grid_size"]

    # 生成网格状态
    grid = [[i * grid_size + j for j in range(grid_size)] for i in range(grid_size)]

    return EnvironmentStateResponse(
        env_id=env_id,
        grid=grid,
        agent_position=(0, 0),
        terminal_states=[(0, 0), (grid_size - 1, grid_size - 1)],
        rewards=env["config"],
    )


@router.put("/{env_id}")
async def update_environment(env_id: str, config: Dict[str, Any]):
    """更新环境配置"""
    if env_id not in environments:
        raise HTTPException(status_code=404, detail=f"Environment {env_id} not found")

    environments[env_id]["config"].update(config)
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
    return [EnvironmentResponse(**env) for env in environments.values()]

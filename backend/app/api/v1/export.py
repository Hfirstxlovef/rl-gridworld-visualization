"""
Export API - 数据导出接口

提供实验数据的XML导出功能，符合实验报告要求的格式。
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os

from .algorithm import experiments
from .environment import environments
from ...services.export.xml_exporter import (
    XMLExporter,
    ExperimentMetadata,
    export_experiment
)
from ...services.algorithm.dp_solver import DPResult, IterationRecord, EpisodeRecord

router = APIRouter(prefix="/export", tags=["Export"])

# XML导出器实例
xml_exporter = XMLExporter()


class ExportResponse(BaseModel):
    """导出响应"""
    status: str
    filename: str
    filepath: str


class ExportListResponse(BaseModel):
    """导出文件列表响应"""
    files: List[str]
    count: int


@router.get("/xml/{exp_id}", response_model=ExportResponse)
async def export_xml(exp_id: str):
    """
    导出实验数据为 XML 格式

    按实验要求，XML 包含：
    - 实验元数据（ID、类型、算法、时间）
    - 配置参数（网格大小、折扣因子、收敛阈值）
    - 执行摘要（收敛状态、迭代次数、执行时间）
    - 迭代历史（状态、动作、值函数变化）
    - 最终结果（值函数、策略）
    """
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail=f"Experiment {exp_id} not found")

    exp_data = experiments[exp_id]
    env_id = exp_data["env_id"]

    if env_id not in environments:
        raise HTTPException(status_code=404, detail=f"Environment {env_id} not found")

    env_data = environments[env_id]
    env = env_data["instance"]
    result = exp_data.get("result")

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="Experiment not completed. Cannot export."
        )

    # 构建元数据
    config = exp_data.get("config", {})
    env_type = str(env_data.get("type", "basic"))

    # 获取网格大小
    if hasattr(env, 'grid_size'):
        grid_size = env.grid_size
    elif hasattr(env, 'width'):
        grid_size = env.width
    else:
        grid_size = int(env.n_states ** 0.5)

    metadata = ExperimentMetadata(
        experiment_id=exp_id,
        experiment_type=env_type.replace("EnvironmentType.", ""),
        algorithm=str(exp_data["algorithm"]).replace("AlgorithmType.", ""),
        grid_size=grid_size,
        gamma=config.get("gamma", 1.0),
        theta=config.get("theta", 1e-6),
        step_reward=env.step_reward
    )

    # 获取迭代历史
    solver = exp_data.get("solver")
    iterations = []
    episodes = []

    if solver and hasattr(solver, 'history'):
        iterations = solver.history

    if hasattr(result, 'episode_history'):
        episodes = result.episode_history

    # 导出XML
    filepath = xml_exporter.export_basic_gridworld(
        metadata=metadata,
        result=result,
        iterations=iterations,
        episodes=episodes
    )

    filename = os.path.basename(filepath)

    return ExportResponse(
        status="success",
        filename=filename,
        filepath=filepath
    )


@router.get("/list", response_model=ExportListResponse)
async def list_exports():
    """列出所有导出的XML文件"""
    files = xml_exporter.list_exports()
    return ExportListResponse(
        files=files,
        count=len(files)
    )


@router.get("/download/{filename}")
async def download_export(filename: str):
    """
    下载导出的XML文件

    - **filename**: 文件名（从 /list 接口获取）
    """
    filepath = os.path.join(xml_exporter.output_dir, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/xml"
    )


@router.delete("/file/{filename}")
async def delete_export(filename: str):
    """删除导出的XML文件"""
    success = xml_exporter.delete_export(filename)

    if not success:
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

    return {"status": "deleted", "filename": filename}

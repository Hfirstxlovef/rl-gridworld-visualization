"""
Algorithm API - 算法控制接口

提供强化学习算法的启动、控制和结果查询功能。
支持动态规划(DP)、策略迭代、值迭代等算法。
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
import uuid
import asyncio

from ...services.environment.basic_grid import BasicGridEnv, Action
from ...services.environment.windy_grid import WindyGridEnv
from ...services.environment.cliff_walking import CliffWalkingEnv
from ...services.algorithm.dp_solver import (
    DPSolver,
    DPResult,
    DPAlgorithmType,
    IterationRecord,
    create_dp_solver
)
from ...services.algorithm.td_solver import (
    TDSolver,
    TDResult,
    create_td_solver
)
from ...services.export.xml_exporter import (
    XMLExporter,
    ExperimentMetadata,
    export_experiment
)
from .environment import environments, _get_env_instance

router = APIRouter(prefix="/algorithm", tags=["Algorithm"])


class AlgorithmType(str, Enum):
    """算法类型"""
    POLICY_EVALUATION = "policy_evaluation"
    POLICY_ITERATION = "policy_iteration"
    VALUE_ITERATION = "value_iteration"
    SARSA = "sarsa"
    Q_LEARNING = "q_learning"


class AlgorithmStartRequest(BaseModel):
    """启动算法请求"""
    env_id: str = Field(..., description="环境ID")
    algorithm: AlgorithmType = Field(..., description="算法类型")
    gamma: float = Field(default=1.0, ge=0.0, le=1.0, description="折扣因子")
    theta: float = Field(default=1e-6, ge=0.0, description="收敛阈值")
    max_iterations: int = Field(default=1000, ge=1, le=100000, description="最大迭代次数")

    # TD算法参数（Sarsa/Q-Learning）
    learning_rate: float = Field(default=0.1, ge=0.0, le=1.0, description="学习率")
    epsilon: float = Field(default=0.1, ge=0.0, le=1.0, description="探索率")
    max_episodes: int = Field(default=500, ge=1, le=10000, description="最大回合数")

    class Config:
        json_schema_extra = {
            "example": {
                "env_id": "env_abc123",
                "algorithm": "policy_iteration",
                "gamma": 1.0,
                "theta": 1e-6,
                "max_iterations": 1000
            }
        }


class AlgorithmControlRequest(BaseModel):
    """算法控制请求"""
    action: str = Field(..., description="控制动作: pause/resume/stop/step")


class AlgorithmStatusResponse(BaseModel):
    """算法状态响应"""
    exp_id: str
    env_id: str
    algorithm: AlgorithmType
    status: str
    progress: float
    current_iteration: int
    converged: bool
    execution_time: float


class AlgorithmResultResponse(BaseModel):
    """算法结果响应"""
    exp_id: str
    algorithm: str
    converged: bool
    total_iterations: int
    total_episodes: int
    execution_time: float
    final_values: List[float]
    final_policy: List[List[float]]
    policy_arrows: Dict[str, List[str]]
    value_grid: List[List[float]]


class IterationDataResponse(BaseModel):
    """迭代数据响应"""
    iteration: int
    state: int
    action: Optional[str]
    old_value: float
    new_value: float
    delta: float


# 实验存储
experiments: Dict[str, Dict[str, Any]] = {}


@router.post("/start", response_model=AlgorithmStatusResponse)
async def start_algorithm(request: AlgorithmStartRequest, background_tasks: BackgroundTasks):
    """
    启动算法训练

    - **env_id**: 环境ID
    - **algorithm**: 算法类型
    - **gamma**: 折扣因子
    - **theta**: 收敛阈值
    - **max_iterations**: 最大迭代次数
    """
    # 验证环境存在
    env = _get_env_instance(request.env_id)
    env_data = environments[request.env_id]

    # 创建实验ID
    exp_id = f"exp_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now()

    # 根据算法类型创建求解器
    is_td_algorithm = request.algorithm in [AlgorithmType.SARSA, AlgorithmType.Q_LEARNING]

    if request.algorithm in [AlgorithmType.POLICY_EVALUATION,
                             AlgorithmType.POLICY_ITERATION,
                             AlgorithmType.VALUE_ITERATION]:
        solver = DPSolver(
            env=env,
            gamma=request.gamma,
            theta=request.theta,
            max_iterations=request.max_iterations
        )
    elif is_td_algorithm:
        solver = TDSolver(
            env=env,
            alpha=request.learning_rate,
            gamma=request.gamma,
            epsilon=request.epsilon
        )
    else:
        raise HTTPException(
            status_code=501,
            detail=f"Algorithm '{request.algorithm}' not supported"
        )

    # 存储实验信息
    config_data = {
        "gamma": request.gamma,
        "theta": request.theta,
        "max_iterations": request.max_iterations
    }
    if is_td_algorithm:
        config_data.update({
            "alpha": request.learning_rate,
            "epsilon": request.epsilon,
            "max_episodes": request.max_episodes
        })

    experiments[exp_id] = {
        "exp_id": exp_id,
        "env_id": request.env_id,
        "algorithm": request.algorithm,
        "solver": solver,
        "status": "running",
        "progress": 0.0,
        "current_iteration": 0,
        "converged": False,
        "execution_time": 0.0,
        "result": None,
        "created_at": created_at,
        "config": config_data
    }

    # 在后台执行算法
    background_tasks.add_task(run_algorithm, exp_id, request.algorithm)

    return AlgorithmStatusResponse(
        exp_id=exp_id,
        env_id=request.env_id,
        algorithm=request.algorithm,
        status="running",
        progress=0.0,
        current_iteration=0,
        converged=False,
        execution_time=0.0
    )


async def run_algorithm(exp_id: str, algorithm: AlgorithmType):
    """后台执行算法"""
    if exp_id not in experiments:
        return

    exp_data = experiments[exp_id]
    solver = exp_data["solver"]
    config = exp_data["config"]

    try:
        if algorithm == AlgorithmType.POLICY_EVALUATION:
            # 只进行策略评估
            solver.policy_evaluation()
            result = DPResult(
                algorithm=DPAlgorithmType.POLICY_EVALUATION,
                converged=True,
                total_iterations=len(solver.history),
                total_episodes=1,
                final_values=solver.V.copy(),
                final_policy=solver.policy.copy(),
                history=solver.history,
                episode_history=[],
                execution_time=0.0
            )
        elif algorithm == AlgorithmType.POLICY_ITERATION:
            result = solver.policy_iteration()
        elif algorithm == AlgorithmType.VALUE_ITERATION:
            result = solver.value_iteration()
        elif algorithm == AlgorithmType.SARSA:
            max_episodes = config.get("max_episodes", 500)
            result = solver.sarsa(max_episodes=max_episodes)
        elif algorithm == AlgorithmType.Q_LEARNING:
            max_episodes = config.get("max_episodes", 500)
            result = solver.q_learning(max_episodes=max_episodes)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        # 更新实验状态
        exp_data["status"] = "completed"
        exp_data["progress"] = 1.0
        exp_data["current_iteration"] = result.total_iterations
        exp_data["converged"] = result.converged
        exp_data["execution_time"] = result.execution_time
        exp_data["result"] = result

    except Exception as e:
        exp_data["status"] = "failed"
        exp_data["error"] = str(e)


@router.get("/status/{exp_id}", response_model=AlgorithmStatusResponse)
async def get_algorithm_status(exp_id: str):
    """获取算法执行状态"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail=f"Experiment {exp_id} not found")

    exp_data = experiments[exp_id]

    return AlgorithmStatusResponse(
        exp_id=exp_id,
        env_id=exp_data["env_id"],
        algorithm=exp_data["algorithm"],
        status=exp_data["status"],
        progress=exp_data["progress"],
        current_iteration=exp_data["current_iteration"],
        converged=exp_data["converged"],
        execution_time=exp_data["execution_time"]
    )


@router.get("/result/{exp_id}", response_model=AlgorithmResultResponse)
async def get_algorithm_result(exp_id: str):
    """获取算法执行结果"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail=f"Experiment {exp_id} not found")

    exp_data = experiments[exp_id]

    if exp_data["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Experiment not completed. Current status: {exp_data['status']}"
        )

    result: DPResult = exp_data["result"]
    solver: DPSolver = exp_data["solver"]
    env: BasicGridEnv = solver.env

    # 构建值函数网格
    value_grid = []
    for row in range(env.grid_size):
        row_values = []
        for col in range(env.grid_size):
            state = row * env.grid_size + col
            row_values.append(float(result.final_values[state]))
        value_grid.append(row_values)

    # 获取策略箭头
    policy_arrows = solver.get_policy_arrows()
    # 转换key为字符串
    policy_arrows_str = {str(k): v for k, v in policy_arrows.items()}

    return AlgorithmResultResponse(
        exp_id=exp_id,
        algorithm=str(result.algorithm),
        converged=result.converged,
        total_iterations=result.total_iterations,
        total_episodes=result.total_episodes,
        execution_time=result.execution_time,
        final_values=result.final_values.tolist(),
        final_policy=result.final_policy.tolist(),
        policy_arrows=policy_arrows_str,
        value_grid=value_grid
    )


@router.get("/iterations/{exp_id}", response_model=List[IterationDataResponse])
async def get_iterations(exp_id: str, limit: int = 100, offset: int = 0):
    """获取迭代历史数据"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail=f"Experiment {exp_id} not found")

    exp_data = experiments[exp_id]
    solver: DPSolver = exp_data["solver"]

    iterations = solver.history[offset:offset + limit]

    return [
        IterationDataResponse(
            iteration=record.iteration,
            state=record.state,
            action=record.action,
            old_value=record.old_value,
            new_value=record.new_value,
            delta=record.delta
        )
        for record in iterations
    ]


@router.post("/control/{exp_id}")
async def control_algorithm(exp_id: str, request: AlgorithmControlRequest):
    """
    控制算法执行

    - **action**: pause/resume/stop/step
    """
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail=f"Experiment {exp_id} not found")

    exp_data = experiments[exp_id]
    action = request.action.lower()

    if action == "stop":
        exp_data["status"] = "stopped"
        return {"status": "stopped", "exp_id": exp_id}
    elif action == "pause":
        exp_data["status"] = "paused"
        return {"status": "paused", "exp_id": exp_id}
    elif action == "resume":
        if exp_data["status"] == "paused":
            exp_data["status"] = "running"
        return {"status": exp_data["status"], "exp_id": exp_id}
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown action: {action}. Use: pause/resume/stop/step"
        )


@router.post("/run-sync")
async def run_algorithm_sync(request: AlgorithmStartRequest):
    """
    同步执行算法（等待完成后返回结果）

    适用于小规模实验，直接返回完整结果。
    支持DP算法(policy_evaluation, policy_iteration, value_iteration)
    和TD算法(sarsa, q_learning)。
    """
    # 验证环境存在
    env = _get_env_instance(request.env_id)
    env_data = environments[request.env_id]

    exp_id = f"exp_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now()

    # 根据算法类型选择求解器
    is_td_algorithm = request.algorithm in [AlgorithmType.SARSA, AlgorithmType.Q_LEARNING]

    if is_td_algorithm:
        # TD算法
        solver = TDSolver(
            env=env,
            alpha=request.learning_rate,
            gamma=request.gamma,
            epsilon=request.epsilon
        )

        if request.algorithm == AlgorithmType.SARSA:
            td_result = solver.sarsa(max_episodes=request.max_episodes)
        else:  # Q_LEARNING
            td_result = solver.q_learning(max_episodes=request.max_episodes)

        # 获取网格尺寸
        if hasattr(env, 'grid_size'):
            height = width = env.grid_size
        elif hasattr(env, 'height') and hasattr(env, 'width'):
            height, width = env.height, env.width
        else:
            height = width = int(env.n_states ** 0.5)

        # 构建值函数网格
        value_grid = []
        V = solver.get_value_function()
        for row in range(height):
            row_values = []
            for col in range(width):
                state = row * width + col
                if state < len(V):
                    row_values.append(float(V[state]))
                else:
                    row_values.append(0.0)
            value_grid.append(row_values)

        policy_arrows = solver.get_policy_arrows()
        policy_arrows_str = {str(k): v for k, v in policy_arrows.items()}

        # 存储实验
        experiments[exp_id] = {
            "exp_id": exp_id,
            "env_id": request.env_id,
            "algorithm": request.algorithm,
            "solver": solver,
            "status": "completed",
            "progress": 1.0,
            "current_iteration": td_result.total_episodes,
            "converged": td_result.converged,
            "execution_time": td_result.execution_time,
            "result": td_result,
            "created_at": created_at,
            "config": {
                "gamma": request.gamma,
                "alpha": request.learning_rate,
                "epsilon": request.epsilon,
                "max_episodes": request.max_episodes
            }
        }

        return {
            "exp_id": exp_id,
            "algorithm": td_result.algorithm,
            "converged": td_result.converged,
            "total_iterations": td_result.total_steps,
            "total_episodes": td_result.total_episodes,
            "execution_time": td_result.execution_time,
            "final_values": V.tolist(),
            "final_policy": td_result.final_policy.tolist(),
            "policy_arrows": policy_arrows_str,
            "value_grid": value_grid,
            "episode_rewards": td_result.episode_rewards,
            "episode_lengths": td_result.episode_lengths,
            "success_rate": td_result.success_rate,
            "avg_reward": td_result.avg_reward
        }

    else:
        # DP算法
        solver = DPSolver(
            env=env,
            gamma=request.gamma,
            theta=request.theta,
            max_iterations=request.max_iterations
        )

        # 执行算法
        if request.algorithm == AlgorithmType.POLICY_EVALUATION:
            solver.policy_evaluation()
            result = DPResult(
                algorithm=DPAlgorithmType.POLICY_EVALUATION,
                converged=True,
                total_iterations=len(solver.history),
                total_episodes=1,
                final_values=solver.V.copy(),
                final_policy=solver.policy.copy(),
                history=solver.history,
                episode_history=[],
                execution_time=0.0
            )
        elif request.algorithm == AlgorithmType.POLICY_ITERATION:
            result = solver.policy_iteration()
        elif request.algorithm == AlgorithmType.VALUE_ITERATION:
            result = solver.value_iteration()
        else:
            raise HTTPException(
                status_code=501,
                detail=f"Algorithm '{request.algorithm}' not supported"
            )

        # 存储实验
        experiments[exp_id] = {
            "exp_id": exp_id,
            "env_id": request.env_id,
            "algorithm": request.algorithm,
            "solver": solver,
            "status": "completed",
            "progress": 1.0,
            "current_iteration": result.total_iterations,
            "converged": result.converged,
            "execution_time": result.execution_time,
            "result": result,
            "created_at": created_at,
            "config": {
                "gamma": request.gamma,
                "theta": request.theta,
                "max_iterations": request.max_iterations
            }
        }

        # 构建值函数网格
        value_grid = []
        for row in range(env.grid_size):
            row_values = []
            for col in range(env.grid_size):
                state = row * env.grid_size + col
                row_values.append(float(result.final_values[state]))
            value_grid.append(row_values)

        policy_arrows = solver.get_policy_arrows()
        policy_arrows_str = {str(k): v for k, v in policy_arrows.items()}

        # 构建迭代快照（用于动画回放）
        iteration_snapshots = []
        for ep in result.episode_history:
            # 为每个快照生成策略箭头
            snapshot_arrows = {}
            for state in range(env.n_states):
                if state not in env.terminal_states:
                    policy_row = ep.policy[state]
                    best_actions = [i for i, p in enumerate(policy_row) if p > 0]
                    arrows = [env.ACTION_NAMES[Action(a)] for a in best_actions]
                    snapshot_arrows[str(state)] = arrows

            iteration_snapshots.append({
                "iteration": ep.episode,
                "values": ep.value_function,
                "policy_arrows": snapshot_arrows,
                "max_delta": ep.max_delta
            })

        return {
            "exp_id": exp_id,
            "algorithm": str(result.algorithm),
            "converged": result.converged,
            "total_iterations": result.total_iterations,
            "total_episodes": result.total_episodes,
            "execution_time": result.execution_time,
            "final_values": result.final_values.tolist(),
            "final_policy": result.final_policy.tolist(),
            "policy_arrows": policy_arrows_str,
            "value_grid": value_grid,
            "value_text": solver.render_value_function(),
            "policy_text": solver.render_policy(),
            "iteration_snapshots": iteration_snapshots
        }


@router.get("", response_model=List[AlgorithmStatusResponse])
async def list_experiments():
    """列出所有实验"""
    return [
        AlgorithmStatusResponse(
            exp_id=exp_data["exp_id"],
            env_id=exp_data["env_id"],
            algorithm=exp_data["algorithm"],
            status=exp_data["status"],
            progress=exp_data["progress"],
            current_iteration=exp_data["current_iteration"],
            converged=exp_data["converged"],
            execution_time=exp_data["execution_time"]
        )
        for exp_data in experiments.values()
    ]


@router.delete("/{exp_id}")
async def delete_experiment(exp_id: str):
    """删除实验"""
    if exp_id not in experiments:
        raise HTTPException(status_code=404, detail=f"Experiment {exp_id} not found")

    del experiments[exp_id]
    return {"status": "deleted", "exp_id": exp_id}

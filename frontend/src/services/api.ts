/**
 * API 服务 - 与后端通信的HTTP接口
 */

import axios, { AxiosInstance } from 'axios';
import {
  EnvironmentConfig,
  AlgorithmConfig
} from '../types';

// API 基础配置
const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:16210';

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ==================== 环境 API ====================

export interface CreateEnvironmentRequest {
  type: string;
  grid_size: number;
  step_reward: number;
  terminal_reward: number;
  gamma: number;
}

export interface EnvironmentResponse {
  env_id: string;
  type: string;
  grid_size: number;
  n_states: number;
  n_actions: number;
  terminal_states: number[];
  step_reward: number;
  terminal_reward: number;
  gamma: number;
  status: string;
  created_at: string;
}

export interface EnvironmentStateResponse {
  env_id: string;
  grid: number[][];
  current_state: number | null;
  agent_position: number[] | null;
  terminal_states: number[];
  terminal_positions: number[][];
  step_reward: number;
  terminal_reward: number;
}

// 创建环境
export async function createEnvironment(
  config: EnvironmentConfig
): Promise<EnvironmentResponse> {
  const request: CreateEnvironmentRequest = {
    type: config.type,
    grid_size: config.gridSize,
    step_reward: config.stepReward,
    terminal_reward: config.terminalReward,
    gamma: config.gamma
  };

  const response = await apiClient.post<EnvironmentResponse>('/environment', request);
  return response.data;
}

// 获取环境信息
export async function getEnvironment(envId: string): Promise<EnvironmentResponse> {
  const response = await apiClient.get<EnvironmentResponse>(`/environment/${envId}`);
  return response.data;
}

// 获取环境状态
export async function getEnvironmentState(envId: string): Promise<EnvironmentStateResponse> {
  const response = await apiClient.get<EnvironmentStateResponse>(`/environment/${envId}/state`);
  return response.data;
}

// 重置环境
export async function resetEnvironment(
  envId: string,
  startState?: number
): Promise<{ status: string; env_id: string; initial_state: number; position: number[] }> {
  const params = startState !== undefined ? { start_state: startState } : {};
  const response = await apiClient.post(`/environment/${envId}/reset`, null, { params });
  return response.data;
}

// 执行动作
export async function stepEnvironment(
  envId: string,
  action: number
): Promise<{
  env_id: string;
  next_state: number;
  reward: number;
  done: boolean;
  info: Record<string, any>;
}> {
  const response = await apiClient.post(`/environment/${envId}/step`, null, {
    params: { action }
  });
  return response.data;
}

// 删除环境
export async function deleteEnvironment(envId: string): Promise<{ status: string }> {
  const response = await apiClient.delete(`/environment/${envId}`);
  return response.data;
}

// 获取所有环境
export async function listEnvironments(): Promise<EnvironmentResponse[]> {
  const response = await apiClient.get<EnvironmentResponse[]>('/environment');
  return response.data;
}

// ==================== 算法 API ====================

export interface AlgorithmStartRequest {
  env_id: string;
  algorithm: string;
  gamma: number;
  theta: number;
  max_iterations: number;
  learning_rate?: number;
  epsilon?: number;
  max_episodes?: number;
}

export interface AlgorithmStatusResponse {
  exp_id: string;
  env_id: string;
  algorithm: string;
  status: string;
  progress: number;
  current_iteration: number;
  converged: boolean;
  execution_time: number;
}

// 迭代快照（用于动画回放）
export interface IterationSnapshotResponse {
  iteration: number;
  values: number[];
  policy_arrows: Record<string, string[]>;
  max_delta: number;
}

export interface AlgorithmResultResponse {
  exp_id: string;
  algorithm: string;
  converged: boolean;
  total_iterations: number;
  total_episodes: number;
  execution_time: number;
  final_values: number[];
  final_policy: number[][];
  policy_arrows: Record<string, string[]>;
  value_grid: number[][];
  value_text?: string;
  policy_text?: string;
  // TD算法特有字段
  episode_rewards?: number[];
  episode_lengths?: number[];
  success_rate?: number;
  avg_reward?: number;
  // 迭代快照（用于动画回放）
  iteration_snapshots?: IterationSnapshotResponse[];
}

export interface IterationDataResponse {
  iteration: number;
  state: number;
  action: string | null;
  old_value: number;
  new_value: number;
  delta: number;
}

// 启动算法（异步）
export async function startAlgorithm(
  envId: string,
  config: AlgorithmConfig
): Promise<AlgorithmStatusResponse> {
  const request: AlgorithmStartRequest = {
    env_id: envId,
    algorithm: config.algorithm,
    gamma: config.gamma,
    theta: config.theta,
    max_iterations: config.maxIterations,
    learning_rate: config.learningRate,
    epsilon: config.epsilon,
    max_episodes: config.maxEpisodes
  };

  const response = await apiClient.post<AlgorithmStatusResponse>('/algorithm/start', request);
  return response.data;
}

// 同步执行算法（等待完成）
export async function runAlgorithmSync(
  envId: string,
  config: AlgorithmConfig
): Promise<AlgorithmResultResponse> {
  const request: AlgorithmStartRequest = {
    env_id: envId,
    algorithm: config.algorithm,
    gamma: config.gamma,
    theta: config.theta,
    max_iterations: config.maxIterations,
    learning_rate: config.learningRate,
    epsilon: config.epsilon,
    max_episodes: config.maxEpisodes
  };

  const response = await apiClient.post<AlgorithmResultResponse>('/algorithm/run-sync', request);
  return response.data;
}

// 获取算法状态
export async function getAlgorithmStatus(expId: string): Promise<AlgorithmStatusResponse> {
  const response = await apiClient.get<AlgorithmStatusResponse>(`/algorithm/status/${expId}`);
  return response.data;
}

// 获取算法结果
export async function getAlgorithmResult(expId: string): Promise<AlgorithmResultResponse> {
  const response = await apiClient.get<AlgorithmResultResponse>(`/algorithm/result/${expId}`);
  return response.data;
}

// 获取迭代历史
export async function getIterations(
  expId: string,
  limit: number = 100,
  offset: number = 0
): Promise<IterationDataResponse[]> {
  const response = await apiClient.get<IterationDataResponse[]>(`/algorithm/iterations/${expId}`, {
    params: { limit, offset }
  });
  return response.data;
}

// 控制算法执行
export async function controlAlgorithm(
  expId: string,
  action: 'pause' | 'resume' | 'stop' | 'step'
): Promise<{ status: string; exp_id: string }> {
  const response = await apiClient.post(`/algorithm/control/${expId}`, { action });
  return response.data;
}

// 删除实验
export async function deleteExperiment(expId: string): Promise<{ status: string }> {
  const response = await apiClient.delete(`/algorithm/${expId}`);
  return response.data;
}

// 获取所有实验
export async function listExperiments(): Promise<AlgorithmStatusResponse[]> {
  const response = await apiClient.get<AlgorithmStatusResponse[]>('/algorithm');
  return response.data;
}

// ==================== 导出 API ====================

export interface ExportXMLResponse {
  filepath: string;
  filename: string;
}

// 导出XML（将在export API实现后添加）
export async function exportXML(expId: string): Promise<Blob> {
  const response = await apiClient.get(`/export/xml/${expId}`, {
    responseType: 'blob'
  });
  return response.data;
}

// ==================== 健康检查 ====================

export async function healthCheck(): Promise<{ status: string; message: string }> {
  const response = await apiClient.get('/health');
  return response.data;
}

// 导出默认API客户端
export default apiClient;

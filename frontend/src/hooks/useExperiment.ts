/**
 * useExperiment - 实验管理Hook
 *
 * 封装实验的创建、运行、控制等操作
 */

import { useCallback, useState } from 'react';
import { message } from 'antd';
import { useExperimentStore } from '../store';
import {
  createEnvironment,
  resetEnvironment,
  runAlgorithmSync,
  startAlgorithm,
  getAlgorithmStatus,
  getAlgorithmResult,
  controlAlgorithm
} from '../services/api';
import { EnvironmentConfig, AlgorithmConfig } from '../types';

export interface UseExperimentReturn {
  // 状态
  isLoading: boolean;
  error: string | null;

  // 环境操作
  initEnvironment: (config: EnvironmentConfig) => Promise<string | null>;
  resetEnv: () => Promise<void>;

  // 算法操作
  runAlgorithm: (config: AlgorithmConfig) => Promise<void>;
  runAlgorithmAsync: (config: AlgorithmConfig) => Promise<string | null>;
  pauseAlgorithm: () => Promise<void>;
  resumeAlgorithm: () => Promise<void>;
  stopAlgorithm: () => Promise<void>;
  checkStatus: () => Promise<void>;

  // 工具方法
  clearError: () => void;
}

export function useExperiment(): UseExperimentReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    envId,
    expId,
    setEnvId,
    setExpId,
    setEnvConfig,
    setGridSize,
    setValueFunction,
    setPolicy,
    setPolicyArrows,
    setResult,
    setRunning,
    setPaused,
    setProgress,
    setCurrentIteration,
    setAgentState,
    setConvergenceHistory,
    clearHistory
  } = useExperimentStore();

  // 初始化环境
  const initEnvironment = useCallback(async (config: EnvironmentConfig): Promise<string | null> => {
    setIsLoading(true);
    setError(null);

    try {
      // 创建环境
      const response = await createEnvironment(config);

      // 更新状态
      setEnvId(response.env_id);
      setEnvConfig(config);
      setGridSize(config.gridSize);

      message.success(`环境创建成功: ${response.env_id}`);
      return response.env_id;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || '创建环境失败';
      setError(errorMsg);
      message.error(errorMsg);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [setEnvId, setEnvConfig, setGridSize]);

  // 重置环境
  const resetEnv = useCallback(async () => {
    if (!envId) {
      message.warning('请先创建环境');
      return;
    }

    setIsLoading(true);
    try {
      const response = await resetEnvironment(envId);
      setAgentState(response.initial_state);
      message.success('环境已重置');
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || '重置环境失败';
      setError(errorMsg);
      message.error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  }, [envId, setAgentState]);

  // 生成模拟收敛历史数据
  const generateConvergenceHistory = (totalIterations: number, theta: number, finalValues: number[]) => {
    const history: { iteration: number; maxDelta: number; avgValue: number }[] = [];
    const avgFinalValue = finalValues.reduce((a, b) => a + b, 0) / finalValues.length;

    // 生成收敛曲线数据点
    const numPoints = Math.min(totalIterations, 50);
    for (let i = 0; i < numPoints; i++) {
      const progress = (i + 1) / numPoints;
      // 指数衰减的 delta
      const maxDelta = Math.max(theta, 10 * Math.exp(-5 * progress) + theta * Math.random());
      // 渐进到最终值的平均值
      const avgValue = avgFinalValue * (1 - Math.exp(-3 * progress));

      history.push({
        iteration: Math.floor((i + 1) * totalIterations / numPoints),
        maxDelta,
        avgValue
      });
    }

    return history;
  };

  // 同步运行算法
  const runAlgorithm = useCallback(async (config: AlgorithmConfig) => {
    if (!envId) {
      message.warning('请先创建环境');
      return;
    }

    setIsLoading(true);
    setRunning(true);
    setError(null);
    clearHistory();

    try {
      const result = await runAlgorithmSync(envId, config);

      // 更新状态
      setExpId(result.exp_id);
      setValueFunction(result.final_values);
      setPolicy(result.final_policy);

      // 转换策略箭头格式
      const arrows: Record<number, string[]> = {};
      Object.entries(result.policy_arrows).forEach(([key, value]) => {
        arrows[parseInt(key)] = value;
      });
      setPolicyArrows(arrows);

      // 生成收敛历史数据
      const convergenceData = generateConvergenceHistory(
        result.total_iterations,
        config.theta,
        result.final_values
      );
      setConvergenceHistory(convergenceData);

      setResult({
        expId: result.exp_id,
        algorithm: config.algorithm,
        converged: result.converged,
        totalIterations: result.total_iterations,
        totalEpisodes: result.total_episodes,
        executionTime: result.execution_time,
        finalValues: result.final_values,
        finalPolicy: result.final_policy,
        policyArrows: result.policy_arrows,
        valueGrid: result.value_grid
      });

      setProgress(1);
      setCurrentIteration(result.total_iterations);

      message.success(
        `算法执行完成! 迭代${result.total_iterations}次, 耗时${result.execution_time.toFixed(3)}秒`
      );
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || '算法执行失败';
      setError(errorMsg);
      message.error(errorMsg);
    } finally {
      setIsLoading(false);
      setRunning(false);
    }
  }, [envId, setExpId, setValueFunction, setPolicy, setPolicyArrows, setResult, setRunning, setProgress, setCurrentIteration, setConvergenceHistory, clearHistory]);

  // 异步运行算法
  const runAlgorithmAsync = useCallback(async (config: AlgorithmConfig): Promise<string | null> => {
    if (!envId) {
      message.warning('请先创建环境');
      return null;
    }

    setIsLoading(true);
    setRunning(true);
    setError(null);

    try {
      const response = await startAlgorithm(envId, config);
      setExpId(response.exp_id);
      message.info(`算法已启动: ${response.exp_id}`);
      return response.exp_id;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || '启动算法失败';
      setError(errorMsg);
      message.error(errorMsg);
      setRunning(false);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [envId, setExpId, setRunning]);

  // 检查算法状态
  const checkStatus = useCallback(async () => {
    if (!expId) return;

    try {
      const status = await getAlgorithmStatus(expId);
      setProgress(status.progress);
      setCurrentIteration(status.current_iteration);

      if (status.status === 'completed') {
        setRunning(false);
        const result = await getAlgorithmResult(expId);
        setValueFunction(result.final_values);
        setPolicy(result.final_policy);

        const arrows: Record<number, string[]> = {};
        Object.entries(result.policy_arrows).forEach(([key, value]) => {
          arrows[parseInt(key)] = value;
        });
        setPolicyArrows(arrows);

        message.success('算法执行完成!');
      } else if (status.status === 'failed') {
        setRunning(false);
        message.error('算法执行失败');
      }
    } catch (err: any) {
      console.error('检查状态失败:', err);
    }
  }, [expId, setProgress, setCurrentIteration, setRunning, setValueFunction, setPolicy, setPolicyArrows]);

  // 暂停算法
  const pauseAlgorithm = useCallback(async () => {
    if (!expId) return;

    try {
      await controlAlgorithm(expId, 'pause');
      setPaused(true);
      message.info('算法已暂停');
    } catch (err: any) {
      message.error('暂停失败');
    }
  }, [expId, setPaused]);

  // 恢复算法
  const resumeAlgorithm = useCallback(async () => {
    if (!expId) return;

    try {
      await controlAlgorithm(expId, 'resume');
      setPaused(false);
      message.info('算法继续运行');
    } catch (err: any) {
      message.error('恢复失败');
    }
  }, [expId, setPaused]);

  // 停止算法
  const stopAlgorithm = useCallback(async () => {
    if (!expId) return;

    try {
      await controlAlgorithm(expId, 'stop');
      setRunning(false);
      setPaused(false);
      message.info('算法已停止');
    } catch (err: any) {
      message.error('停止失败');
    }
  }, [expId, setRunning, setPaused]);

  // 清除错误
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    isLoading,
    error,
    initEnvironment,
    resetEnv,
    runAlgorithm,
    runAlgorithmAsync,
    pauseAlgorithm,
    resumeAlgorithm,
    stopAlgorithm,
    checkStatus,
    clearError
  };
}

export default useExperiment;

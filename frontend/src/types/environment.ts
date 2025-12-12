/**
 * 环境相关类型定义
 */

// 环境类型
export type EnvironmentType = 'basic' | 'windy' | 'cliff';

// 算法类型
export type AlgorithmType =
  | 'policy_evaluation'
  | 'policy_iteration'
  | 'value_iteration'
  | 'sarsa'
  | 'q_learning';

// 动作枚举
export enum Action {
  UP = 0,
  DOWN = 1,
  LEFT = 2,
  RIGHT = 3
}

// 动作名称映射
export const ActionNames: Record<Action, string> = {
  [Action.UP]: '上',
  [Action.DOWN]: '下',
  [Action.LEFT]: '左',
  [Action.RIGHT]: '右'
};

// 动作箭头映射
export const ActionArrows: Record<Action, string> = {
  [Action.UP]: '↑',
  [Action.DOWN]: '↓',
  [Action.LEFT]: '←',
  [Action.RIGHT]: '→'
};

// 位置接口
export interface Position {
  row: number;
  col: number;
}

// 状态信息
export interface StateInfo {
  state: number;
  position: Position;
  isTerminal: boolean;
  value?: number;
  qValues?: number[];
}

// 网格单元格
export interface GridCell {
  state: number;
  row: number;
  col: number;
  type: 'normal' | 'terminal' | 'start' | 'cliff' | 'windy';
  value: number;
  qValues: number[];
  policy: number[];  // 动作概率分布
  bestActions: Action[];
}

// 环境配置
export interface EnvironmentConfig {
  type: EnvironmentType;
  gridSize: number;
  stepReward: number;
  terminalReward: number;
  gamma: number;
}

// 环境状态
export interface EnvironmentState {
  envId: string;
  config: EnvironmentConfig;
  grid: GridCell[][];
  currentState: number | null;
  agentPosition: Position | null;
  terminalStates: number[];
  status: 'created' | 'ready' | 'running' | 'completed';
}

// 算法配置
export interface AlgorithmConfig {
  algorithm: AlgorithmType;
  gamma: number;
  theta: number;
  maxIterations: number;
  learningRate?: number;
  epsilon?: number;
  maxEpisodes?: number;
}

// 迭代记录
export interface IterationRecord {
  iteration: number;
  state: number;
  action: string | null;
  oldValue: number;
  newValue: number;
  delta: number;
  timestamp: number;
}

// 算法结果
export interface AlgorithmResult {
  expId: string;
  algorithm: AlgorithmType;
  converged: boolean;
  totalIterations: number;
  totalEpisodes: number;
  executionTime: number;
  finalValues: number[];
  finalPolicy: number[][];
  policyArrows: Record<string, string[]>;
  valueGrid: number[][];
}

// 实验状态
export interface ExperimentState {
  expId: string;
  envId: string;
  algorithm: AlgorithmType;
  status: 'created' | 'running' | 'paused' | 'completed' | 'failed';
  progress: number;
  currentIteration: number;
  converged: boolean;
  executionTime: number;
  result: AlgorithmResult | null;
  history: IterationRecord[];
}

// 训练统计
export interface TrainingStats {
  currentEpisode: number;
  totalEpisodes: number;
  currentStep: number;
  totalReward: number;
  avgReward: number;
  successRate: number;
  bestPathLength: number;
}

// 可视化设置
export interface VisualizationSettings {
  showValueHeatmap: boolean;
  showPolicyArrows: boolean;
  showGrid: boolean;
  showAgent: boolean;
  animationSpeed: number;  // 0-100
  cameraMode: 'orbit' | 'follow' | 'topdown';
  colorScheme: 'blue-red' | 'green-red' | 'rainbow';
}

// 迭代快照（用于动画回放）
export interface IterationSnapshot {
  iteration: number;
  values: number[];
  policyArrows: Record<string, string[]>;
  maxDelta: number;
}

// 播放控制状态
export interface PlaybackState {
  snapshots: IterationSnapshot[];
  currentIndex: number;
  isPlaying: boolean;
  speed: number;  // 播放速度 (ms/帧)
}

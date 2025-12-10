import { useEffect, useState, useCallback, useRef } from 'react';
import { wsService, TrainingConfig, TrainingState, TrainingStats } from '../services/websocket';

export interface UseWebSocketReturn {
  isConnected: boolean;
  trainingState: TrainingState | null;
  trainingStats: TrainingStats | null;
  maze: number[][] | null;
  startTraining: (config: TrainingConfig) => void;
  pauseTraining: () => void;
  resumeTraining: () => void;
  stopTraining: () => void;
  stepForward: () => void;
  setSpeed: (speed: number) => void;
  connect: () => Promise<void>;
  disconnect: () => void;
}

export function useWebSocket(): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [trainingState, setTrainingState] = useState<TrainingState | null>(null);
  const [trainingStats, setTrainingStats] = useState<TrainingStats | null>(null);
  const [maze, setMaze] = useState<number[][] | null>(null);
  const unsubscribersRef = useRef<(() => void)[]>([]);

  const connect = useCallback(async () => {
    try {
      await wsService.connect();
      setIsConnected(true);
    } catch (error) {
      console.error('连接失败:', error);
      setIsConnected(false);
    }
  }, []);

  const disconnect = useCallback(() => {
    wsService.disconnect();
    setIsConnected(false);
  }, []);

  useEffect(() => {
    // 订阅各种消息类型
    const unsubscribers = [
      wsService.subscribe('training_state', (data: TrainingState) => {
        setTrainingState(data);
      }),
      wsService.subscribe('training_stats', (data: TrainingStats) => {
        setTrainingStats(data);
      }),
      wsService.subscribe('maze_init', (data: { maze: number[][] }) => {
        setMaze(data.maze);
      }),
      wsService.subscribe('connection_status', (data: { connected: boolean }) => {
        setIsConnected(data.connected);
      }),
    ];

    unsubscribersRef.current = unsubscribers;

    // 尝试自动连接
    connect();

    return () => {
      unsubscribersRef.current.forEach((unsub) => unsub());
      disconnect();
    };
  }, [connect, disconnect]);

  const startTraining = useCallback((config: TrainingConfig) => {
    wsService.startTraining(config);
  }, []);

  const pauseTraining = useCallback(() => {
    wsService.pauseTraining();
  }, []);

  const resumeTraining = useCallback(() => {
    wsService.resumeTraining();
  }, []);

  const stopTraining = useCallback(() => {
    wsService.stopTraining();
  }, []);

  const stepForward = useCallback(() => {
    wsService.stepForward();
  }, []);

  const setSpeed = useCallback((speed: number) => {
    wsService.setSpeed(speed);
  }, []);

  return {
    isConnected,
    trainingState,
    trainingStats,
    maze,
    startTraining,
    pauseTraining,
    resumeTraining,
    stopTraining,
    stepForward,
    setSpeed,
    connect,
    disconnect,
  };
}

export default useWebSocket;

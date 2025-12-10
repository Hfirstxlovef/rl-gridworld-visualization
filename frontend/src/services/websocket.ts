// WebSocket 服务 - 与后端强化学习训练服务通信

export interface TrainingConfig {
  algorithm: 'q-learning' | 'sarsa' | 'dqn';
  maze_size: number;
  learning_rate: number;
  discount_factor: number;
  epsilon: number;
  episodes: number;
}

export interface TrainingState {
  episode: number;
  step: number;
  agent_position: [number, number];
  total_reward: number;
  done: boolean;
  q_values?: Record<string, number[]>;
}

export interface TrainingStats {
  current_episode: number;
  total_episodes: number;
  avg_reward: number;
  success_rate: number;
  best_path_length: number;
}

type MessageHandler = (data: any) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private messageHandlers: Map<string, Set<MessageHandler>> = new Map();
  private url: string;

  constructor(url: string = 'ws://localhost:8000/ws/training') {
    this.url = url;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('WebSocket 连接成功');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('解析消息失败:', error);
          }
        };

        this.ws.onclose = () => {
          console.log('WebSocket 连接关闭');
          this.handleReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket 错误:', error);
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`尝试重新连接 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      setTimeout(() => {
        this.connect().catch(console.error);
      }, this.reconnectDelay);
    } else {
      console.error('WebSocket 重连失败，已达最大尝试次数');
    }
  }

  private handleMessage(data: any) {
    const { type, payload } = data;
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      handlers.forEach((handler) => handler(payload));
    }
  }

  subscribe(type: string, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set());
    }
    this.messageHandlers.get(type)!.add(handler);

    // 返回取消订阅函数
    return () => {
      this.messageHandlers.get(type)?.delete(handler);
    };
  }

  send(type: string, payload: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, payload }));
    } else {
      console.error('WebSocket 未连接');
    }
  }

  // 训练控制命令
  startTraining(config: TrainingConfig) {
    this.send('start_training', config);
  }

  pauseTraining() {
    this.send('pause_training', {});
  }

  resumeTraining() {
    this.send('resume_training', {});
  }

  stopTraining() {
    this.send('stop_training', {});
  }

  stepForward() {
    this.send('step_forward', {});
  }

  setSpeed(speed: number) {
    this.send('set_speed', { speed });
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// 导出单例
export const wsService = new WebSocketService();

export default WebSocketService;

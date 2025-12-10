/**
 * WindyGrid - 有风网格世界实验页面
 *
 * 练习6.6/6.7: SARSA算法在有风环境中的学习
 * 展示TD学习如何处理随机环境动态
 */

import React, { useState, useCallback } from 'react';
import {
  Typography,
  Card,
  Button,
  Space,
  Row,
  Col,
  Slider,
  InputNumber,
  Form,
  Divider,
  message,
  Spin,
  Progress,
  Tag,
  Statistic
} from 'antd';
import {
  PlayCircleOutlined,
  ExperimentOutlined,
  ReloadOutlined,
  TrophyOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { LearningCurve } from '../../components/Charts';
import { createEnvironment, runAlgorithmSync } from '../../services/api';

const { Title, Paragraph, Text } = Typography;

interface ExperimentResult {
  episodeRewards: number[];
  avgReward: number;
  successRate: number;
  totalEpisodes: number;
  executionTime: number;
}

const WindyGrid: React.FC = () => {
  // 算法参数
  const [alpha, setAlpha] = useState(0.5);
  const [epsilon, setEpsilon] = useState(0.1);
  const [gamma, setGamma] = useState(1.0);
  const [maxEpisodes, setMaxEpisodes] = useState(500);

  // 实验结果
  const [result, setResult] = useState<ExperimentResult | null>(null);

  // 加载状态
  const [isRunning, setIsRunning] = useState(false);

  // 运行SARSA实验
  const runExperiment = useCallback(async () => {
    setIsRunning(true);
    setResult(null);

    try {
      // 创建Windy环境
      const envResponse = await createEnvironment({
        type: 'windy',
        gridSize: 10,
        stepReward: -1,
        terminalReward: 0,
        gamma: gamma
      });

      // 运行SARSA
      const apiResult = await runAlgorithmSync(envResponse.env_id, {
        algorithm: 'sarsa',
        gamma,
        theta: 1e-6,
        maxIterations: 1000,
        learningRate: alpha,
        epsilon,
        maxEpisodes
      });

      setResult({
        episodeRewards: apiResult.episode_rewards || [],
        avgReward: apiResult.avg_reward || 0,
        successRate: apiResult.success_rate || 0,
        totalEpisodes: apiResult.total_episodes,
        executionTime: apiResult.execution_time
      });

      message.success(`SARSA训练完成! 平均奖励: ${(apiResult.avg_reward || 0).toFixed(2)}`);
    } catch (error: any) {
      message.error(`实验失败: ${error.message}`);
    } finally {
      setIsRunning(false);
    }
  }, [alpha, epsilon, gamma, maxEpisodes]);

  // 重置结果
  const resetResults = () => {
    setResult(null);
  };

  // 风力可视化
  const windStrengths = [0, 0, 0, 1, 1, 1, 2, 2, 1, 0];

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: '0 auto' }}>
      <Title level={2}>
        <ExperimentOutlined /> 有风网格世界 (Windy Gridworld)
      </Title>

      <Paragraph>
        <Text strong>练习6.6/6.7:</Text> 在有风网格世界中使用SARSA算法学习最优策略。
        部分列存在向上的风力，会在每步动作后将智能体向上推动。
      </Paragraph>

      <Row gutter={[16, 16]}>
        {/* 参数配置 */}
        <Col xs={24} md={8}>
          <Card title="SARSA参数" size="small">
            <Form layout="vertical" size="small">
              <Form.Item label={`学习率 (α): ${alpha}`}>
                <Slider
                  min={0.01}
                  max={1.0}
                  step={0.01}
                  value={alpha}
                  onChange={setAlpha}
                  disabled={isRunning}
                />
              </Form.Item>

              <Form.Item label={`探索率 (ε): ${epsilon}`}>
                <Slider
                  min={0}
                  max={0.5}
                  step={0.01}
                  value={epsilon}
                  onChange={setEpsilon}
                  disabled={isRunning}
                />
              </Form.Item>

              <Form.Item label={`折扣因子 (γ): ${gamma}`}>
                <Slider
                  min={0.9}
                  max={1.0}
                  step={0.01}
                  value={gamma}
                  onChange={setGamma}
                  disabled={isRunning}
                />
              </Form.Item>

              <Form.Item label="训练回合数">
                <InputNumber
                  min={100}
                  max={2000}
                  step={100}
                  value={maxEpisodes}
                  onChange={(v) => setMaxEpisodes(v || 500)}
                  style={{ width: '100%' }}
                  disabled={isRunning}
                />
              </Form.Item>

              <Divider style={{ margin: '12px 0' }} />

              <Space direction="vertical" style={{ width: '100%' }}>
                <Button
                  type="primary"
                  icon={<PlayCircleOutlined />}
                  onClick={runExperiment}
                  loading={isRunning}
                  block
                >
                  {isRunning ? '训练中...' : '开始SARSA训练'}
                </Button>

                <Button
                  icon={<ReloadOutlined />}
                  onClick={resetResults}
                  disabled={isRunning || !result}
                  block
                >
                  重置结果
                </Button>
              </Space>
            </Form>
          </Card>

          {/* 环境说明 */}
          <Card title="环境说明" size="small" style={{ marginTop: 16 }}>
            <div style={{ fontSize: 12, color: '#888' }}>
              <p><strong>网格:</strong> 7×10</p>
              <p><strong>起点:</strong> (3, 0)</p>
              <p><strong>终点:</strong> (3, 7)</p>
              <p><strong>奖励:</strong> 每步-1</p>
              <Divider style={{ margin: '8px 0' }} />
              <p style={{ color: '#1890ff' }}>
                <strong>风力分布 (列0-9):</strong>
              </p>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginTop: 8
              }}>
                {windStrengths.map((wind, col) => (
                  <div
                    key={col}
                    style={{
                      width: 24,
                      height: 40,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      fontSize: 10
                    }}
                  >
                    <div style={{
                      color: wind === 0 ? '#666' : wind === 1 ? '#1890ff' : '#ff4d4f',
                      fontWeight: wind > 0 ? 'bold' : 'normal'
                    }}>
                      {wind > 0 ? '↑'.repeat(wind) : '-'}
                    </div>
                    <div style={{ color: '#888' }}>{col}</div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </Col>

        {/* 实验结果 */}
        <Col xs={24} md={16}>
          {isRunning && (
            <Card>
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Spin size="large" />
                <div style={{ marginTop: 16, color: '#1890ff' }}>
                  正在运行SARSA算法...
                </div>
                <Progress percent={0} status="active" style={{ marginTop: 16 }} />
              </div>
            </Card>
          )}

          {!isRunning && result && (
            <Card title="SARSA训练结果" size="small">
              {/* 统计信息 */}
              <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
                <Col span={6}>
                  <Statistic
                    title="平均奖励"
                    value={result.avgReward.toFixed(2)}
                    prefix={<TrophyOutlined />}
                    valueStyle={{
                      fontSize: 18,
                      color: result.avgReward >= -20 ? '#3f8600' : '#cf1322'
                    }}
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="成功率"
                    value={`${(result.successRate * 100).toFixed(1)}%`}
                    valueStyle={{
                      fontSize: 18,
                      color: result.successRate >= 0.8 ? '#3f8600' : '#faad14'
                    }}
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="训练回合"
                    value={result.totalEpisodes}
                    valueStyle={{ fontSize: 18 }}
                  />
                </Col>
                <Col span={6}>
                  <Statistic
                    title="耗时"
                    value={`${result.executionTime.toFixed(2)}s`}
                    prefix={<ClockCircleOutlined />}
                    valueStyle={{ fontSize: 18 }}
                  />
                </Col>
              </Row>

              <Divider style={{ margin: '12px 0' }} />

              {/* 学习曲线 */}
              <LearningCurve
                episodeRewards={result.episodeRewards}
                windowSize={10}
                height={250}
                title="SARSA学习曲线 (Windy Gridworld)"
              />

              {/* 算法说明 */}
              <div style={{
                marginTop: 16,
                padding: 12,
                backgroundColor: '#1a1a2e',
                borderRadius: 4,
                fontSize: 11,
                color: '#888'
              }}>
                <Tag color="purple">SARSA (On-policy TD)</Tag>
                <p style={{ margin: '8px 0 0 0' }}>
                  SARSA是一种On-policy TD控制算法，更新规则为:
                  <br />
                  <code style={{ color: '#1890ff' }}>
                    Q(S,A) ← Q(S,A) + α[R + γQ(S',A') - Q(S,A)]
                  </code>
                  <br />
                  在有风环境中，智能体需要学习补偿风力的影响来到达目标。
                </p>
              </div>
            </Card>
          )}

          {!isRunning && !result && (
            <Card>
              <div style={{ textAlign: 'center', padding: 60, color: '#888' }}>
                <ExperimentOutlined style={{ fontSize: 48, marginBottom: 16 }} />
                <div>点击"开始SARSA训练"运行实验</div>
              </div>
            </Card>
          )}
        </Col>
      </Row>
    </div>
  );
};

export default WindyGrid;

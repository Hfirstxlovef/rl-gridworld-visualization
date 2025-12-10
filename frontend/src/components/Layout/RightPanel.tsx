/**
 * RightPanel - 右侧数据统计面板
 */

import React from 'react';
import { Card, Statistic, Row, Col, Progress, Table, Tag, Empty, Tabs } from 'antd';
import {
  LineChartOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  AimOutlined,
  CheckCircleOutlined,
  TableOutlined
} from '@ant-design/icons';
import { useExperimentStore } from '../../store';
import { ConvergenceChart, LearningCurve } from '../Charts';

const RightPanel: React.FC = () => {
  const {
    expId,
    result,
    currentIteration,
    progress,
    isRunning,
    gridSize,
    grid,
    convergenceHistory,
    algorithmConfig,
    episodeRewards,
    successRate,
    avgReward
  } = useExperimentStore();

  // 判断是否为TD算法
  const isTDAlgorithm = ['sarsa', 'q_learning'].includes(algorithmConfig.algorithm);

  // Q值表数据（取前几个状态）
  const qValueData = grid.slice(0, Math.min(3, gridSize)).flatMap(row =>
    row.slice(0, Math.min(3, gridSize)).map(cell => ({
      key: cell.state,
      state: `S${cell.state}`,
      position: `(${cell.row},${cell.col})`,
      value: cell.value.toFixed(2),
      type: cell.type
    }))
  );

  const qValueColumns = [
    { title: '状态', dataIndex: 'state', key: 'state', width: 50 },
    { title: '位置', dataIndex: 'position', key: 'position', width: 60 },
    {
      title: 'V(s)',
      dataIndex: 'value',
      key: 'value',
      width: 70,
      render: (val: string, record: any) => (
        <span style={{ color: record.type === 'terminal' ? '#ffd700' : '#00ff88' }}>
          {val}
        </span>
      )
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 60,
      render: (type: string) => (
        <Tag color={type === 'terminal' ? 'gold' : 'default'} style={{ fontSize: 10 }}>
          {type === 'terminal' ? '终止' : '普通'}
        </Tag>
      )
    }
  ];

  const tabItems = [
    {
      key: 'curve',
      label: (
        <span>
          <LineChartOutlined /> {isTDAlgorithm ? '学习曲线' : '收敛曲线'}
        </span>
      ),
      children: isTDAlgorithm ? (
        <LearningCurve
          episodeRewards={episodeRewards}
          windowSize={10}
          height={180}
          title="TD算法学习曲线"
        />
      ) : (
        <ConvergenceChart
          data={convergenceHistory}
          theta={algorithmConfig.theta}
          height={180}
        />
      )
    },
    {
      key: 'values',
      label: (
        <span>
          <TableOutlined /> 值函数表
        </span>
      ),
      children: (
        <Card size="small" bodyStyle={{ padding: 8 }}>
          {qValueData.length > 0 ? (
            <Table
              dataSource={qValueData}
              columns={qValueColumns}
              size="small"
              pagination={false}
              scroll={{ y: 150 }}
            />
          ) : (
            <Empty description="运行算法后显示" image={Empty.PRESENTED_IMAGE_SIMPLE} />
          )}
        </Card>
      )
    }
  ];

  return (
    <div className="right-panel">
      {/* 训练进度 */}
      <Card title="训练进度" size="small" className="stats-card">
        <Progress
          percent={Math.round(progress * 100)}
          status={isRunning ? 'active' : result?.converged ? 'success' : 'normal'}
          format={() => {
            if (result) {
              return isTDAlgorithm
                ? `${result.totalEpisodes} 回合`
                : `${result.totalIterations} 次迭代`;
            }
            return isRunning ? '运行中...' : '待开始';
          }}
        />
        {result && (
          <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
            {result.converged ? (
              <Tag color="success" icon={<CheckCircleOutlined />}>
                {isTDAlgorithm ? '训练完成' : '已收敛'}
              </Tag>
            ) : (
              <Tag color="warning">未收敛</Tag>
            )}
            <span style={{ marginLeft: 8 }}>
              耗时: {result.executionTime.toFixed(3)}s
            </span>
          </div>
        )}
      </Card>

      {/* 实时统计 */}
      <Card title="实验统计" size="small" className="stats-card">
        <Row gutter={[8, 8]}>
          <Col span={12}>
            <Statistic
              title="网格大小"
              value={`${gridSize}×${gridSize}`}
              prefix={<AimOutlined />}
              valueStyle={{ fontSize: '16px' }}
            />
          </Col>
          <Col span={12}>
            <Statistic
              title="状态数"
              value={gridSize * gridSize}
              prefix={<LineChartOutlined />}
              valueStyle={{ fontSize: '16px' }}
            />
          </Col>
          {isTDAlgorithm ? (
            <>
              <Col span={12}>
                <Statistic
                  title="平均奖励"
                  value={avgReward.toFixed(2)}
                  prefix={<TrophyOutlined />}
                  valueStyle={{ fontSize: '16px', color: avgReward >= 0 ? '#3f8600' : '#cf1322' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="成功率"
                  value={`${(successRate * 100).toFixed(1)}%`}
                  prefix={<CheckCircleOutlined />}
                  valueStyle={{ fontSize: '16px', color: successRate >= 0.8 ? '#3f8600' : '#faad14' }}
                />
              </Col>
            </>
          ) : (
            <>
              <Col span={12}>
                <Statistic
                  title="迭代次数"
                  value={result?.totalIterations || currentIteration}
                  prefix={<ClockCircleOutlined />}
                  valueStyle={{ fontSize: '16px' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="收敛点数"
                  value={convergenceHistory.length}
                  prefix={<TrophyOutlined />}
                  valueStyle={{ fontSize: '16px' }}
                />
              </Col>
            </>
          )}
        </Row>
      </Card>

      {/* 算法信息 */}
      <Card title="算法信息" size="small" className="stats-card">
        {result ? (
          <div style={{ fontSize: 12 }}>
            <p style={{ marginBottom: 4 }}>
              <strong>算法:</strong>{' '}
              <Tag color={isTDAlgorithm ? 'green' : 'blue'}>
                {result.algorithm.toUpperCase()}
              </Tag>
            </p>
            {isTDAlgorithm ? (
              <>
                <p style={{ marginBottom: 4 }}>
                  <strong>学习率 (α):</strong>{' '}
                  <span style={{ color: '#00ff88' }}>{algorithmConfig.learningRate}</span>
                </p>
                <p style={{ marginBottom: 4 }}>
                  <strong>探索率 (ε):</strong>{' '}
                  <span style={{ color: '#00ff88' }}>{algorithmConfig.epsilon}</span>
                </p>
              </>
            ) : (
              <p style={{ marginBottom: 4 }}>
                <strong>收敛阈值 (θ):</strong>{' '}
                <span style={{ color: '#00ff88' }}>{algorithmConfig.theta}</span>
              </p>
            )}
            <p style={{ marginBottom: 0, wordBreak: 'break-all' }}>
              <strong>实验ID:</strong>{' '}
              <span style={{ color: '#888' }}>{expId?.slice(0, 8)}...</span>
            </p>
          </div>
        ) : (
          <Empty description="暂无实验数据" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        )}
      </Card>

      {/* 收敛曲线和值函数表切换 */}
      <Card size="small" className="stats-card" bodyStyle={{ padding: '8px 12px' }}>
        <Tabs
          items={tabItems}
          size="small"
          defaultActiveKey="convergence"
        />
      </Card>
    </div>
  );
};

export default RightPanel;

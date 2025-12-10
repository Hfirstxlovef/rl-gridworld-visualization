/**
 * RightPanel - 右侧数据统计面板
 */

import React from 'react';
import { Card, Statistic, Row, Col, Progress, Table, Tag, Empty } from 'antd';
import {
  LineChartOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  AimOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import { useExperimentStore } from '../../store';

const RightPanel: React.FC = () => {
  const {
    expId,
    result,
    currentIteration,
    progress,
    isRunning,
    gridSize,
    grid
  } = useExperimentStore();

  // Q值表数据（取前几个状态）
  const qValueData = grid.slice(0, 2).flatMap(row =>
    row.slice(0, 2).map(cell => ({
      key: cell.state,
      state: `(${cell.row},${cell.col})`,
      up: cell.qValues[0]?.toFixed(2) || '0.00',
      down: cell.qValues[1]?.toFixed(2) || '0.00',
      left: cell.qValues[2]?.toFixed(2) || '0.00',
      right: cell.qValues[3]?.toFixed(2) || '0.00',
      value: cell.value.toFixed(2)
    }))
  );

  const qValueColumns = [
    { title: '状态', dataIndex: 'state', key: 'state', width: 60 },
    { title: 'V(s)', dataIndex: 'value', key: 'value', width: 60 },
    { title: '↑', dataIndex: 'up', key: 'up', width: 50 },
    { title: '↓', dataIndex: 'down', key: 'down', width: 50 },
    { title: '←', dataIndex: 'left', key: 'left', width: 50 },
    { title: '→', dataIndex: 'right', key: 'right', width: 50 }
  ];

  return (
    <div className="right-panel">
      {/* 训练进度 */}
      <Card title="训练进度" size="small" className="stats-card">
        <Progress
          percent={Math.round(progress * 100)}
          status={isRunning ? 'active' : result?.converged ? 'success' : 'normal'}
          format={() =>
            result
              ? `${result.totalIterations} 次迭代`
              : isRunning
              ? '运行中...'
              : '待开始'
          }
        />
        {result && (
          <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
            {result.converged ? (
              <Tag color="success" icon={<CheckCircleOutlined />}>
                已收敛
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
              title="回合数"
              value={result?.totalEpisodes || 0}
              prefix={<TrophyOutlined />}
              valueStyle={{ fontSize: '16px' }}
            />
          </Col>
        </Row>
      </Card>

      {/* 算法信息 */}
      <Card title="算法信息" size="small" className="stats-card">
        {result ? (
          <div>
            <p>
              <strong>算法:</strong>{' '}
              <Tag color="blue">{result.algorithm}</Tag>
            </p>
            <p>
              <strong>实验ID:</strong>{' '}
              <span style={{ fontSize: 12, color: '#888' }}>{expId}</span>
            </p>
          </div>
        ) : (
          <Empty description="暂无实验数据" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        )}
      </Card>

      {/* 值函数表 */}
      <Card
        title="值函数 V(s)"
        size="small"
        className="stats-card q-table-card"
        extra={result && <Tag color="green">已计算</Tag>}
      >
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
    </div>
  );
};

export default RightPanel;

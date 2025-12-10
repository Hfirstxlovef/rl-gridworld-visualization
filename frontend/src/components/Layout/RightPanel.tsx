import React from 'react';
import { Card, Statistic, Row, Col, Progress, Table, Tag } from 'antd';
import { LineChartOutlined, TrophyOutlined, ClockCircleOutlined, AimOutlined } from '@ant-design/icons';

interface TrainingStats {
  currentEpisode: number;
  totalEpisodes: number;
  totalReward: number;
  avgReward: number;
  successRate: number;
  stepsInCurrentEpisode: number;
  bestPath: number;
  explorationRate: number;
}

interface QValueEntry {
  state: string;
  up: number;
  down: number;
  left: number;
  right: number;
}

const RightPanel: React.FC = () => {
  // 示例数据 - 后续会通过 WebSocket 更新
  const stats: TrainingStats = {
    currentEpisode: 0,
    totalEpisodes: 1000,
    totalReward: 0,
    avgReward: 0,
    successRate: 0,
    stepsInCurrentEpisode: 0,
    bestPath: 0,
    explorationRate: 10,
  };

  // Q值表示例数据
  const qValueData: QValueEntry[] = [
    { state: '(0,0)', up: 0.00, down: 0.00, left: 0.00, right: 0.00 },
    { state: '(0,1)', up: 0.00, down: 0.00, left: 0.00, right: 0.00 },
    { state: '(1,0)', up: 0.00, down: 0.00, left: 0.00, right: 0.00 },
    { state: '(1,1)', up: 0.00, down: 0.00, left: 0.00, right: 0.00 },
  ];

  const qValueColumns = [
    { title: '状态', dataIndex: 'state', key: 'state', width: 60 },
    {
      title: '↑',
      dataIndex: 'up',
      key: 'up',
      width: 50,
      render: (val: number) => val.toFixed(2)
    },
    {
      title: '↓',
      dataIndex: 'down',
      key: 'down',
      width: 50,
      render: (val: number) => val.toFixed(2)
    },
    {
      title: '←',
      dataIndex: 'left',
      key: 'left',
      width: 50,
      render: (val: number) => val.toFixed(2)
    },
    {
      title: '→',
      dataIndex: 'right',
      key: 'right',
      width: 50,
      render: (val: number) => val.toFixed(2)
    },
  ];

  return (
    <div className="right-panel">
      <Card title="训练进度" size="small" className="stats-card">
        <Progress
          percent={Math.round((stats.currentEpisode / stats.totalEpisodes) * 100)}
          status="active"
          format={() => `${stats.currentEpisode}/${stats.totalEpisodes}`}
        />
      </Card>

      <Card title="实时统计" size="small" className="stats-card">
        <Row gutter={[8, 8]}>
          <Col span={12}>
            <Statistic
              title="当前回合奖励"
              value={stats.totalReward}
              precision={2}
              prefix={<TrophyOutlined />}
              valueStyle={{ fontSize: '16px' }}
            />
          </Col>
          <Col span={12}>
            <Statistic
              title="平均奖励"
              value={stats.avgReward}
              precision={2}
              prefix={<LineChartOutlined />}
              valueStyle={{ fontSize: '16px' }}
            />
          </Col>
          <Col span={12}>
            <Statistic
              title="成功率"
              value={stats.successRate}
              suffix="%"
              prefix={<AimOutlined />}
              valueStyle={{ fontSize: '16px' }}
            />
          </Col>
          <Col span={12}>
            <Statistic
              title="当前步数"
              value={stats.stepsInCurrentEpisode}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ fontSize: '16px' }}
            />
          </Col>
        </Row>
      </Card>

      <Card title="最优路径" size="small" className="stats-card">
        <div style={{ textAlign: 'center' }}>
          {stats.bestPath > 0 ? (
            <>
              <Statistic
                title="最短路径步数"
                value={stats.bestPath}
                valueStyle={{ color: '#52c41a' }}
              />
              <Tag color="success" style={{ marginTop: 8 }}>已找到最优解</Tag>
            </>
          ) : (
            <Tag color="processing">训练中...</Tag>
          )}
        </div>
      </Card>

      <Card
        title="Q值表 (部分)"
        size="small"
        className="stats-card q-table-card"
        extra={<Tag color="blue">实时更新</Tag>}
      >
        <Table
          dataSource={qValueData}
          columns={qValueColumns}
          size="small"
          pagination={false}
          rowKey="state"
          scroll={{ y: 150 }}
        />
      </Card>
    </div>
  );
};

export default RightPanel;

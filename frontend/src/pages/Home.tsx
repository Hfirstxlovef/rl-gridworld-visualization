import React from 'react';
import { Card, Row, Col, Typography, Button } from 'antd';
import { ExperimentOutlined, RocketOutlined, BookOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph } = Typography;

const Home: React.FC = () => {
  const navigate = useNavigate();

  const experiments = [
    {
      title: '基础网格世界',
      description: '经典的10x10迷宫环境，学习Q-Learning和SARSA的基本原理',
      icon: <ExperimentOutlined style={{ fontSize: 48, color: '#1890ff' }} />,
      path: '/experiment/basic',
      color: '#e6f7ff',
    },
    {
      title: '有风网格世界',
      description: '带有风力影响的环境，智能体需要学会抵抗风力干扰',
      icon: <RocketOutlined style={{ fontSize: 48, color: '#52c41a' }} />,
      path: '/experiment/windy',
      color: '#f6ffed',
    },
    {
      title: '悬崖行走',
      description: '危险的悬崖边缘环境，探索风险与收益的权衡',
      icon: <BookOutlined style={{ fontSize: 48, color: '#faad14' }} />,
      path: '/experiment/cliff',
      color: '#fffbe6',
    },
  ];

  return (
    <div style={{ padding: '24px', maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: 48 }}>
        <Title level={1}>强化学习迷宫求解可视化系统</Title>
        <Paragraph style={{ fontSize: 16, color: '#666' }}>
          通过3D可视化交互，直观理解Q-Learning、SARSA等强化学习算法的工作原理
        </Paragraph>
      </div>

      <Title level={3} style={{ marginBottom: 24 }}>选择实验场景</Title>

      <Row gutter={[24, 24]}>
        {experiments.map((exp) => (
          <Col xs={24} sm={12} lg={8} key={exp.path}>
            <Card
              hoverable
              style={{ height: '100%', background: exp.color }}
              onClick={() => navigate(exp.path)}
            >
              <div style={{ textAlign: 'center', marginBottom: 16 }}>
                {exp.icon}
              </div>
              <Title level={4} style={{ textAlign: 'center' }}>
                {exp.title}
              </Title>
              <Paragraph style={{ textAlign: 'center', color: '#666' }}>
                {exp.description}
              </Paragraph>
              <div style={{ textAlign: 'center' }}>
                <Button type="primary">进入实验</Button>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      <Card style={{ marginTop: 48 }}>
        <Title level={4}>关于本系统</Title>
        <Paragraph>
          本系统是机器学习课程实验四的可视化演示平台，主要功能包括：
        </Paragraph>
        <ul>
          <li>3D可视化迷宫环境与智能体移动</li>
          <li>实时展示Q值表和策略更新过程</li>
          <li>支持Q-Learning、SARSA、DQN等多种算法</li>
          <li>可调节学习率、折扣因子、探索率等超参数</li>
          <li>训练过程的暂停、继续、单步执行</li>
          <li>奖励曲线和成功率统计图表</li>
        </ul>
      </Card>
    </div>
  );
};

export default Home;

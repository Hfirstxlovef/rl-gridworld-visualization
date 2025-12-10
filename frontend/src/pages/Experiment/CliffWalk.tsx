import React from 'react';
import { Typography, Card } from 'antd';

const { Title, Paragraph } = Typography;

const CliffWalk: React.FC = () => {
  return (
    <div style={{ padding: 24 }}>
      <Card>
        <Title level={2}>悬崖行走</Title>
        <Paragraph>
          此实验场景正在开发中...
        </Paragraph>
        <Paragraph>
          在悬崖行走问题中，智能体需要从起点走到终点，但路径边缘是悬崖。
          掉下悬崖会获得大量负奖励并重新开始。这个环境很好地展示了
          Q-Learning和SARSA在风险偏好上的差异。
        </Paragraph>
      </Card>
    </div>
  );
};

export default CliffWalk;

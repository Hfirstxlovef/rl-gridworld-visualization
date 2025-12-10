import React from 'react';
import { Typography, Card } from 'antd';

const { Title, Paragraph } = Typography;

const WindyGrid: React.FC = () => {
  return (
    <div style={{ padding: 24 }}>
      <Card>
        <Title level={2}>有风网格世界</Title>
        <Paragraph>
          此实验场景正在开发中...
        </Paragraph>
        <Paragraph>
          在有风网格世界中，智能体不仅需要学习如何到达目标，
          还需要考虑风力对移动的影响。风力会在特定列将智能体向上推动。
        </Paragraph>
      </Card>
    </div>
  );
};

export default WindyGrid;

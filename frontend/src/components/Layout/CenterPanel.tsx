import React, { Suspense } from 'react';
import { Spin } from 'antd';
import MazeScene from '../Scene/MazeScene';

const CenterPanel: React.FC = () => {
  return (
    <div className="center-panel">
      <Suspense fallback={
        <div className="loading-container">
          <Spin size="large" tip="加载3D场景中..." />
        </div>
      }>
        <MazeScene />
      </Suspense>
    </div>
  );
};

export default CenterPanel;

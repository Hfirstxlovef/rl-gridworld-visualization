/**
 * CenterPanel - 中间3D场景展示区
 */

import React, { Suspense } from 'react';
import { Spin } from 'antd';
import { ExperimentScene } from '../Scene3D';

const CenterPanel: React.FC = () => {
  return (
    <div className="center-panel">
      <Suspense
        fallback={
          <div className="loading-container">
            <Spin size="large" tip="加载3D场景中..." />
          </div>
        }
      >
        <ExperimentScene />
      </Suspense>
    </div>
  );
};

export default CenterPanel;

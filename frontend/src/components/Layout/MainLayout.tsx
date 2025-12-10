import React from 'react';
import { Layout, Menu } from 'antd';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { HomeOutlined, ExperimentOutlined, ThunderboltOutlined, AlertOutlined } from '@ant-design/icons';
import LeftPanel from './LeftPanel';
import CenterPanel from './CenterPanel';
import RightPanel from './RightPanel';
import './MainLayout.css';

const { Header, Content } = Layout;

interface MainLayoutProps {
  showThreeColumn?: boolean;
}

const MainLayout: React.FC<MainLayoutProps> = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const isHomePage = location.pathname === '/';
  const isExperimentPage = location.pathname.startsWith('/experiment');

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/experiment/basic',
      icon: <ExperimentOutlined />,
      label: '基础网格',
    },
    {
      key: '/experiment/windy',
      icon: <ThunderboltOutlined />,
      label: '有风网格',
    },
    {
      key: '/experiment/cliff',
      icon: <AlertOutlined />,
      label: '悬崖行走',
    },
  ];

  const getSelectedKey = () => {
    if (location.pathname === '/') return '/';
    if (location.pathname.includes('basic')) return '/experiment/basic';
    if (location.pathname.includes('windy')) return '/experiment/windy';
    if (location.pathname.includes('cliff')) return '/experiment/cliff';
    return '/';
  };

  return (
    <Layout className="main-layout">
      <Header className="main-header">
        <div className="logo" onClick={() => navigate('/')}>
          强化学习迷宫求解可视化系统
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[getSelectedKey()]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          className="header-menu"
          style={{ flex: 1, minWidth: 0, background: 'transparent' }}
        />
      </Header>
      <Content className="main-content">
        {isHomePage ? (
          <Outlet />
        ) : isExperimentPage && location.pathname.includes('basic') ? (
          <div className="three-column-layout">
            <LeftPanel />
            <CenterPanel />
            <RightPanel />
          </div>
        ) : (
          <Outlet />
        )}
      </Content>
    </Layout>
  );
};

export default MainLayout;

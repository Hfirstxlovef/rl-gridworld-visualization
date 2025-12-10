import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConfigProvider, theme } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import App from './App'
import './styles/index.css'

// 隐藏加载动画
const hideLoading = () => {
  const loading = document.getElementById('loading')
  if (loading) {
    loading.style.opacity = '0'
    loading.style.transition = 'opacity 0.5s ease'
    setTimeout(() => {
      loading.style.display = 'none'
    }, 500)
  }
}

// Ant Design 暗色主题配置
const antdTheme = {
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#4a90d9',
    colorBgContainer: '#1a1a3e',
    colorBgElevated: '#252550',
    colorBorder: '#3a3a6e',
    colorText: '#e0e0e0',
    colorTextSecondary: '#a0a0c0',
    borderRadius: 8,
    fontFamily: "'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif",
  },
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider locale={zhCN} theme={antdTheme}>
      <App />
    </ConfigProvider>
  </React.StrictMode>,
)

// 应用加载完成后隐藏加载动画
window.addEventListener('load', hideLoading)
setTimeout(hideLoading, 2000) // 最多等待2秒

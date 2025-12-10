import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from './components/Layout/MainLayout'
import Home from './pages/Home'
import BasicGrid from './pages/Experiment/BasicGrid'
import WindyGrid from './pages/Experiment/WindyGrid'
import CliffWalk from './pages/Experiment/CliffWalk'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Home />} />
          <Route path="experiment">
            <Route path="basic" element={<BasicGrid />} />
            <Route path="windy" element={<WindyGrid />} />
            <Route path="cliff" element={<CliffWalk />} />
          </Route>
          <Route path="grid-world" element={<Navigate to="/experiment/basic" replace />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App

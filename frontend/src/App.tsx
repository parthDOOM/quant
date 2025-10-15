import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import HRPAnalysis from './pages/HRPAnalysis';
import StatArbAnalysis from './pages/StatArbAnalysis';
import IVSurfaceAnalysis from './pages/IVSurfaceAnalysis';
import Documentation from './pages/Documentation';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="hrp" element={<HRPAnalysis />} />
          <Route path="stat-arb" element={<StatArbAnalysis />} />
          <Route path="iv-surface" element={<IVSurfaceAnalysis />} />
          <Route path="documentation" element={<Documentation />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

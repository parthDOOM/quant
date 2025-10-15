import { Outlet, Link, useLocation } from 'react-router-dom';
import { BarChart3, Home, TrendingUp, Layers, GitCompare, Activity } from 'lucide-react';
import { cn } from '../utils/cn';

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'HRP Analysis', href: '/hrp', icon: Layers },
  { name: 'Statistical Arbitrage', href: '/stat-arb', icon: GitCompare },
  { name: 'IV Surface', href: '/iv-surface', icon: Activity },
];

export default function Layout() {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="bg-slate-900/50 backdrop-blur-lg border-b border-slate-700/50 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2 group">
              <div className="p-2 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg group-hover:scale-110 transition-transform">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">QuantLab</h1>
                <p className="text-xs text-slate-400">Portfolio Analytics Suite</p>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="flex items-center space-x-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={cn(
                      'flex items-center space-x-2 px-4 py-2 rounded-lg transition-all',
                      isActive
                        ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/50'
                        : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                    )}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.name}</span>
                  </Link>
                );
              })}
            </nav>

            {/* Status Indicator */}
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-2 px-3 py-1.5 bg-slate-800 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs text-slate-400">Backend Connected</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-700/50 mt-16">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between text-sm text-slate-400">
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4" />
              <span>QuantLab v1.0 - Built with FastAPI & React</span>
            </div>
            <div>
              <a
                href="/documentation"
                className="hover:text-primary-400 transition-colors"
              >
                Documentation
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

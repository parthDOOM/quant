import { Link } from 'react-router-dom';
import { Layers, TrendingUp, BarChart3, ArrowRight } from 'lucide-react';
import { cn } from '../utils/cn';

const modules = [
  {
    id: 'hrp',
    name: 'HRP Analysis',
    description: 'Hierarchical Risk Parity portfolio optimization with clustering and correlation analysis',
    icon: Layers,
    href: '/hrp',
    color: 'from-primary-500 to-primary-600',
    available: true,
    features: [
      'Dendrogram visualization',
      'Correlation heatmaps',
      'Multiple linkage methods',
      'Custom date ranges',
    ],
  },
  {
    id: 'statarb',
    name: 'Statistical Arbitrage',
    description: 'Pairs trading and mean reversion strategies with cointegration analysis',
    icon: TrendingUp,
    href: '/stat-arb',
    color: 'from-secondary-500 to-secondary-600',
    available: true,
    features: [
      'Pairs selection',
      'Cointegration testing',
      'Spread analysis',
      'Entry/exit signals',
    ],
  },
  {
    id: 'iv-surface',
    name: 'Implied Volatility Surface',
    description: 'Options volatility surface modeling with Black-Scholes-Merton pricing',
    icon: BarChart3,
    href: '/iv-surface',
    color: 'from-accent-500 to-amber-600',
    available: true,
    features: [
      'Newton-Raphson IV solver',
      'Volatility smile analysis',
      'ATM IV tracking',
      'Put-call skew metrics',
    ],
  },
];

export default function Dashboard() {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary-600 via-primary-500 to-secondary-500 p-8 md:p-12 text-white shadow-2xl">
        <div className="absolute inset-0 bg-grid-white/10 [mask-image:linear-gradient(0deg,transparent,rgba(255,255,255,0.6))]"></div>
        <div className="relative z-10">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Welcome to QuantLab
          </h1>
          <p className="text-xl text-blue-100 max-w-2xl">
            Advanced quantitative analytics suite for portfolio optimization,
            statistical arbitrage, and derivatives pricing.
          </p>
        </div>
      </div>

      {/* Modules Grid */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Analytics Modules</h2>
          <div className="text-sm text-slate-400">
            {modules.filter((m) => m.available).length} of {modules.length} available
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((module) => {
            const Icon = module.icon;
            return (
              <div
                key={module.id}
                className={cn(
                  'group relative overflow-hidden rounded-xl border transition-all',
                  module.available
                    ? 'border-slate-700 bg-slate-800/50 hover:border-primary-500 hover:shadow-xl hover:shadow-primary-500/20'
                    : 'border-slate-800 bg-slate-900/50 opacity-60'
                )}
              >
                {/* Gradient Overlay */}
                <div
                  className={cn(
                    'absolute inset-0 opacity-0 transition-opacity',
                    module.available && 'group-hover:opacity-10',
                    `bg-gradient-to-br ${module.color}`
                  )}
                ></div>

                {/* Content */}
                <div className="relative p-6 space-y-4">
                  {/* Icon & Status */}
                  <div className="flex items-start justify-between">
                    <div
                      className={cn(
                        'p-3 rounded-lg bg-gradient-to-br',
                        module.color
                      )}
                    >
                      <Icon className="w-8 h-8 text-white" />
                    </div>
                    {!module.available && (
                      <span className="px-2 py-1 text-xs font-medium text-slate-400 bg-slate-800 rounded-full">
                        Coming Soon
                      </span>
                    )}
                  </div>

                  {/* Title & Description */}
                  <div>
                    <h3 className="text-xl font-bold text-white mb-2">
                      {module.name}
                    </h3>
                    <p className="text-sm text-slate-400">
                      {module.description}
                    </p>
                  </div>

                  {/* Features */}
                  <ul className="space-y-1.5">
                    {module.features.map((feature) => (
                      <li
                        key={feature}
                        className="flex items-center text-sm text-slate-300"
                      >
                        <div className="w-1.5 h-1.5 rounded-full bg-primary-400 mr-2"></div>
                        {feature}
                      </li>
                    ))}
                  </ul>

                  {/* Action Button */}
                  {module.available ? (
                    <Link
                      to={module.href}
                      className={cn(
                        'flex items-center justify-center w-full px-4 py-2.5 rounded-lg font-medium transition-all',
                        'bg-primary-500 text-white hover:bg-primary-600 hover:shadow-lg hover:shadow-primary-500/50'
                      )}
                    >
                      <span>Launch Module</span>
                      <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                    </Link>
                  ) : (
                    <button
                      disabled
                      className="flex items-center justify-center w-full px-4 py-2.5 rounded-lg font-medium bg-slate-800 text-slate-500 cursor-not-allowed"
                    >
                      Not Available
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
          <div className="text-3xl font-bold text-white mb-1">3</div>
          <div className="text-sm text-slate-400">Analytics Modules</div>
        </div>
        <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
          <div className="text-3xl font-bold text-white mb-1">50+</div>
          <div className="text-sm text-slate-400">Supported Tickers</div>
        </div>
        <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
          <div className="text-3xl font-bold text-white mb-1">100%</div>
          <div className="text-sm text-slate-400">Test Coverage</div>
        </div>
      </div>
    </div>
  );
}

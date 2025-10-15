import { FileText, Github, BookOpen, Code, TestTube, HelpCircle, ChevronRight, Package, Database, Zap, Shield, TrendingUp, GitBranch, Terminal, Rocket, Users, AlertCircle } from 'lucide-react';

export default function Documentation() {
  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent mb-4">
          📚 Documentation
        </h1>
        <p className="text-slate-400 text-lg max-w-3xl mx-auto">
          Complete guide to using the Quantitative Strategy & Risk Dashboard. 
          From installation to advanced usage, everything you need to get started.
        </p>
      </div>

      {/* Table of Contents */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 mb-12">
        <h2 className="text-xl font-bold text-slate-200 mb-4 flex items-center">
          <BookOpen className="w-5 h-5 mr-2 text-primary-400" />
          Table of Contents
        </h2>
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div>
            <a href="#quick-start" className="flex items-center text-slate-400 hover:text-primary-400 transition-colors py-1">
              <ChevronRight className="w-4 h-4 mr-1" /> Quick Start
            </a>
            <a href="#modules" className="flex items-center text-slate-400 hover:text-primary-400 transition-colors py-1">
              <ChevronRight className="w-4 h-4 mr-1" /> Module Guides
            </a>
            <a href="#api" className="flex items-center text-slate-400 hover:text-primary-400 transition-colors py-1">
              <ChevronRight className="w-4 h-4 mr-1" /> API Reference
            </a>
            <a href="#tech-stack" className="flex items-center text-slate-400 hover:text-primary-400 transition-colors py-1">
              <ChevronRight className="w-4 h-4 mr-1" /> Tech Stack
            </a>
          </div>
          <div>
            <a href="#testing" className="flex items-center text-slate-400 hover:text-primary-400 transition-colors py-1">
              <ChevronRight className="w-4 h-4 mr-1" /> Testing
            </a>
            <a href="#deployment" className="flex items-center text-slate-400 hover:text-primary-400 transition-colors py-1">
              <ChevronRight className="w-4 h-4 mr-1" /> Deployment
            </a>
            <a href="#faq" className="flex items-center text-slate-400 hover:text-primary-400 transition-colors py-1">
              <ChevronRight className="w-4 h-4 mr-1" /> FAQ
            </a>
            <a href="#contributing" className="flex items-center text-slate-400 hover:text-primary-400 transition-colors py-1">
              <ChevronRight className="w-4 h-4 mr-1" /> Contributing
            </a>
          </div>
        </div>
      </div>

      {/* Quick Start Section */}
      <section id="quick-start" className="mb-12 scroll-mt-20">
        <div className="bg-gradient-to-r from-primary-500/10 to-accent-500/10 border border-primary-500/30 rounded-lg p-8">
          <div className="flex items-center mb-6">
            <Rocket className="w-8 h-8 text-primary-400 mr-3" />
            <h2 className="text-3xl font-bold text-slate-200">Quick Start</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Prerequisites */}
            <div className="bg-slate-800/50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center">
                <Package className="w-5 h-5 mr-2 text-accent-400" />
                Prerequisites
              </h3>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li className="flex items-start">
                  <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-primary-400 flex-shrink-0" />
                  <span><strong>Python 3.10+</strong> (with pip)</span>
                </li>
                <li className="flex items-start">
                  <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-primary-400 flex-shrink-0" />
                  <span><strong>Node.js 16+</strong> (with npm)</span>
                </li>
                <li className="flex items-start">
                  <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-primary-400 flex-shrink-0" />
                  <span><strong>Git</strong> for version control</span>
                </li>
                <li className="flex items-start">
                  <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-primary-400 flex-shrink-0" />
                  <span><strong>4GB RAM</strong> minimum (8GB recommended)</span>
                </li>
              </ul>
            </div>

            {/* Installation */}
            <div className="bg-slate-800/50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center">
                <Terminal className="w-5 h-5 mr-2 text-green-400" />
                Installation
              </h3>
              <div className="space-y-3 text-sm">
                <div className="bg-slate-900 p-3 rounded font-mono">
                  <div className="text-slate-500"># Clone repository</div>
                  <div className="text-green-400">git clone https://github.com/yourusername/quant-dashboard.git</div>
                  <div className="text-green-400">cd quant-dashboard</div>
                </div>
                <p className="text-slate-400">
                  See <a href="https://github.com/yourusername/quant-dashboard/blob/main/GETTING_STARTED.md" target="_blank" rel="noopener noreferrer" className="text-primary-400 hover:text-primary-300">GETTING_STARTED.md</a> for detailed setup.
                </p>
              </div>
            </div>
          </div>

          {/* Backend Setup */}
          <div className="mt-6 bg-slate-800/50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-slate-200 mb-4">Backend Setup (FastAPI)</h3>
            <div className="bg-slate-900 p-4 rounded font-mono text-sm space-y-1">
              <div className="text-slate-500"># Navigate to backend</div>
              <div className="text-green-400">cd backend</div>
              <div className="text-slate-500 mt-2"># Create virtual environment</div>
              <div className="text-green-400">python -m venv .venv</div>
              <div className="text-slate-500 mt-2"># Activate (Windows)</div>
              <div className="text-green-400">.venv\Scripts\activate</div>
              <div className="text-slate-500 mt-2"># Activate (Mac/Linux)</div>
              <div className="text-green-400">source .venv/bin/activate</div>
              <div className="text-slate-500 mt-2"># Install dependencies</div>
              <div className="text-green-400">pip install -r requirements.txt</div>
              <div className="text-slate-500 mt-2"># Run server</div>
              <div className="text-green-400">uvicorn app.main:app --reload</div>
              <div className="text-slate-500 mt-2"># API runs on http://localhost:8000</div>
            </div>
          </div>

          {/* Frontend Setup */}
          <div className="mt-6 bg-slate-800/50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-slate-200 mb-4">Frontend Setup (React + Vite)</h3>
            <div className="bg-slate-900 p-4 rounded font-mono text-sm space-y-1">
              <div className="text-slate-500"># Open new terminal, navigate to frontend</div>
              <div className="text-green-400">cd frontend</div>
              <div className="text-slate-500 mt-2"># Install dependencies</div>
              <div className="text-green-400">npm install</div>
              <div className="text-slate-500 mt-2"># Run development server</div>
              <div className="text-green-400">npm run dev</div>
              <div className="text-slate-500 mt-2"># UI runs on http://localhost:5173</div>
            </div>
          </div>
        </div>
      </section>

      {/* Modules Section */}
      <section id="modules" className="mb-12 scroll-mt-20">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
          <div className="flex items-center mb-6">
            <TrendingUp className="w-8 h-8 text-primary-400 mr-3" />
            <h2 className="text-3xl font-bold text-slate-200">Module Guides</h2>
          </div>

          <div className="space-y-6">
            {/* HRP Module */}
            <div className="border-l-4 border-primary-500 pl-6 bg-slate-900/30 p-6 rounded-r-lg">
              <h3 className="text-2xl font-semibold text-slate-200 mb-3 flex items-center">
                📈 Hierarchical Risk Parity (HRP)
              </h3>
              <p className="text-slate-400 mb-4">
                Portfolio optimization using hierarchical clustering and recursive bisection. Groups assets based on correlation 
                distance to create diversified, risk-balanced portfolios.
              </p>
              
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div>
                  <h4 className="text-sm font-semibold text-primary-400 mb-2">Key Features</h4>
                  <ul className="text-sm text-slate-400 space-y-1">
                    <li>• Interactive dendrogram visualization</li>
                    <li>• Correlation heatmap with hover sync</li>
                    <li>• Multiple linkage methods</li>
                    <li>• Cluster-based asset allocation</li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-accent-400 mb-2">Algorithms</h4>
                  <ul className="text-sm text-slate-400 space-y-1">
                    <li>• Hierarchical clustering (scipy)</li>
                    <li>• Correlation distance: d = √(0.5*(1-ρ))</li>
                    <li>• Matrix seriation (optimal leaf ordering)</li>
                    <li>• Recursive bisection for weights</li>
                  </ul>
                </div>
              </div>

              <div className="bg-slate-900 p-3 rounded text-sm">
                <div className="text-slate-500 mb-1">Example Usage:</div>
                <code className="text-green-400">
                  POST /hrp/analyze → Select tickers → Choose date range → View dendrogram + heatmap
                </code>
              </div>
            </div>

            {/* StatArb Module */}
            <div className="border-l-4 border-accent-500 pl-6 bg-slate-900/30 p-6 rounded-r-lg">
              <h3 className="text-2xl font-semibold text-slate-200 mb-3 flex items-center">
                🔄 Statistical Arbitrage
              </h3>
              <p className="text-slate-400 mb-4">
                Identify cointegrated pairs for pairs trading strategies. Implements Engle-Granger cointegration testing and 
                generates trading signals based on z-score thresholds.
              </p>
              
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div>
                  <h4 className="text-sm font-semibold text-primary-400 mb-2">Key Features</h4>
                  <ul className="text-sm text-slate-400 space-y-1">
                    <li>• Cointegration testing (p-value)</li>
                    <li>• Spread analysis with z-scores</li>
                    <li>• Trading signal generation</li>
                    <li>• Hedge ratio calculation</li>
                    <li>• Half-life of mean reversion</li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-accent-400 mb-2">Algorithms</h4>
                  <ul className="text-sm text-slate-400 space-y-1">
                    <li>• Engle-Granger test (statsmodels)</li>
                    <li>• OLS regression for hedge ratio</li>
                    <li>• ADF test for stationarity</li>
                    <li>• z-score: (spread - μ) / σ</li>
                    <li>• Half-life: -ln(2) / ln(1+θ)</li>
                  </ul>
                </div>
              </div>

              <div className="bg-slate-900 p-3 rounded text-sm">
                <div className="text-slate-500 mb-1">Example Usage:</div>
                <code className="text-green-400">
                  POST /stat-arb/find-pairs → Enter tickers → Set threshold → View cointegrated pairs
                </code>
              </div>
            </div>

            {/* IV Module */}
            <div className="border-l-4 border-blue-500 pl-6 bg-slate-900/30 p-6 rounded-r-lg">
              <h3 className="text-2xl font-semibold text-slate-200 mb-3 flex items-center">
                📊 Implied Volatility Surface
              </h3>
              <p className="text-slate-400 mb-4">
                Visualize options implied volatility in 3D space across strike prices and expiration dates. Uses Black-Scholes-Merton 
                pricing with Newton-Raphson IV solver.
              </p>
              
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div>
                  <h4 className="text-sm font-semibold text-primary-400 mb-2">Key Features</h4>
                  <ul className="text-sm text-slate-400 space-y-1">
                    <li>• 3D surface plot (Plotly.js)</li>
                    <li>• Real-time options chain data</li>
                    <li>• IV metrics (ATM IV, skew, range)</li>
                    <li>• Filter by expiration & volume</li>
                    <li>• Sortable data table</li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-accent-400 mb-2">Algorithms</h4>
                  <ul className="text-sm text-slate-400 space-y-1">
                    <li>• Black-Scholes-Merton pricing</li>
                    <li>• Newton-Raphson IV solver</li>
                    <li>• Vega calculation (∂C/∂σ)</li>
                    <li>• Convergence: |BSM - market| &lt; 0.0001</li>
                    <li>• Moneyness = Strike / Spot</li>
                  </ul>
                </div>
              </div>

              <div className="bg-slate-900 p-3 rounded text-sm">
                <div className="text-slate-500 mb-1">Example Usage:</div>
                <code className="text-green-400">
                  GET /iv/surface/AAPL → Select expiration → Set min volume → View 3D surface
                </code>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* API Reference */}
      <section id="api" className="mb-12 scroll-mt-20">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
          <div className="flex items-center mb-6">
            <Code className="w-8 h-8 text-primary-400 mr-3" />
            <h2 className="text-3xl font-bold text-slate-200">API Reference</h2>
          </div>

          <div className="mb-6">
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
              <p className="text-slate-300 flex items-center">
                <AlertCircle className="w-5 h-5 mr-2 text-blue-400" />
                <span>
                  <strong>Interactive API Docs:</strong> Visit <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 underline">http://localhost:8000/docs</a> for Swagger UI with live testing
                </span>
              </p>
            </div>
          </div>

          <div className="space-y-4">
            {/* HRP Endpoints */}
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-primary-400 mb-3">HRP Module</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <div className="flex items-center mb-2">
                    <span className="bg-primary-500 text-white px-2 py-0.5 rounded text-xs font-bold mr-2">POST</span>
                    <code className="text-accent-400">/hrp/analyze</code>
                  </div>
                  <p className="text-slate-400 ml-14">Run HRP analysis on selected tickers</p>
                  <div className="ml-14 mt-2 text-slate-500">
                    <strong>Body:</strong> {`{ tickers, start_date, end_date, linkage_method }`}
                  </div>
                </div>
                <div>
                  <div className="flex items-center mb-2">
                    <span className="bg-primary-500 text-white px-2 py-0.5 rounded text-xs font-bold mr-2">POST</span>
                    <code className="text-accent-400">/hrp/correlation</code>
                  </div>
                  <p className="text-slate-400 ml-14">Get correlation matrix for tickers</p>
                  <div className="ml-14 mt-2 text-slate-500">
                    <strong>Body:</strong> {`{ tickers, start_date, end_date }`}
                  </div>
                </div>
              </div>
            </div>

            {/* StatArb Endpoints */}
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-accent-400 mb-3">StatArb Module</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <div className="flex items-center mb-2">
                    <span className="bg-primary-500 text-white px-2 py-0.5 rounded text-xs font-bold mr-2">POST</span>
                    <code className="text-accent-400">/stat-arb/test-pair</code>
                  </div>
                  <p className="text-slate-400 ml-14">Test cointegration between two tickers</p>
                  <div className="ml-14 mt-2 text-slate-500">
                    <strong>Body:</strong> {`{ ticker1, ticker2, start_date, end_date }`}
                  </div>
                </div>
                <div>
                  <div className="flex items-center mb-2">
                    <span className="bg-primary-500 text-white px-2 py-0.5 rounded text-xs font-bold mr-2">POST</span>
                    <code className="text-accent-400">/stat-arb/find-pairs</code>
                  </div>
                  <p className="text-slate-400 ml-14">Find all cointegrated pairs from list</p>
                  <div className="ml-14 mt-2 text-slate-500">
                    <strong>Body:</strong> {`{ tickers[], start_date, end_date, p_value_threshold }`}
                  </div>
                </div>
                <div>
                  <div className="flex items-center mb-2">
                    <span className="bg-primary-500 text-white px-2 py-0.5 rounded text-xs font-bold mr-2">POST</span>
                    <code className="text-accent-400">/stat-arb/spread-analysis</code>
                  </div>
                  <p className="text-slate-400 ml-14">Analyze spread with trading signals</p>
                  <div className="ml-14 mt-2 text-slate-500">
                    <strong>Body:</strong> {`{ ticker1, ticker2, start_date, end_date, entry_threshold, exit_threshold }`}
                  </div>
                </div>
              </div>
            </div>

            {/* IV Endpoints */}
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-blue-400 mb-3">IV Module</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <div className="flex items-center mb-2">
                    <span className="bg-green-500 text-white px-2 py-0.5 rounded text-xs font-bold mr-2">GET</span>
                    <code className="text-accent-400">/iv/surface/{`{ticker}`}</code>
                  </div>
                  <p className="text-slate-400 ml-14">Fetch implied volatility surface data</p>
                  <div className="ml-14 mt-2 text-slate-500">
                    <strong>Query Params:</strong> expiration_filter (first/all), min_volume (int)
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section id="tech-stack" className="mb-12 scroll-mt-20">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
          <div className="flex items-center mb-6">
            <Database className="w-8 h-8 text-primary-400 mr-3" />
            <h2 className="text-3xl font-bold text-slate-200">Tech Stack</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-900/50 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-green-400 mb-4">Backend</h3>
              <ul className="space-y-2 text-sm text-slate-400">
                <li className="flex items-center"><Zap className="w-4 h-4 mr-2 text-green-400" /> <strong>FastAPI</strong> - Async web framework</li>
                <li className="flex items-center"><Package className="w-4 h-4 mr-2 text-green-400" /> <strong>scipy</strong> - Scientific computing</li>
                <li className="flex items-center"><Package className="w-4 h-4 mr-2 text-green-400" /> <strong>statsmodels</strong> - Statistical tests</li>
                <li className="flex items-center"><Package className="w-4 h-4 mr-2 text-green-400" /> <strong>yfinance</strong> - Market data</li>
                <li className="flex items-center"><Package className="w-4 h-4 mr-2 text-green-400" /> <strong>pandas/numpy</strong> - Data processing</li>
                <li className="flex items-center"><TestTube className="w-4 h-4 mr-2 text-green-400" /> <strong>pytest</strong> - Testing framework</li>
              </ul>
            </div>

            <div className="bg-slate-900/50 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-blue-400 mb-4">Frontend</h3>
              <ul className="space-y-2 text-sm text-slate-400">
                <li className="flex items-center"><Zap className="w-4 h-4 mr-2 text-blue-400" /> <strong>React 18</strong> - UI library</li>
                <li className="flex items-center"><Code className="w-4 h-4 mr-2 text-blue-400" /> <strong>TypeScript</strong> - Type safety</li>
                <li className="flex items-center"><Zap className="w-4 h-4 mr-2 text-blue-400" /> <strong>Vite</strong> - Build tool</li>
                <li className="flex items-center"><Package className="w-4 h-4 mr-2 text-blue-400" /> <strong>D3.js</strong> - 2D visualizations</li>
                <li className="flex items-center"><Package className="w-4 h-4 mr-2 text-blue-400" /> <strong>Plotly.js</strong> - 3D surface plots</li>
                <li className="flex items-center"><Package className="w-4 h-4 mr-2 text-blue-400" /> <strong>TailwindCSS</strong> - Styling</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Testing */}
      <section id="testing" className="mb-12 scroll-mt-20">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
          <div className="flex items-center mb-6">
            <TestTube className="w-8 h-8 text-green-400 mr-3" />
            <h2 className="text-3xl font-bold text-slate-200">Testing</h2>
          </div>

          <div className="grid md:grid-cols-3 gap-4 mb-6">
            <div className="bg-slate-900/50 rounded-lg p-5 text-center">
              <div className="text-4xl font-bold text-green-400 mb-2">126</div>
              <div className="text-slate-400 text-sm">Total Tests</div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-5 text-center">
              <div className="text-4xl font-bold text-green-400 mb-2">100%</div>
              <div className="text-slate-400 text-sm">Passing Rate</div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-5 text-center">
              <div className="text-4xl font-bold text-blue-400 mb-2">3</div>
              <div className="text-slate-400 text-sm">Test Suites</div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-slate-200 mb-3">Unit Tests</h3>
              <p className="text-slate-400 text-sm mb-3">
                Test individual service functions in isolation with mocked dependencies.
              </p>
              <div className="bg-slate-900 p-3 rounded text-sm font-mono">
                <div className="text-slate-500"># Run unit tests</div>
                <div className="text-green-400">pytest tests/unit/ -v</div>
              </div>
            </div>

            <div className="bg-slate-900/50 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-slate-200 mb-3">Integration Tests</h3>
              <p className="text-slate-400 text-sm mb-3">
                Test full API endpoints with FastAPI TestClient.
              </p>
              <div className="bg-slate-900 p-3 rounded text-sm font-mono">
                <div className="text-slate-500"># Run integration tests</div>
                <div className="text-green-400">pytest tests/integration/ -v</div>
              </div>
            </div>

            <div className="bg-slate-900/50 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-slate-200 mb-3">Validation Tests</h3>
              <p className="text-slate-400 text-sm mb-3">
                Verify mathematical correctness against known academic examples.
              </p>
              <div className="bg-slate-900 p-3 rounded text-sm font-mono">
                <div className="text-slate-500"># Run validation tests</div>
                <div className="text-green-400">pytest tests/validation/ -v</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Deployment */}
      <section id="deployment" className="mb-12 scroll-mt-20">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
          <div className="flex items-center mb-6">
            <Shield className="w-8 h-8 text-primary-400 mr-3" />
            <h2 className="text-3xl font-bold text-slate-200">Deployment</h2>
          </div>

          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 mb-6">
            <p className="text-yellow-200 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2 text-yellow-400" />
              <span>
                <strong>Note:</strong> This is an MVP for educational/research purposes. For production, additional security measures are required.
              </span>
            </p>
          </div>

          <h3 className="text-xl font-semibold text-slate-200 mb-4">Production Checklist</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <ul className="space-y-2 text-sm text-slate-400">
              <li className="flex items-start">
                <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-red-400 flex-shrink-0" />
                <span><strong>Authentication:</strong> Implement JWT tokens</span>
              </li>
              <li className="flex items-start">
                <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-red-400 flex-shrink-0" />
                <span><strong>Rate Limiting:</strong> Add slowapi middleware</span>
              </li>
              <li className="flex items-start">
                <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-red-400 flex-shrink-0" />
                <span><strong>Caching:</strong> Redis for expensive calculations</span>
              </li>
              <li className="flex items-start">
                <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-red-400 flex-shrink-0" />
                <span><strong>Database:</strong> PostgreSQL for user data</span>
              </li>
            </ul>
            <ul className="space-y-2 text-sm text-slate-400">
              <li className="flex items-start">
                <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-red-400 flex-shrink-0" />
                <span><strong>Containerization:</strong> Docker + Docker Compose</span>
              </li>
              <li className="flex items-start">
                <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-red-400 flex-shrink-0" />
                <span><strong>CI/CD:</strong> GitHub Actions pipeline</span>
              </li>
              <li className="flex items-start">
                <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-red-400 flex-shrink-0" />
                <span><strong>HTTPS:</strong> SSL certificates (Let's Encrypt)</span>
              </li>
              <li className="flex items-start">
                <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-red-400 flex-shrink-0" />
                <span><strong>Monitoring:</strong> Sentry, DataDog, or similar</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="mb-12 scroll-mt-20">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
          <div className="flex items-center mb-6">
            <HelpCircle className="w-8 h-8 text-accent-400 mr-3" />
            <h2 className="text-3xl font-bold text-slate-200">Frequently Asked Questions</h2>
          </div>

          <div className="space-y-6">
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-slate-200 mb-2">What data sources are used?</h3>
              <p className="text-slate-400 text-sm">
                All market data is fetched from Yahoo Finance API via the <code className="bg-slate-900 px-2 py-1 rounded">yfinance</code> Python library. 
                This includes historical prices, options chains, and the risk-free rate (10-year Treasury). Data is fetched on-demand (no database storage).
              </p>
            </div>

            <div className="bg-slate-900/50 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-slate-200 mb-2">How accurate are the HRP allocations?</h3>
              <p className="text-slate-400 text-sm">
                HRP is a data-driven approach that depends on historical correlation estimates. Like all portfolio optimization methods, 
                past correlations may not predict future behavior. Use as one input in your investment process, not sole decision maker. 
                Backtesting and out-of-sample testing are recommended.
              </p>
            </div>

            <div className="bg-slate-900/50 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-slate-200 mb-2">What is the IV solver convergence threshold?</h3>
              <p className="text-slate-400 text-sm">
                The Newton-Raphson solver iterates until the Black-Scholes price matches the market price within 0.0001 (1¢) or 
                reaches 100 iterations. Typical convergence occurs in 5-8 iterations for liquid options. Illiquid options with wide 
                bid-ask spreads may fail to converge.
              </p>
            </div>

            <div className="bg-slate-900/50 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-slate-200 mb-2">Can I use this for live trading?</h3>
              <p className="text-slate-400 text-sm">
                <strong className="text-red-400">No.</strong> This is an educational/research tool. For live trading, you need: real-time data feeds, 
                order execution system, risk management, latency optimization, and regulatory compliance. Use this for analysis and backtesting only.
              </p>
            </div>

            <div className="bg-slate-900/50 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-slate-200 mb-2">Why do some API calls take a long time?</h3>
              <p className="text-slate-400 text-sm">
                Data fetching from Yahoo Finance can take 1-2 seconds per ticker. For batch operations (e.g., finding pairs among 20 tickers), 
                this means ~30-40 seconds total. Consider implementing caching (Redis) or using a paid data provider with faster APIs for production use.
              </p>
            </div>

            <div className="bg-slate-900/50 rounded-lg p-5">
              <h3 className="text-lg font-semibold text-slate-200 mb-2">How do I report bugs or request features?</h3>
              <p className="text-slate-400 text-sm">
                Create an issue on <a href="https://github.com/yourusername/quant-dashboard/issues" target="_blank" rel="noopener noreferrer" className="text-primary-400 hover:text-primary-300">GitHub</a>. 
                For bugs, include: steps to reproduce, expected behavior, actual behavior, and browser/OS. For features, explain the use case and benefits.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Contributing */}
      <section id="contributing" className="mb-12 scroll-mt-20">
        <div className="bg-gradient-to-r from-primary-500/10 to-accent-500/10 border border-primary-500/30 rounded-lg p-8">
          <div className="flex items-center mb-6">
            <Users className="w-8 h-8 text-primary-400 mr-3" />
            <h2 className="text-3xl font-bold text-slate-200">Contributing</h2>
          </div>

          <p className="text-slate-400 mb-6">
            Contributions are welcome! Whether it's bug fixes, new features, or documentation improvements, 
            we appreciate your help in making this project better.
          </p>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-800/50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center">
                <GitBranch className="w-5 h-5 mr-2 text-primary-400" />
                Development Workflow
              </h3>
              <ol className="space-y-2 text-sm text-slate-400">
                <li>1. Fork the repository</li>
                <li>2. Create a feature branch (<code className="bg-slate-900 px-2 py-0.5 rounded">git checkout -b feature/amazing-feature</code>)</li>
                <li>3. Make your changes</li>
                <li>4. Add tests for new functionality</li>
                <li>5. Run the test suite (<code className="bg-slate-900 px-2 py-0.5 rounded">pytest tests/ -v</code>)</li>
                <li>6. Commit your changes (<code className="bg-slate-900 px-2 py-0.5 rounded">git commit -m &apos;Add amazing feature&apos;</code>)</li>
                <li>7. Push to the branch (<code className="bg-slate-900 px-2 py-0.5 rounded">git push origin feature/amazing-feature</code>)</li>
                <li>8. Open a Pull Request</li>
              </ol>
            </div>

            <div className="bg-slate-800/50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-slate-200 mb-4">Code Standards</h3>
              <ul className="space-y-2 text-sm text-slate-400">
                <li className="flex items-start">
                  <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-primary-400 flex-shrink-0" />
                  <span><strong>Python:</strong> Follow PEP 8, use type hints</span>
                </li>
                <li className="flex items-start">
                  <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-primary-400 flex-shrink-0" />
                  <span><strong>TypeScript:</strong> Enable strict mode, use ESLint</span>
                </li>
                <li className="flex items-start">
                  <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-primary-400 flex-shrink-0" />
                  <span><strong>Testing:</strong> Aim for 80%+ coverage</span>
                </li>
                <li className="flex items-start">
                  <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-primary-400 flex-shrink-0" />
                  <span><strong>Documentation:</strong> Add docstrings and comments</span>
                </li>
                <li className="flex items-start">
                  <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-primary-400 flex-shrink-0" />
                  <span><strong>Commits:</strong> Write clear, descriptive messages</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Footer Links */}
      <div className="mt-12 text-center text-slate-500 text-sm border-t border-slate-700 pt-6">
        <div className="flex items-center justify-center space-x-6 mb-4">
          <a href="https://github.com/yourusername/quant-dashboard" target="_blank" rel="noopener noreferrer" className="hover:text-primary-400 transition-colors flex items-center">
            <Github className="w-4 h-4 mr-1" /> GitHub
          </a>
          <a href="https://github.com/yourusername/quant-dashboard/blob/main/GETTING_STARTED.md" target="_blank" rel="noopener noreferrer" className="hover:text-primary-400 transition-colors flex items-center">
            <FileText className="w-4 h-4 mr-1" /> Getting Started
          </a>
          <a href="https://github.com/yourusername/quant-dashboard/blob/main/ARCHITECTURE.md" target="_blank" rel="noopener noreferrer" className="hover:text-primary-400 transition-colors flex items-center">
            <Code className="w-4 h-4 mr-1" /> Architecture
          </a>
        </div>
        <p>Need help? Create an issue on GitHub or contact the maintainers.</p>
        <p className="mt-2">
          Built with ❤️ for quantitative finance enthusiasts | MIT License
        </p>
      </div>
    </div>
  );
}

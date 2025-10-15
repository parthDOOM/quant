import React, { useMemo, useState } from 'react';
import Plot from 'react-plotly.js';
import type Plotly from 'plotly.js';
import type { OptionContractIV } from '../types/ivSurface';

interface IVSurfaceChart3DProps {
  calls: OptionContractIV[];
  puts: OptionContractIV[];
  spotPrice: number;
}

type ChartMode = 'calls' | 'puts' | 'both';

const IVSurfaceChart3D: React.FC<IVSurfaceChart3DProps> = ({ calls, puts, spotPrice }) => {
  const [mode, setMode] = useState<ChartMode>('both');

  // Filter contracts with valid IV
  const validCalls = useMemo(
    () => calls.filter((c) => c.implied_volatility !== null),
    [calls]
  );

  const validPuts = useMemo(
    () => puts.filter((p) => p.implied_volatility !== null),
    [puts]
  );

  // Prepare data for 3D surface
  const prepareData = (contracts: OptionContractIV[]) => {
    if (contracts.length === 0) return { x: [], y: [], z: [] };

    // Sort by moneyness and time
    const sorted = [...contracts].sort((a, b) => {
      if (a.moneyness !== b.moneyness) return a.moneyness - b.moneyness;
      return a.time_to_expiry - b.time_to_expiry;
    });

    const x = sorted.map((c) => c.moneyness);
    const y = sorted.map((c) => c.time_to_expiry);
    const z = sorted.map((c) => (c.implied_volatility ?? 0) * 100); // Convert to percentage

    return { x, y, z };
  };

  const callsData = useMemo(() => prepareData(validCalls), [validCalls]);
  const putsData = useMemo(() => prepareData(validPuts), [validPuts]);

  // Create plot data
  const plotData: Array<Partial<Plotly.PlotData>> = [];

  if (mode === 'calls' || mode === 'both') {
    plotData.push({
      type: 'scatter3d',
      mode: 'markers',
      name: 'Calls',
      x: callsData.x,
      y: callsData.y,
      z: callsData.z,
      marker: {
        size: 5,
        color: callsData.z,
        colorscale: [
          [0, 'rgb(56, 189, 248)'],    // sky-400 (low IV)
          [0.5, 'rgb(34, 211, 238)'],  // cyan-400 (mid IV)
          [1, 'rgb(20, 184, 166)'],    // teal-500 (high IV)
        ],
        colorbar: {
          title: { text: 'IV (%)' },
          tickmode: 'linear',
          tick0: 0,
          dtick: 10,
          bgcolor: 'rgba(30, 41, 59, 0.8)',
          bordercolor: 'rgb(71, 85, 105)',
          borderwidth: 1,
          tickfont: {
            color: 'rgb(226, 232, 240)',
          },
        },
        showscale: mode !== 'both',
      },
      text: validCalls.map(
        (c) =>
          `Strike: $${c.strike.toFixed(2)}<br>` +
          `Moneyness: ${c.moneyness.toFixed(3)}<br>` +
          `Time: ${c.time_to_expiry.toFixed(3)} years<br>` +
          `IV: ${((c.implied_volatility ?? 0) * 100).toFixed(2)}%<br>` +
          `Volume: ${c.volume.toLocaleString()}`
      ),
      hoverinfo: 'text',
    });
  }

  if (mode === 'puts' || mode === 'both') {
    plotData.push({
      type: 'scatter3d',
      mode: 'markers',
      name: 'Puts',
      x: putsData.x,
      y: putsData.y,
      z: putsData.z,
      marker: {
        size: 5,
        color: putsData.z,
        colorscale: [
          [0, 'rgb(251, 191, 36)'],    // amber-400 (low IV)
          [0.5, 'rgb(251, 146, 60)'],  // orange-400 (mid IV)
          [1, 'rgb(239, 68, 68)'],     // red-500 (high IV)
        ],
        colorbar: {
          title: { text: 'IV (%)' },
          tickmode: 'linear',
          tick0: 0,
          dtick: 10,
          bgcolor: 'rgba(30, 41, 59, 0.8)',
          bordercolor: 'rgb(71, 85, 105)',
          borderwidth: 1,
          tickfont: {
            color: 'rgb(226, 232, 240)',
          },
        },
        showscale: mode !== 'both',
      },
      text: validPuts.map(
        (p) =>
          `Strike: $${p.strike.toFixed(2)}<br>` +
          `Moneyness: ${p.moneyness.toFixed(3)}<br>` +
          `Time: ${p.time_to_expiry.toFixed(3)} years<br>` +
          `IV: ${((p.implied_volatility ?? 0) * 100).toFixed(2)}%<br>` +
          `Volume: ${p.volume.toLocaleString()}`
      ),
      hoverinfo: 'text',
    });
  }

  const layout = {
    title: {
      text: 'Implied Volatility Surface',
      font: {
        color: 'rgb(226, 232, 240)',
        size: 18,
      },
    },
    scene: {
      xaxis: {
        title: { text: 'Moneyness (Strike / Spot)' },
        titlefont: { color: 'rgb(226, 232, 240)' },
        tickfont: { color: 'rgb(148, 163, 184)' },
        gridcolor: 'rgb(51, 65, 85)',
        backgroundcolor: 'rgb(15, 23, 42)',
      },
      yaxis: {
        title: { text: 'Time to Expiry (Years)' },
        titlefont: { color: 'rgb(226, 232, 240)' },
        tickfont: { color: 'rgb(148, 163, 184)' },
        gridcolor: 'rgb(51, 65, 85)',
        backgroundcolor: 'rgb(15, 23, 42)',
      },
      zaxis: {
        title: { text: 'Implied Volatility (%)' },
        titlefont: { color: 'rgb(226, 232, 240)' },
        tickfont: { color: 'rgb(148, 163, 184)' },
        gridcolor: 'rgb(51, 65, 85)',
        backgroundcolor: 'rgb(15, 23, 42)',
      },
      bgcolor: 'rgb(15, 23, 42)',
      camera: {
        eye: { x: 1.5, y: 1.5, z: 1.3 },
      },
    },
    paper_bgcolor: 'rgba(30, 41, 59, 0)',
    plot_bgcolor: 'rgba(30, 41, 59, 0)',
    showlegend: mode === 'both',
    legend: {
      x: 0.02,
      y: 0.98,
      bgcolor: 'rgba(30, 41, 59, 0.8)',
      bordercolor: 'rgb(71, 85, 105)',
      borderwidth: 1,
      font: {
        color: 'rgb(226, 232, 240)',
      },
    },
    margin: {
      l: 0,
      r: 0,
      b: 0,
      t: 40,
    },
    autosize: true,
  };

  const config: Partial<Plotly.Config> = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
  };

  const hasData = (mode === 'calls' && validCalls.length > 0) ||
                  (mode === 'puts' && validPuts.length > 0) ||
                  (mode === 'both' && (validCalls.length > 0 || validPuts.length > 0));

  return (
    <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl shadow-xl border border-slate-700 p-6">
      {/* Header with Mode Toggle */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-white mb-1">3D Volatility Surface</h3>
          <p className="text-sm text-slate-400">
            Interactive visualization of IV across moneyness and time
          </p>
        </div>

        {/* Mode Selector */}
        <div className="flex items-center gap-2 bg-slate-900/50 rounded-lg p-1 border border-slate-700">
          <button
            onClick={() => setMode('calls')}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${
              mode === 'calls'
                ? 'bg-teal-600 text-white shadow-lg'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
            }`}
          >
            Calls
          </button>
          <button
            onClick={() => setMode('puts')}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${
              mode === 'puts'
                ? 'bg-amber-600 text-white shadow-lg'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
            }`}
          >
            Puts
          </button>
          <button
            onClick={() => setMode('both')}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${
              mode === 'both'
                ? 'bg-indigo-600 text-white shadow-lg'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
            }`}
          >
            Both
          </button>
        </div>
      </div>

      {/* Chart */}
      {hasData ? (
        <div className="bg-slate-900/50 rounded-lg border border-slate-700 p-4">
          <Plot
            data={plotData}
            layout={layout}
            config={config}
            style={{ width: '100%', height: '600px' }}
            useResizeHandler={true}
          />

          {/* Info Box */}
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-3">
              <div className="text-slate-400 mb-1">📊 Data Points</div>
              <div className="text-white font-semibold">
                {mode === 'both'
                  ? `${validCalls.length} calls, ${validPuts.length} puts`
                  : mode === 'calls'
                  ? `${validCalls.length} contracts`
                  : `${validPuts.length} contracts`}
              </div>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-3">
              <div className="text-slate-400 mb-1">🎯 Spot Price</div>
              <div className="text-white font-semibold">${spotPrice.toFixed(2)}</div>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-3">
              <div className="text-slate-400 mb-1">💡 Controls</div>
              <div className="text-white font-semibold">Drag to rotate, scroll to zoom</div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-12 text-center">
          <div className="text-4xl mb-3">📊</div>
          <p className="text-slate-400">
            No valid IV data available for {mode === 'both' ? 'calls or puts' : mode}
          </p>
          <p className="text-xs text-slate-500 mt-2">
            Try selecting a different mode or adjusting filters
          </p>
        </div>
      )}
    </div>
  );
};

export default IVSurfaceChart3D;

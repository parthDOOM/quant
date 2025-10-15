import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Maximize2, Minimize2 } from 'lucide-react';
import type { SpreadAnalysisResponse } from '../types/api';

interface SpreadChartProps {
  data: SpreadAnalysisResponse;
}

const SpreadChart: React.FC<SpreadChartProps> = ({ data }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    if (!svgRef.current || !data.spread_data.length) return;

    // Clear previous chart
    d3.select(svgRef.current).selectAll('*').remove();

    // Dimensions - adjust based on expanded state
    const margin = { top: 20, right: 80, bottom: 60, left: 60 };
    const width = svgRef.current.clientWidth - margin.left - margin.right;
    const chartHeight = isExpanded ? 600 : 400; // Taller when expanded
    const height = chartHeight - margin.top - margin.bottom;

    // Create SVG
    const svg = d3
      .select(svgRef.current)
      .attr('width', svgRef.current.clientWidth)
      .attr('height', chartHeight)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Parse dates
    const parseDate = d3.timeParse('%Y-%m-%d');
    const spreadData = data.spread_data.map(d => ({
      ...d,
      parsedDate: parseDate(d.date)!,
    }));

    // Scales
    const xScale = d3
      .scaleTime()
      .domain(d3.extent(spreadData, d => d.parsedDate) as [Date, Date])
      .range([0, width]);

    // Better spread scale with symmetric padding
    const spreadMin = d3.min(spreadData, d => d.spread)!;
    const spreadMax = d3.max(spreadData, d => d.spread)!;
    const spreadRange = spreadMax - spreadMin;
    const spreadPadding = spreadRange * 0.15; // 15% padding
    
    const ySpreadScale = d3
      .scaleLinear()
      .domain([
        spreadMin - spreadPadding,
        spreadMax + spreadPadding,
      ])
      .range([height, 0])
      .nice(); // Round to nice numbers

    // Better z-score scale with symmetric domain around 0
    const zscoreMin = d3.min(spreadData, d => d.zscore)!;
    const zscoreMax = d3.max(spreadData, d => d.zscore)!;
    const zscoreAbsMax = Math.max(Math.abs(zscoreMin), Math.abs(zscoreMax));
    const zscorePadding = zscoreAbsMax * 0.2; // 20% padding
    
    const yZScoreScale = d3
      .scaleLinear()
      .domain([
        -(zscoreAbsMax + zscorePadding),
        zscoreAbsMax + zscorePadding,
      ])
      .range([height, 0])
      .nice();

    // Axes
    const xAxis = d3.axisBottom(xScale).ticks(8);
    const ySpreadAxis = d3.axisLeft(ySpreadScale).ticks(8);
    const yZScoreAxis = d3.axisRight(yZScoreScale).ticks(8);

    // Draw axes
    svg
      .append('g')
      .attr('transform', `translate(0,${height})`)
      .call(xAxis)
      .attr('class', 'axis')
      .selectAll('text')
      .style('fill', '#94a3b8')
      .style('font-size', '12px');

    svg
      .append('g')
      .call(ySpreadAxis)
      .attr('class', 'axis')
      .selectAll('text')
      .style('fill', '#94a3b8')
      .style('font-size', '12px');

    svg
      .append('g')
      .attr('transform', `translate(${width},0)`)
      .call(yZScoreAxis)
      .attr('class', 'axis')
      .selectAll('text')
      .style('fill', '#94a3b8')
      .style('font-size', '12px');

    // Style axis lines
    svg.selectAll('.axis path, .axis line').style('stroke', '#475569');

    // Axis labels
    svg
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left)
      .attr('x', 0 - height / 2)
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
      .style('fill', '#0ea5e9')
      .style('font-size', '12px')
      .text('Spread');

    svg
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', width + margin.right - 10)
      .attr('x', 0 - height / 2)
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
      .style('fill', '#14b8a6')
      .style('font-size', '12px')
      .text('Z-Score');

    svg
      .append('text')
      .attr('transform', `translate(${width / 2}, ${height + margin.bottom - 10})`)
      .style('text-anchor', 'middle')
      .style('fill', '#94a3b8')
      .style('font-size', '12px')
      .text('Date');

    // Threshold bands
    const thresholds = [
      { value: 2.0, color: '#ef4444', opacity: 0.1, label: 'Entry (+2σ)' },
      { value: -2.0, color: '#22c55e', opacity: 0.1, label: 'Entry (-2σ)' },
      { value: 0.0, color: '#6366f1', opacity: 0.05, label: 'Exit (0σ)' },
    ];

    thresholds.forEach(threshold => {
      svg
        .append('line')
        .attr('x1', 0)
        .attr('x2', width)
        .attr('y1', yZScoreScale(threshold.value))
        .attr('y2', yZScoreScale(threshold.value))
        .style('stroke', threshold.color)
        .style('stroke-width', 1)
        .style('stroke-dasharray', '5,5')
        .style('opacity', 0.5);

      svg
        .append('rect')
        .attr('x', 0)
        .attr('y', Math.min(yZScoreScale(threshold.value), yZScoreScale(0)))
        .attr('width', width)
        .attr('height', Math.abs(yZScoreScale(threshold.value) - yZScoreScale(0)))
        .style('fill', threshold.color)
        .style('opacity', threshold.opacity);
    });

    // Line generators
    const spreadLine = d3
      .line<typeof spreadData[0]>()
      .x(d => xScale(d.parsedDate))
      .y(d => ySpreadScale(d.spread))
      .curve(d3.curveMonotoneX);

    const zscoreLine = d3
      .line<typeof spreadData[0]>()
      .x(d => xScale(d.parsedDate))
      .y(d => yZScoreScale(d.zscore))
      .curve(d3.curveMonotoneX);

    // Draw lines
    svg
      .append('path')
      .datum(spreadData)
      .attr('fill', 'none')
      .attr('stroke', '#0ea5e9')
      .attr('stroke-width', 2)
      .attr('d', spreadLine);

    svg
      .append('path')
      .datum(spreadData)
      .attr('fill', 'none')
      .attr('stroke', '#14b8a6')
      .attr('stroke-width', 2)
      .attr('d', zscoreLine);

    // Signal markers
    const signalColors: Record<string, string> = {
      long: '#22c55e',
      short: '#ef4444',
      exit: '#94a3b8',
    };

    spreadData.forEach(d => {
      if (d.signal && d.signal !== null) {
        svg
          .append('circle')
          .attr('cx', xScale(d.parsedDate))
          .attr('cy', yZScoreScale(d.zscore))
          .attr('r', 4)
          .style('fill', signalColors[d.signal])
          .style('stroke', '#1e293b')
          .style('stroke-width', 2);
      }
    });

    // Tooltip
    const tooltip = d3.select(tooltipRef.current);

    // Overlay for mouse events
    svg
      .append('rect')
      .attr('width', width)
      .attr('height', height)
      .style('fill', 'none')
      .style('pointer-events', 'all')
      .on('mousemove', function (event) {
        const [mouseX] = d3.pointer(event);
        const date = xScale.invert(mouseX);
        const bisect = d3.bisector((d: typeof spreadData[0]) => d.parsedDate).left;
        const index = bisect(spreadData, date);
        const d = spreadData[index];

        if (d) {
          tooltip
            .style('display', 'block')
            .style('left', `${event.pageX + 10}px`)
            .style('top', `${event.pageY - 10}px`).html(`
              <div class="text-xs">
                <div class="font-semibold mb-1">${d.date}</div>
                <div class="flex items-center mb-1">
                  <span class="w-3 h-3 rounded-full bg-sky-500 mr-2"></span>
                  <span>Spread: ${d.spread.toFixed(4)}</span>
                </div>
                <div class="flex items-center mb-1">
                  <span class="w-3 h-3 rounded-full bg-teal-500 mr-2"></span>
                  <span>Z-Score: ${d.zscore.toFixed(2)}</span>
                </div>
                ${
                  d.signal
                    ? `<div class="flex items-center mt-2 pt-2 border-t border-slate-600">
                         <span class="w-3 h-3 rounded-full mr-2" style="background-color: ${signalColors[d.signal]}"></span>
                         <span class="font-semibold uppercase">${d.signal}</span>
                       </div>`
                    : ''
                }
              </div>
            `);
        }
      })
      .on('mouseout', () => {
        tooltip.style('display', 'none');
      });
  }, [data, isExpanded]);

  return (
    <div className="relative">
      {/* Expand/Collapse Button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="absolute top-0 right-0 z-10 p-2 bg-slate-700/50 hover:bg-slate-600/50 rounded-lg transition-colors group"
        title={isExpanded ? 'Collapse chart' : 'Expand chart'}
      >
        {isExpanded ? (
          <Minimize2 className="w-5 h-5 text-slate-400 group-hover:text-sky-400" />
        ) : (
          <Maximize2 className="w-5 h-5 text-slate-400 group-hover:text-sky-400" />
        )}
      </button>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-900/50 rounded-lg p-4">
          <p className="text-xs text-slate-400 mb-1">Hedge Ratio</p>
          <p className="text-lg font-semibold text-white font-mono">{data.hedge_ratio.toFixed(4)}</p>
        </div>
        <div className="bg-slate-900/50 rounded-lg p-4">
          <p className="text-xs text-slate-400 mb-1">Half-Life</p>
          <p className="text-lg font-semibold text-white font-mono">{data.half_life.toFixed(1)} days</p>
        </div>
        <div className="bg-slate-900/50 rounded-lg p-4">
          <p className="text-xs text-slate-400 mb-1">Mean Spread</p>
          <p className="text-lg font-semibold text-white font-mono">{data.statistics.mean.toFixed(4)}</p>
        </div>
        <div className="bg-slate-900/50 rounded-lg p-4">
          <p className="text-xs text-slate-400 mb-1">Spread Std Dev</p>
          <p className="text-lg font-semibold text-white font-mono">{data.statistics.std.toFixed(4)}</p>
        </div>
      </div>

      {/* Chart */}
      <div className={`transition-all duration-300 ${isExpanded ? 'ring-2 ring-sky-500/50' : ''}`}>
        <svg 
          ref={svgRef} 
          className="w-full bg-slate-900/30 rounded-lg p-4 transition-all duration-300" 
        />
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center justify-center gap-4 mt-4 text-sm">
        <div className="flex items-center">
          <div className="w-8 h-0.5 bg-sky-500 mr-2"></div>
          <span className="text-slate-300">Spread</span>
        </div>
        <div className="flex items-center">
          <div className="w-8 h-0.5 bg-teal-500 mr-2"></div>
          <span className="text-slate-300">Z-Score</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
          <span className="text-slate-300">Long Signal</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
          <span className="text-slate-300">Short Signal</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full bg-slate-400 mr-2"></div>
          <span className="text-slate-300">Exit Signal</span>
        </div>
      </div>

      {/* Tooltip */}
      <div
        ref={tooltipRef}
        className="absolute hidden bg-slate-800 border border-slate-600 rounded-lg p-3 shadow-xl pointer-events-none z-50"
        style={{ display: 'none' }}
      />
    </div>
  );
};

export default SpreadChart;

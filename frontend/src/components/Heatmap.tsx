import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import type { HeatmapCell } from '../types/api';

interface HeatmapProps {
  data: HeatmapCell[];
  tickers: string[];
  width?: number;
  height?: number;
  className?: string;
}

export default function Heatmap({
  data,
  tickers,
  width = 800,
  height = 800,
  className = '',
}: HeatmapProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data.length || !tickers.length) return;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    // Margins - increased for better label spacing
    const margin = { top: 120, right: 40, bottom: 100, left: 100 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Calculate cell size
    const cellSize = Math.min(innerWidth, innerHeight) / tickers.length;

    // Create SVG
    const svg = d3
      .select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Create scales
    const xScale = d3
      .scaleBand()
      .domain(tickers)
      .range([0, cellSize * tickers.length])
      .padding(0.05);

    const yScale = d3
      .scaleBand()
      .domain(tickers)
      .range([0, cellSize * tickers.length])
      .padding(0.05);

    // Color scale - diverging from blue (negative) through white (zero) to teal (positive)
    const colorScale = d3
      .scaleLinear<string>()
      .domain([-1, 0, 1])
      .range(['#3b82f6', '#f8fafc', '#14b8a6'])
      .clamp(true);

    // Create cells
    const cells = g
      .selectAll('.cell')
      .data(data)
      .enter()
      .append('rect')
      .attr('class', 'cell')
      .attr('x', (d) => xScale(d.x) ?? 0)
      .attr('y', (d) => yScale(d.y) ?? 0)
      .attr('width', xScale.bandwidth())
      .attr('height', yScale.bandwidth())
      .attr('fill', (d) => colorScale(d.value))
      .attr('stroke', '#1e293b')
      .attr('stroke-width', 1)
      .style('cursor', 'pointer');

    // Add text labels for correlation values
    g.selectAll('.cell-text')
      .data(data)
      .enter()
      .append('text')
      .attr('class', 'cell-text')
      .attr('x', (d) => (xScale(d.x) ?? 0) + xScale.bandwidth() / 2)
      .attr('y', (d) => (yScale(d.y) ?? 0) + yScale.bandwidth() / 2)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .style('font-size', `${Math.max(8, cellSize / 6)}px`)
      .style('font-weight', '600')
      .style('fill', (d) => {
        // Dark text for light backgrounds, light text for dark backgrounds
        return Math.abs(d.value) > 0.5 ? '#f8fafc' : '#0f172a';
      })
      .style('pointer-events', 'none')
      .text((d) => d.value.toFixed(2));

    // Add X axis labels (top)
    g.append('g')
      .attr('class', 'x-axis')
      .selectAll('.x-label')
      .data(tickers)
      .enter()
      .append('text')
      .attr('class', 'x-label')
      .attr('x', (d) => (xScale(d) ?? 0) + xScale.bandwidth() / 2)
      .attr('y', -20) // Move further up from cells
      .attr('text-anchor', 'start') // Align to start for better rotation
      .attr('transform', (d) => {
        const x = (xScale(d) ?? 0) + xScale.bandwidth() / 2;
        return `rotate(-45, ${x}, -20)`; // Match the y position
      })
      .style('font-size', '11px')
      .style('font-weight', '600')
      .style('fill', '#e2e8f0')
      .text((d) => d);

    // Add Y axis labels (left)
    g.append('g')
      .attr('class', 'y-axis')
      .selectAll('.y-label')
      .data(tickers)
      .enter()
      .append('text')
      .attr('class', 'y-label')
      .attr('x', -15) // Move further left from cells
      .attr('y', (d) => (yScale(d) ?? 0) + yScale.bandwidth() / 2)
      .attr('text-anchor', 'end')
      .attr('dominant-baseline', 'middle')
      .style('font-size', '11px')
      .style('font-weight', '600')
      .style('fill', '#e2e8f0')
      .text((d) => d);

    // Create tooltip
    const tooltip = d3
      .select('body')
      .append('div')
      .attr('class', 'heatmap-tooltip')
      .style('position', 'absolute')
      .style('visibility', 'hidden')
      .style('background-color', 'rgba(15, 23, 42, 0.95)')
      .style('color', '#e2e8f0')
      .style('padding', '12px 16px')
      .style('border-radius', '8px')
      .style('font-size', '13px')
      .style('pointer-events', 'none')
      .style('z-index', '1000')
      .style('border', '1px solid #334155')
      .style('box-shadow', '0 4px 6px rgba(0, 0, 0, 0.3)');

    // Add interactivity
    cells
      .on('mouseover', function (_event, d) {
        // Highlight cell
        d3.select(this)
          .attr('stroke', '#f59e0b')
          .attr('stroke-width', 3)
          .attr('opacity', 0.9);

        // Show tooltip
        const correlationType =
          d.value > 0.7
            ? 'Strong Positive'
            : d.value > 0.3
            ? 'Moderate Positive'
            : d.value > -0.3
            ? 'Weak'
            : d.value > -0.7
            ? 'Moderate Negative'
            : 'Strong Negative';

        const content = `
          <div style="line-height: 1.6;">
            <strong style="font-size: 14px;">${d.x} vs ${d.y}</strong><br/>
            <span style="color: ${colorScale(d.value)}; font-weight: bold; font-size: 16px;">
              ${d.value.toFixed(4)}
            </span><br/>
            <span style="color: #94a3b8; font-size: 12px;">${correlationType} Correlation</span>
          </div>
        `;

        tooltip.html(content).style('visibility', 'visible');
      })
      .on('mousemove', function (event) {
        tooltip
          .style('top', event.pageY - 10 + 'px')
          .style('left', event.pageX + 10 + 'px');
      })
      .on('mouseout', function () {
        // Reset cell style
        d3.select(this)
          .attr('stroke', '#1e293b')
          .attr('stroke-width', 1)
          .attr('opacity', 1);

        // Hide tooltip
        tooltip.style('visibility', 'hidden');
      });

    // Add color legend
    const legendWidth = 300;
    const legendHeight = 20;
    const legendX = (cellSize * tickers.length - legendWidth) / 2;
    const legendY = cellSize * tickers.length + 40;

    // Legend gradient
    const defs = svg.append('defs');
    const linearGradient = defs
      .append('linearGradient')
      .attr('id', 'legend-gradient')
      .attr('x1', '0%')
      .attr('x2', '100%');

    linearGradient
      .selectAll('stop')
      .data([
        { offset: '0%', color: '#3b82f6' },
        { offset: '50%', color: '#f8fafc' },
        { offset: '100%', color: '#14b8a6' },
      ])
      .enter()
      .append('stop')
      .attr('offset', (d) => d.offset)
      .attr('stop-color', (d) => d.color);

    const legend = g.append('g').attr('transform', `translate(${legendX},${legendY})`);

    legend
      .append('rect')
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .attr('fill', 'url(#legend-gradient)')
      .attr('stroke', '#475569')
      .attr('stroke-width', 1);

    // Legend labels
    legend
      .append('text')
      .attr('x', 0)
      .attr('y', legendHeight + 20)
      .attr('text-anchor', 'start')
      .style('font-size', '11px')
      .style('fill', '#94a3b8')
      .text('-1.00 (Negative)');

    legend
      .append('text')
      .attr('x', legendWidth / 2)
      .attr('y', legendHeight + 20)
      .attr('text-anchor', 'middle')
      .style('font-size', '11px')
      .style('fill', '#94a3b8')
      .text('0.00 (No Correlation)');

    legend
      .append('text')
      .attr('x', legendWidth)
      .attr('y', legendHeight + 20)
      .attr('text-anchor', 'end')
      .style('font-size', '11px')
      .style('fill', '#94a3b8')
      .text('1.00 (Positive)');

    // Add zoom behavior
    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 5])
      .on('zoom', (event) => {
        g.attr('transform', `translate(${margin.left},${margin.top}) ${event.transform}`);
      });

    svg.call(zoom);

    // Cleanup tooltip on unmount
    return () => {
      tooltip.remove();
    };
  }, [data, tickers, width, height]);

  return (
    <div className={`relative ${className}`}>
      <svg ref={svgRef} className="w-full h-full bg-slate-900 rounded-lg" />
      <div className="absolute top-2 right-2 text-xs text-slate-400 bg-slate-800/50 px-2 py-1 rounded">
        💡 Hover for details, scroll to zoom
      </div>
    </div>
  );
}

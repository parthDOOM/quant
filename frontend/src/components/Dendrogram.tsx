import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import type { DendrogramNode } from '../types/api';

interface DendrogramProps {
  data: DendrogramNode;
  width?: number;
  height?: number;
  className?: string;
}

export default function Dendrogram({
  data,
  width = 800,
  height = 600,
  className = '',
}: DendrogramProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data) return;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    // Margins
    const margin = { top: 40, right: 120, bottom: 40, left: 120 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Create SVG with zoom behavior
    const svg = d3
      .select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Create hierarchy from data
    const root = d3.hierarchy(data);

    // Create tree layout (top-to-bottom hierarchical)
    const treeLayout = d3
      .tree<DendrogramNode>()
      .size([innerWidth, innerHeight])
      .separation((a, b) => (a.parent === b.parent ? 1 : 2));

    // Apply layout
    treeLayout(root);

    // Create links (vertical tree paths between nodes)
    g.selectAll('.link')
      .data(root.links())
      .enter()
      .append('path')
      .attr('class', 'link')
      .attr('fill', 'none')
      .attr('stroke', '#64748b')
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0.6)
      .attr('d', (d) => {
        const sourceX = d.source.x ?? 0;
        const sourceY = d.source.y ?? 0;
        const targetX = d.target.x ?? 0;
        const targetY = d.target.y ?? 0;
        // Vertical tree: draw from parent (top) to child (bottom)
        return `M${sourceX},${sourceY}
                C${sourceX},${(sourceY + targetY) / 2}
                 ${targetX},${(sourceY + targetY) / 2}
                 ${targetX},${targetY}`;
      });

    // Create nodes (circles) - vertical tree layout (x, y)
    const node = g
      .selectAll('.node')
      .data(root.descendants())
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', (d) => `translate(${d.x},${d.y})`);

    // Add circles for nodes
    node
      .append('circle')
      .attr('r', (d) => (d.children ? 5 : 7))
      .attr('fill', (d) => {
        if (!d.children) {
          // Leaf nodes - color by ticker
          return '#0ea5e9'; // Primary blue
        }
        // Internal nodes - color by height
        const maxHeight = root.data.height || 1;
        const normalizedHeight = d.data.height / maxHeight;
        return d3.interpolate('#14b8a6', '#f59e0b')(normalizedHeight);
      })
      .attr('stroke', '#1e293b')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer');

    // Add labels for leaf nodes (ticker names) - positioned below nodes for vertical tree
    node
      .filter((d) => !d.children)
      .append('text')
      .attr('dy', 20)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('font-weight', '600')
      .style('fill', '#e2e8f0')
      .text((d) => d.data.name);

    // Add height labels for internal nodes
    node
      .filter((d) => Boolean(d.children && d.children.length > 0))
      .append('text')
      .attr('dy', -10)
      .attr('text-anchor', 'middle')
      .style('font-size', '10px')
      .style('fill', '#94a3b8')
      .text((d) => d.data.height.toFixed(2));

    // Add tooltips
    const tooltip = d3
      .select('body')
      .append('div')
      .attr('class', 'dendrogram-tooltip')
      .style('position', 'absolute')
      .style('visibility', 'hidden')
      .style('background-color', 'rgba(15, 23, 42, 0.95)')
      .style('color', '#e2e8f0')
      .style('padding', '8px 12px')
      .style('border-radius', '6px')
      .style('font-size', '12px')
      .style('pointer-events', 'none')
      .style('z-index', '1000')
      .style('border', '1px solid #334155');

    node
      .on('mouseover', function (_event, d) {
        // Highlight node
        d3.select(this).select('circle').attr('r', d.children ? 8 : 10);

        // Show tooltip
        const content = d.children
          ? `<strong>Cluster Node</strong><br/>Height: ${d.data.height.toFixed(3)}<br/>Members: ${d.leaves().length}`
          : `<strong>${d.data.name}</strong><br/>Leaf Node`;

        tooltip.html(content).style('visibility', 'visible');
      })
      .on('mousemove', function (event) {
        tooltip
          .style('top', event.pageY - 10 + 'px')
          .style('left', event.pageX + 10 + 'px');
      })
      .on('mouseout', function (_event, d) {
        // Reset node size
        d3.select(this)
          .select('circle')
          .attr('r', d.children ? 5 : 7);

        // Hide tooltip
        tooltip.style('visibility', 'hidden');
      });

    // Add zoom behavior
    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    // Cleanup tooltip on unmount
    return () => {
      tooltip.remove();
    };
  }, [data, width, height]);

  return (
    <div className={`relative ${className}`}>
      <svg ref={svgRef} className="w-full h-full bg-slate-900 rounded-lg" />
      <div className="absolute top-2 right-2 text-xs text-slate-400 bg-slate-800/50 px-2 py-1 rounded">
        💡 Scroll to zoom, drag to pan
      </div>
    </div>
  );
}

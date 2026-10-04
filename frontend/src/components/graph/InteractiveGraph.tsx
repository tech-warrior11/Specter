import React, { useState, useEffect } from 'react';
import { SubGraph, GraphNode } from '../../types';
import { ZoomIn, ZoomOut, RefreshCw, ShieldAlert, Cpu, HardDrive, Globe, User, Terminal } from 'lucide-react';
import { ComposableMap, ZoomableGroup, Geographies, Geography } from 'react-simple-maps';

interface InteractiveGraphProps {
  subgraph: SubGraph;
  onNodeClick?: (node: GraphNode) => void;
  selectedNodeId?: string;
  height?: string;
}

export const InteractiveGraph: React.FC<InteractiveGraphProps> = ({
  subgraph,
  onNodeClick,
  selectedNodeId,
  height = '500px'
}) => {
  const [zoom, setZoom] = useState(1);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  useEffect(() => {
    if (selectedNodeId && subgraph.nodes.length > 0) {
      const node = subgraph.nodes.find(n => n.id === selectedNodeId);
      if (node) setSelectedNode(node);
    }
  }, [selectedNodeId, subgraph]);

  // Node Colors by Entity Type
  const getNodeColor = (nodeId: string, label: string) => {
    if (nodeId.toLowerCase().includes('hacker') || nodeId.toLowerCase().includes('malicious') || nodeId.toLowerCase().includes('attacker')) {
      return { bg: 'bg-red-500/30', border: 'border-red-500', text: 'text-red-400', icon: ShieldAlert };
    }
    
    switch (label.toLowerCase()) {
      case 'user': return { bg: 'bg-[#111]', border: 'border-[#00ff9d]', text: 'text-[#00ff9d]', icon: User };
      case 'host': return { bg: 'bg-blue-500/20', border: 'border-blue-500', text: 'text-blue-400', icon: Cpu };
      case 'ip': return { bg: 'bg-emerald-500/20', border: 'border-emerald-500', text: 'text-emerald-400', icon: Globe };
      case 'process': return { bg: 'bg-amber-500/20', border: 'border-amber-500', text: 'text-amber-400', icon: Terminal };
      case 'file': return { bg: 'bg-purple-500/20', border: 'border-purple-500', text: 'text-purple-400', icon: HardDrive };
      case 'alert': return { bg: 'bg-rose-500/20', border: 'border-rose-500', text: 'text-rose-400', icon: ShieldAlert };
      default: return { bg: 'bg-cyan-500/20', border: 'border-cyan-500', text: 'text-cyan-400', icon: Globe };
    }
  };

  // Compute Layout Coordinates in a force-directed circular ring
  const numNodes = subgraph.nodes.length;
  const radius = Math.min(220, Math.max(120, numNodes * 25));
  const centerX = 380; // ComposableMap width/2
  const centerY = 240; // ComposableMap height/2

  const nodePositions: Record<string, { x: number; y: number }> = {};
  subgraph.nodes.forEach((node, i) => {
    const angle = (i / Math.max(1, numNodes)) * 2 * Math.PI;
    nodePositions[node.id] = {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle)
    };
  });

  return (
    <div className="relative w-full rounded-none bg-[#050505] border border-[#333] overflow-hidden" style={{ height }}>
      {/* Control Overlay */}
      <div className="absolute top-4 left-4 z-20 flex items-center gap-1.5 p-1.5 rounded-none bg-[#0a0a0a] border border-[#333]">
        <button
          onClick={() => setZoom(z => Math.min(5, z + 0.25))}
          className="p-1.5 rounded-none hover:bg-[#111] text-[#888] hover:text-slate-200 transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => setZoom(z => Math.max(0.5, z - 0.25))}
          className="p-1.5 rounded-none hover:bg-[#111] text-[#888] hover:text-slate-200 transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={() => setZoom(1)}
          className="p-1.5 rounded-none hover:bg-[#111] text-[#888] hover:text-slate-200 transition-colors"
          title="Reset View"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <div className="absolute top-4 right-4 z-20 flex items-center gap-3 px-3 py-1.5 rounded-none bg-[#0a0a0a] border border-[#333] text-xs font-mono text-[#888]">
        <span>Nodes: <strong className="text-slate-200">{subgraph.nodes.length}</strong></span>
        <span>•</span>
        <span>Edges: <strong className="text-slate-200">{subgraph.edges.length}</strong></span>
      </div>

      <div className="w-full h-full cursor-grab active:cursor-grabbing">
        <ComposableMap
          projection="geoMercator"
          width={760}
          height={480}
          style={{ width: "100%", height: "100%" }}
        >
          <ZoomableGroup zoom={zoom} minZoom={0.5} maxZoom={10} onMoveEnd={({ zoom: newZoom }) => setZoom(newZoom)}>
            <Geographies geography="/features.json">
              {({ geographies }) =>
                geographies.map((geo) => (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    fill="rgba(6, 182, 212, 0.05)"
                    stroke="#06b6d4"
                    strokeWidth={0.8}
                    className="outline-none hover:fill-[rgba(6,182,212,0.2)] focus:outline-none transition-colors duration-300"
                  />
                ))
              }
            </Geographies>

            {/* Custom SVG Definitions */}
            <defs>
              <marker
                id="arrowhead"
                markerWidth="8"
                markerHeight="6"
                refX="18"
                refY="3"
                orient="auto"
              >
                <polygon points="0 0, 8 3, 0 6" fill="#00ff9d" opacity="0.8" />
              </marker>
            </defs>

            {/* Edges */}
            {subgraph.edges.map((edge, idx) => {
              const src = nodePositions[edge.source];
              const tgt = nodePositions[edge.target];
              if (!src || !tgt) return null;

              const midX = (src.x + tgt.x) / 2;
              const midY = (src.y + tgt.y) / 2;

              return (
                <g key={edge.id || idx}>
                  <line
                    x1={src.x}
                    y1={src.y}
                    x2={tgt.x}
                    y2={tgt.y}
                    stroke="#333"
                    strokeWidth="1.5"
                    strokeDasharray="4 2"
                    markerEnd="url(#arrowhead)"
                  />
                  <text
                    x={midX}
                    y={midY - 4}
                    fill="#888"
                    fontSize="6"
                    textAnchor="middle"
                    fontFamily="monospace"
                    className="select-none"
                  >
                    {edge.relation_type}
                  </text>
                </g>
              );
            })}

            {/* Nodes */}
            {subgraph.nodes.map((node) => {
              const pos = nodePositions[node.id];
              if (!pos) return null;
              const isSelected = selectedNode?.id === node.id;
              const color = getNodeColor(node.id, node.label);

              return (
                <g
                  key={node.id}
                  transform={`translate(${pos.x}, ${pos.y})`}
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedNode(node);
                    onNodeClick?.(node);
                  }}
                  className="cursor-pointer group"
                >
                  <circle
                    r={isSelected ? 16 : 12}
                    className={`transition-all ${isSelected ? 'fill-[#00ff9d]/20 stroke-[#00ff9d] stroke-2' : 'fill-[#111] stroke-[#333] stroke-1 group-hover:stroke-[#00ff9d]'}`}
                  />
                  <circle
                    r={6}
                    className={`${color.bg} ${color.border} stroke-1`}
                  />
                  <text
                    y={22}
                    fill={isSelected ? '#00ff9d' : '#ccc'}
                    fontSize="8"
                    fontWeight={isSelected ? '600' : '400'}
                    textAnchor="middle"
                    fontFamily="monospace"
                    className="select-none"
                  >
                    {node.id.length > 18 ? `${node.id.substring(0, 16)}...` : node.id}
                  </text>
                  <text
                    y={32}
                    fill="#888"
                    fontSize="6"
                    textAnchor="middle"
                    className="select-none uppercase"
                  >
                    {node.label}
                  </text>
                </g>
              );
            })}
          </ZoomableGroup>
        </ComposableMap>
      </div>

      {/* Selected Node Details Drawer */}
      {selectedNode && (
        <div className="absolute bottom-4 right-4 z-20 w-80 p-4 rounded-none bg-[#0a0a0a] border border-[#333] shadow-none">
          <div className="flex items-center justify-between border-b border-[#333] pb-2 mb-3">
            <span className="text-[11px] font-mono text-[#00ff9d] uppercase font-bold tracking-wider">
              {selectedNode.label} Entity
            </span>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-xs text-slate-500 hover:text-[#ccc]"
            >
              ✕
            </button>
          </div>
          <div className="space-y-2 text-xs">
            <div>
              <span className="text-[#555] text-[10px] block uppercase">Identifier</span>
              <span className="font-mono text-[#eee] font-semibold break-all">{selectedNode.id}</span>
            </div>
            {Object.entries(selectedNode.properties || {}).map(([k, v]) => (
              <div key={k} className="flex justify-between items-center py-1 border-t border-[#222]">
                <span className="text-[#555] text-[10px] uppercase font-mono">{k}</span>
                <span className="text-[#ccc] font-mono text-[11px]">{String(v)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

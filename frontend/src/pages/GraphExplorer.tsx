import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { SubGraph, AttackPath, GraphNode } from '../types';
import { InteractiveGraph } from '../components/graph/InteractiveGraph';
import { Network, Search, ArrowRight, ShieldCheck, Flame, Cpu, Filter } from 'lucide-react';

export const GraphExplorer: React.FC = () => {
  const [rootEntity, setRootEntity] = useState('user:testuser');
  const [depth, setDepth] = useState(2);
  const [subgraph, setSubgraph] = useState<SubGraph>({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(false);
  const [pathSource, setPathSource] = useState('ip:198.51.100.25');
  const [pathTarget, setPathTarget] = useState('file:/etc/shadow');
  const [attackPath, setAttackPath] = useState<AttackPath | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  const loadGraph = async () => {
    setLoading(true);
    try {
      const data = await api.getNeighborhood(rootEntity, depth);
      setSubgraph(data);
    } catch (err) {
      console.error('Failed to load neighborhood graph:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleComputePath = async () => {
    try {
      const pathData = await api.getAttackPath(pathSource, pathTarget);
      setAttackPath(pathData);
      setSubgraph({ nodes: pathData.nodes, edges: pathData.edges });
    } catch (err) {
      console.error('Failed to compute attack path:', err);
    }
  };

  useEffect(() => {
    loadGraph();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Network className="w-5 h-5 text-cyan-400" />
            <span>Interactive Security Graph Explorer</span>
          </h1>
          <p className="text-xs text-[#888] mt-1">
            Traverse entity relationships, compute shortest attack paths, and analyze asset blast radius.
          </p>
        </div>
      </div>

      {/* Exploration Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Neighborhood Expansion */}
        <div className="p-4 rounded-none bg-[#0a0a0a] border border-[#333] space-y-3">
          <div className="text-xs font-semibold text-slate-200 flex items-center gap-2">
            <Search className="w-4 h-4 text-cyan-400" />
            <span>Neighborhood Expansion</span>
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={rootEntity}
              onChange={(e) => setRootEntity(e.target.value)}
              placeholder="e.g. user:alice or host:LAB-PC-01"
              className="flex-1 px-3 py-2 rounded-none bg-[#050505] border border-slate-700 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
            />
            <select
              value={depth}
              onChange={(e) => setDepth(Number(e.target.value))}
              className="px-3 py-2 rounded-none bg-[#050505] border border-slate-700 text-xs font-mono text-[#ccc]"
            >
              <option value={1}>1-Hop</option>
              <option value={2}>2-Hops</option>
              <option value={3}>3-Hops</option>
            </select>
            <button
              onClick={loadGraph}
              disabled={loading}
              className="px-4 py-2 rounded-none bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs font-mono transition-all"
            >
              Explore
            </button>
          </div>
        </div>

        {/* Shortest Attack Path Search */}
        <div className="p-4 rounded-none bg-[#0a0a0a] border border-[#333] space-y-3">
          <div className="text-xs font-semibold text-slate-200 flex items-center gap-2">
            <Flame className="w-4 h-4 text-rose-400" />
            <span>Attack Path Calculator</span>
          </div>
          <div className="flex gap-2 items-center">
            <input
              type="text"
              value={pathSource}
              onChange={(e) => setPathSource(e.target.value)}
              placeholder="Source Entity"
              className="flex-1 px-3 py-2 rounded-none bg-[#050505] border border-slate-700 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
            />
            <ArrowRight className="w-4 h-4 text-slate-500 shrink-0" />
            <input
              type="text"
              value={pathTarget}
              onChange={(e) => setPathTarget(e.target.value)}
              placeholder="Target Entity"
              className="flex-1 px-3 py-2 rounded-none bg-[#050505] border border-slate-700 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
            />
            <button
              onClick={handleComputePath}
              className="px-4 py-2 rounded-none bg-rose-500 hover:bg-rose-400 text-slate-950 font-bold text-xs font-mono transition-all shrink-0"
            >
              Trace Path
            </button>
          </div>
        </div>
      </div>

      {/* Main Visual Graph Canvas */}
      <InteractiveGraph
        subgraph={subgraph}
        height="540px"
        onNodeClick={(node) => setSelectedNode(node)}
      />

      {/* Attack Path Narrative (if calculated) */}
      {attackPath && (
        <div className="p-5 rounded-none bg-[#0a0a0a] border border-rose-500/30">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs font-bold text-rose-400 uppercase font-mono tracking-wider">
              Attack Path Reconstructed: {attackPath.path_id}
            </h3>
            <span className="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
              Risk Score: {attackPath.risk_score}/100 ({Math.round(attackPath.confidence * 100)}% Confidence)
            </span>
          </div>
          <p className="text-xs text-[#ccc] leading-relaxed mb-3">{attackPath.description}</p>
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-mono text-slate-500">Stage Sequence:</span>
            {attackPath.stage_progression.map((stage, i) => (
              <span key={i} className="px-2.5 py-1 rounded bg-[#050505] border border-[#333] text-cyan-400 font-mono text-[11px] font-semibold">
                {stage}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

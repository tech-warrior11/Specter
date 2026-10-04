import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { DashboardSummary } from '../types';
import {
  ShieldAlert, Activity, Network, FolderSearch, Zap, ShieldCheck
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await api.getDashboardSummary();
        setSummary(data);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center text-[#00ff9d] font-mono animate-pulse uppercase tracking-widest text-sm">
        Initializing Specter Core Subsystems...
      </div>
    );
  }

  const kpis = summary?.kpis || {
    total_events: 0, total_alerts: 0, open_investigations: 0,
    open_incidents: 0, anomalies_detected: 0, active_iocs: 0,
    graph_nodes: 0, graph_edges: 0
  };

  return (
    <div className="space-y-6 font-mono text-sm max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="p-6 bg-[#0a0a0a] border border-[#333] flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-xl font-bold text-white tracking-widest uppercase">Command Center</h1>
            <span className="px-2 py-0.5 text-[10px] bg-[#00ff9d]/10 text-[#00ff9d] border border-[#00ff9d]/30 uppercase tracking-widest flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 bg-[#00ff9d] rounded-full animate-pulse"></span>
              Live
            </span>
          </div>
          <p className="text-xs text-[#888] max-w-2xl uppercase tracking-wide">
            Monitoring active threat streams, behavioral anomalies, and orchestrating multi-stage defensive responses across the network.
          </p>
        </div>

        <Link
          to="/scenarios"
          className="px-4 py-2 bg-white text-black hover:bg-[#00ff9d] font-bold text-xs uppercase tracking-widest transition-colors flex items-center gap-2"
        >
          <Zap className="w-4 h-4 fill-black" />
          <span>Launch Sim</span>
        </Link>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Processed', value: kpis.total_events.toLocaleString(), sub: 'Events' },
          { label: 'Detections', value: kpis.total_alerts, sub: 'Actionable Alerts' },
          { label: 'Operations', value: kpis.open_investigations, sub: 'Investigations' },
          { label: 'Entities', value: kpis.graph_nodes, sub: `${kpis.graph_edges} Edges` }
        ].map((stat, i) => (
          <div key={i} className="p-5 bg-[#0a0a0a] border border-[#333] hover:border-[#555] transition-colors relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-[#333] group-hover:bg-[#00ff9d] transition-colors"></div>
            <span className="text-[10px] font-bold text-[#666] uppercase tracking-widest block mb-2">{stat.label}</span>
            <div className="text-2xl font-bold text-white mb-1 tracking-wider">{stat.value}</div>
            <div className="text-[10px] text-[#444] uppercase font-bold tracking-widest">{stat.sub}</div>
          </div>
        ))}
      </div>

      {/* High-Risk Entities & MITRE Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* High-Risk Entities */}
        <div className="p-6 bg-[#0a0a0a] border border-[#333]">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-[#222]">
            <h2 className="text-sm font-bold text-white uppercase tracking-widest flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#00ff9d]" /> Threat Vectors
            </h2>
            <Link to="/entities" className="text-[10px] font-bold text-[#888] hover:text-[#00ff9d] uppercase tracking-widest transition-colors">Directory &rarr;</Link>
          </div>
          <div className="space-y-3">
            {(summary?.high_risk_entities || []).slice(0, 5).map((ent) => (
              <div key={ent.id} className="p-3 bg-[#111] border border-[#222] flex items-center justify-between hover:border-[#444] transition-colors">
                <div className="flex items-center gap-3">
                  <span className="text-[9px] font-bold px-2 py-0.5 bg-[#222] text-[#888] uppercase tracking-widest">
                    {ent.type}
                  </span>
                  <span className="text-xs font-bold text-[#ccc] truncate max-w-[150px]">{ent.value}</span>
                </div>
                <div className="text-right">
                  <div className="text-xs font-bold text-[#ff4444]">{ent.risk_score}/100</div>
                  <div className="text-[9px] text-[#666] uppercase font-bold tracking-widest mt-0.5">{ent.criticality}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* MITRE ATT&CK Tactic Distribution */}
        <div className="p-6 bg-[#0a0a0a] border border-[#333]">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-[#222]">
            <h2 className="text-sm font-bold text-white uppercase tracking-widest flex items-center gap-2">
              <Activity className="w-4 h-4 text-[#00ff9d]" /> Tactics (ATT&CK)
            </h2>
            <Link to="/mitre" className="text-[10px] font-bold text-[#888] hover:text-[#00ff9d] uppercase tracking-widest transition-colors">Matrix &rarr;</Link>
          </div>
          <div className="space-y-5">
            {(summary?.mitre_distribution || []).map((m) => {
              const percent = Math.min(100, m.count * 20);
              return (
                <div key={m.tactic} className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[#ccc] font-bold uppercase tracking-wider">{m.tactic}</span>
                    <span className="text-[#00ff9d] font-bold text-[10px]">{m.count} ALERTS</span>
                  </div>
                  <div className="flex gap-[2px] w-full h-3">
                    {Array.from({ length: 100 }).map((_, i) => (
                      <div 
                        key={i} 
                        className={`flex-1 h-full ${i < percent ? 'bg-[#00ff9d]' : 'bg-[#1a1a1a]'}`} 
                      />
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

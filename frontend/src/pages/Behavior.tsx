import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  Activity, 
  Search, 
  Filter, 
  Users, 
  Server, 
  TrendingUp, 
  AlertTriangle,
  Clock,
  ChevronRight
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Behavior: React.FC = () => {
  const navigate = useNavigate();
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadAnomalies();
  }, []);

  const loadAnomalies = async () => {
    setLoading(true);
    try {
      const data = await api.getAnomalies();
      setAnomalies(data);
    } catch (err) {
      console.error('Failed to load anomalies:', err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = anomalies.filter(a => {
    const matchSearch = a.entity_id.toLowerCase().includes(search.toLowerCase()) ||
      a.anomaly_type.toLowerCase().includes(search.toLowerCase()) ||
      a.description.toLowerCase().includes(search.toLowerCase());
    return matchSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Activity className="w-7 h-7 text-amber-400" />
            Behavioral Baselines & Statistical Anomaly Engine
          </h1>
          <p className="text-sm text-[#888] mt-1">
            Deterministic user and asset behavioral profiling, off-hours login detection, and rare execution clustering.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-none bg-[#0a0a0a] border border-[#333] text-xs font-mono text-[#ccc]">
            Detected Deviations: <strong className="text-amber-400">{anomalies.length}</strong>
          </span>
        </div>
      </div>

      {/* Profiling Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-4 space-y-2">
          <div className="text-xs font-semibold text-[#888] uppercase tracking-wider">Baseline Window</div>
          <div className="text-xl font-bold font-mono text-slate-100">14-Day Rolling</div>
          <p className="text-[11px] text-slate-500">Continuous statistical profiling of login hours & normal processes.</p>
        </div>
        <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-4 space-y-2">
          <div className="text-xs font-semibold text-[#888] uppercase tracking-wider">Detection Mode</div>
          <div className="text-xl font-bold font-mono text-amber-400">Statistical (Z-Score)</div>
          <p className="text-[11px] text-slate-500">Flagging deviations &gt; 3.0σ from baseline activity curves.</p>
        </div>
        <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-4 space-y-2">
          <div className="text-xs font-semibold text-[#888] uppercase tracking-wider">Profiled Entities</div>
          <div className="text-xl font-bold font-mono text-white">Users & Endpoints</div>
          <p className="text-[11px] text-slate-500">Entity clustering based on normal subnets and working hours.</p>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-4">
        <div className="relative w-full">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search anomalies by entity identity, type (off_hours, rare_process, spike), or description..."
            className="w-full bg-[#050505] border border-[#333] rounded-none pl-10 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500"
          />
        </div>
      </div>

      {/* Anomalies Table */}
      <div className="bg-[#0a0a0a] border border-[#333] rounded-none overflow-hidden">
        <div className="p-4 border-b border-[#333] flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            Observed Behavioral Deviations ({filtered.length})
          </h2>
          <span className="text-xs text-slate-500 font-mono">Status: Advisory</span>
        </div>

        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-12 text-center text-slate-500 font-mono text-xs animate-pulse">
              Computing entity baseline variance...
            </div>
          ) : filtered.length === 0 ? (
            <div className="p-12 text-center text-slate-500 text-xs">
              No behavioral anomalies detected in current baseline window.
            </div>
          ) : (
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-[#050505] text-[#888] font-medium uppercase tracking-wider border-b border-[#333]">
                <tr>
                  <th className="p-3">Entity</th>
                  <th className="p-3">Anomaly Type</th>
                  <th className="p-3">Deviation Explanation</th>
                  <th className="p-3 text-right">Confidence</th>
                  <th className="p-3 text-right">Detected At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {filtered.map((a, idx) => (
                  <tr key={idx} className="hover:bg-[#111] transition-colors">
                    <td className="p-3 font-semibold text-white">
                      {a.entity_id}
                    </td>
                    <td className="p-3 font-sans">
                      <span className="px-2 py-0.5 rounded bg-amber-950/80 text-amber-400 border border-amber-800 text-[10px] font-mono font-bold uppercase">
                        {a.anomaly_type}
                      </span>
                    </td>
                    <td className="p-3 text-[#ccc] font-sans max-w-md">
                      {a.description}
                    </td>
                    <td className="p-3 text-right text-emerald-400">
                      {Math.round((a.confidence || 0.8) * 100)}%
                    </td>
                    <td className="p-3 text-right text-slate-500 font-sans">
                      {new Date(a.detected_at).toLocaleTimeString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

import React, { useState } from 'react';
import { api } from '../services/api';
import { Search, Terminal, Filter, ArrowRight, FolderPlus, Database, Clock, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const ThreatHunting: React.FC = () => {
  const [query, setQuery] = useState('source_ip = "198.51.100.25"');
  const [timeWindow, setTimeWindow] = useState(48);
  const [results, setResults] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const data = await api.searchHunt(query, timeWindow);
      setResults(data);
    } catch (err) {
      console.error('Hunt search failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePivot = (pivotVal: string) => {
    if (pivotVal.startsWith('ip:')) {
      setQuery(`source_ip = "${pivotVal.replace('ip:', '')}"`);
    } else if (pivotVal.startsWith('user:')) {
      setQuery(`user = "${pivotVal.replace('user:', '')}"`);
    } else if (pivotVal.startsWith('host:')) {
      setQuery(`host = "${pivotVal.replace('host:', '')}"`);
    }
  };

  const handleCreateInvestigation = async () => {
    if (!results || results.events.length === 0) return;
    try {
      const evIds = results.events.map((e: any) => e.id);
      const res = await api.createInvestigation({
        title: `Threat Hunt Case: ${query.substring(0, 40)}`,
        priority: 'HIGH',
        summary: `Assembled from proactive threat hunt query: ${query}`,
        related_events: evIds,
        root_entities: results.suggested_pivots.slice(0, 3)
      });
      navigate(`/investigations/${res.id}`);
    } catch (err) {
      console.error('Failed to create investigation case:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Terminal className="w-5 h-5 text-cyan-400" />
            <span>Threat Hunting DSL Engine</span>
          </h1>
          <p className="text-xs text-[#888] mt-1">
            Proactively query disparate telemetry with boolean logic, string matching, and multi-entity pivoting.
          </p>
        </div>
      </div>

      {/* Query Bar */}
      <form onSubmit={handleSearch} className="p-4 rounded-none bg-[#0a0a0a] border border-[#333] space-y-3">
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-cyan-400">
              <Search className="w-4 h-4" />
            </div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder='e.g. source_ip = "10.10.10.50" AND severity >= "medium"'
              className="w-full pl-10 pr-4 py-2.5 rounded-none bg-[#050505] border border-slate-700/80 text-xs font-mono text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          <div className="flex items-center gap-2">
            <select
              value={timeWindow}
              onChange={(e) => setTimeWindow(Number(e.target.value))}
              className="px-3 py-2.5 rounded-none bg-[#050505] border border-slate-700/80 text-xs font-mono text-[#ccc] focus:outline-none focus:border-cyan-500"
            >
              <option value={24}>Last 24 Hours</option>
              <option value={48}>Last 48 Hours</option>
              <option value={168}>Last 7 Days</option>
            </select>

            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2.5 rounded-none bg-[#0a0a0a]   hover: hover: text-slate-950 font-bold text-xs font-mono transition-all flex items-center gap-2 shadow-none shadow-cyan-500/20"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              <span>Execute Hunt</span>
            </button>
          </div>
        </div>

        {/* Quick Query Templates */}
        <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] text-[#888]">
          <span className="font-mono text-slate-500">Templates:</span>
          <button
            type="button"
            onClick={() => setQuery('source_ip = "198.51.100.25" AND severity = "high"')}
            className="px-2 py-0.5 rounded bg-[#111] hover:bg-slate-700 text-cyan-400 font-mono text-[10px]"
          >
            External IP High Severity
          </button>
          <button
            type="button"
            onClick={() => setQuery('process = "powershell.exe" AND user = "testuser"')}
            className="px-2 py-0.5 rounded bg-[#111] hover:bg-slate-700 text-cyan-400 font-mono text-[10px]"
          >
            PowerShell by Account
          </button>
          <button
            type="button"
            onClick={() => setQuery('action = "login_failed"')}
            className="px-2 py-0.5 rounded bg-[#111] hover:bg-slate-700 text-cyan-400 font-mono text-[10px]"
          >
            All Failed Logins
          </button>
        </div>
      </form>

      {/* Suggested Pivots & Action Bar */}
      {results && (
        <div className="p-4 rounded-none bg-[#0a0a0a] border border-[#333] flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs text-[#888] font-medium">Available Pivots:</span>
            {(results.suggested_pivots || []).map((pivot: string) => (
              <button
                key={pivot}
                onClick={() => handlePivot(pivot)}
                className="px-2.5 py-1 rounded-none bg-[#111] hover:bg-cyan-500/20 hover:text-cyan-400 hover:border-cyan-500/30 border border-slate-700 text-[#ccc] font-mono text-[11px] transition-all flex items-center gap-1.5"
              >
                <span>{pivot}</span>
                <ArrowRight className="w-3 h-3 text-cyan-400" />
              </button>
            ))}
          </div>

          <button
            onClick={handleCreateInvestigation}
            className="px-3.5 py-1.5 rounded-none bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 text-cyan-300 text-xs font-mono font-semibold transition-all flex items-center gap-2"
          >
            <FolderPlus className="w-4 h-4" />
            <span>Assemble Investigation Case</span>
          </button>
        </div>
      )}

      {/* Results Table */}
      {results && (
        <div className="rounded-none bg-[#0a0a0a] border border-[#333] overflow-hidden">
          <div className="p-4 border-b border-[#333] flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-200">
              Matched Telemetry ({results.total_matches} events)
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-[#050505] text-[#888] border-b border-[#333] text-[11px]">
                <tr>
                  <th className="p-3">Timestamp</th>
                  <th className="p-3">Source</th>
                  <th className="p-3">Event Type</th>
                  <th className="p-3">Action</th>
                  <th className="p-3">User / Host</th>
                  <th className="p-3">Source IP</th>
                  <th className="p-3">Severity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-[#ccc]">
                {(results.events || []).map((ev: any) => (
                  <tr key={ev.id} className="hover:bg-[#111] transition-colors">
                    <td className="p-3 text-[#888]">{new Date(ev.timestamp).toLocaleTimeString()}</td>
                    <td className="p-3 text-[#888]">{ev.source}</td>
                    <td className="p-3 uppercase text-cyan-400/90">{ev.event_type}</td>
                    <td className="p-3 font-semibold text-slate-200">{ev.action}</td>
                    <td className="p-3">{ev.user || ev.host || '-'}</td>
                    <td className="p-3 text-emerald-400">{ev.source_ip || '-'}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold ${
                        ev.severity === 'high' || ev.severity === 'critical'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                          : 'bg-[#111] text-[#888]'
                      }`}>
                        {ev.severity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

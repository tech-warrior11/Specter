import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  Flame, 
  Search, 
  Filter, 
  ShieldCheck, 
  AlertCircle, 
  Clock, 
  ChevronRight,
  UserCheck
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Incidents: React.FC = () => {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  useEffect(() => {
    loadIncidents();
  }, []);

  const loadIncidents = async () => {
    setLoading(true);
    try {
      const data = await api.getIncidents();
      setIncidents(data);
    } catch (err) {
      console.error('Failed to load incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityBadge = (s: string) => {
    switch (s?.toUpperCase()) {
      case 'CRITICAL': return 'bg-rose-950/80 text-rose-400 border border-rose-800';
      case 'HIGH': return 'bg-amber-950/80 text-amber-400 border border-amber-800';
      case 'MEDIUM': return 'bg-yellow-950/80 text-yellow-400 border border-yellow-800';
      default: return 'bg-[#111] text-[#888] border border-slate-700';
    }
  };

  const getStatusBadge = (s: string) => {
    switch (s?.toUpperCase()) {
      case 'OPEN': return 'bg-rose-950 text-rose-400 border border-rose-800';
      case 'INVESTIGATING': return 'bg-amber-950 text-amber-400 border border-amber-800';
      case 'CONTAINED': return 'bg-sky-950 text-white border border-sky-800';
      case 'RECOVERY': return 'bg-[#111] text-[#00ff9d] border border-[#00ff9d]';
      case 'CLOSED': return 'bg-emerald-950 text-emerald-400 border border-emerald-800';
      default: return 'bg-[#111] text-[#888]';
    }
  };

  const filtered = incidents.filter(inc => {
    const matchSearch = inc.title.toLowerCase().includes(search.toLowerCase()) || 
      (inc.summary && inc.summary.toLowerCase().includes(search.toLowerCase()));
    const matchStatus = statusFilter === 'ALL' || inc.status.toUpperCase() === statusFilter;
    return matchSearch && matchStatus;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Flame className="w-7 h-7 text-rose-500" />
            Security Incident Response Management
          </h1>
          <p className="text-sm text-[#888] mt-1">
            Confirmed incident lifecycle tracking, affected asset blast radiuses, and containment execution.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-none bg-[#0a0a0a] border border-[#333] text-xs font-mono text-[#ccc]">
            Active Incidents: <strong className="text-rose-400">{incidents.length}</strong>
          </span>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-4 flex flex-col md:flex-row items-center gap-4">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search active incidents, root causes, or affected hosts..."
            className="w-full bg-[#050505] border border-[#333] rounded-none pl-10 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-rose-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="w-4 h-4 text-[#888]" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-[#ccc] focus:outline-none focus:border-rose-500"
          >
            <option value="ALL">All Incident Statuses</option>
            <option value="OPEN">Open</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="CONTAINED">Contained</option>
            <option value="RECOVERY">Recovery</option>
            <option value="CLOSED">Closed</option>
          </select>
        </div>
      </div>

      {/* Incident Cards */}
      <div className="grid grid-cols-1 gap-4">
        {loading ? (
          <div className="p-12 text-center text-slate-500 font-mono text-xs animate-pulse">
            Loading active incident catalog...
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-xs bg-[#0a0a0a] rounded-none border border-[#333]">
            No confirmed incidents match filter criteria.
          </div>
        ) : (
          filtered.map((inc) => (
            <div
              key={inc.id}
              className="bg-[#0a0a0a] border border-[#333] rounded-none p-5 hover:border-rose-500/50 transition-all flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
            >
              <div className="space-y-2 flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-mono text-xs font-bold text-rose-400 bg-rose-950/60 border border-rose-900 px-2 py-0.5 rounded">
                    {inc.id}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${getSeverityBadge(inc.severity)}`}>
                    {inc.severity}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${getStatusBadge(inc.status)}`}>
                    {inc.status}
                  </span>
                  <span className="font-mono text-xs font-bold text-amber-400 bg-amber-950/40 border border-amber-900 px-2 py-0.5 rounded">
                    Risk: {inc.risk_score}/100
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-100">
                  {inc.title}
                </h3>

                <p className="text-xs text-[#888] leading-relaxed max-w-3xl">
                  {inc.summary || 'Correlated high-confidence security event requiring incident responder containment actions.'}
                </p>

                <div className="flex items-center gap-4 text-xs font-mono text-slate-500 pt-1">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" />
                    {new Date(inc.created_at).toLocaleString()}
                  </span>
                  <span className="flex items-center gap-1">
                    <UserCheck className="w-3.5 h-3.5" />
                    Assigned: {inc.assigned_to || 'SOC Incident Team'}
                  </span>
                </div>
              </div>

              <div className="flex md:flex-col items-end gap-2 w-full md:w-auto">
                <button
                  onClick={() => navigate(`/investigations`)}
                  className="px-4 py-2 bg-[#111] hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-none text-xs font-medium flex items-center justify-center gap-1.5 transition-colors w-full md:w-auto whitespace-nowrap"
                >
                  <span>View Case Evidence</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

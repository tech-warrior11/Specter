import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { InvestigationItem } from '../types';
import { 
  FolderLock, 
  Plus, 
  Search, 
  Filter, 
  ShieldAlert, 
  ExternalLink,
  ChevronRight,
  Clock,
  Layers
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Investigations: React.FC = () => {
  const navigate = useNavigate();
  const [investigations, setInvestigations] = useState<InvestigationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState('ALL');

  // Modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newPriority, setNewPriority] = useState('HIGH');
  const [newSummary, setNewSummary] = useState('');
  const [newEntities, setNewEntities] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadInvestigations();
  }, []);

  const loadInvestigations = async () => {
    setLoading(true);
    try {
      const data = await api.getInvestigations();
      setInvestigations(data);
    } catch (err) {
      console.error('Failed to load investigations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle) return;
    setCreating(true);
    try {
      const rootEntities = newEntities.split(',').map(s => s.trim()).filter(Boolean);
      const res = await api.createInvestigation({
        title: newTitle,
        priority: newPriority,
        summary: newSummary,
        root_entities: rootEntities
      });
      setShowCreateModal(false);
      navigate(`/investigations/${res.id}`);
    } catch (err) {
      console.error('Failed to create case:', err);
    } finally {
      setCreating(false);
    }
  };

  const getPriorityBadge = (p: string) => {
    switch (p.toUpperCase()) {
      case 'CRITICAL': return 'bg-rose-950/80 text-rose-400 border border-rose-800';
      case 'HIGH': return 'bg-amber-950/80 text-amber-400 border border-amber-800';
      case 'MEDIUM': return 'bg-yellow-950/80 text-yellow-400 border border-yellow-800';
      default: return 'bg-[#111] text-[#888] border border-slate-700';
    }
  };

  const getStatusBadge = (s: string) => {
    switch (s.toUpperCase()) {
      case 'OPEN': return 'bg-sky-950 text-white border border-sky-800';
      case 'INVESTIGATING': return 'bg-[#111] text-[#00ff9d] border border-[#00ff9d]';
      case 'CLOSED': return 'bg-[#111] text-slate-500 border border-slate-700';
      default: return 'bg-[#111] text-[#888] border border-slate-700';
    }
  };

  const filtered = investigations.filter(inv => {
    const matchSearch = inv.title.toLowerCase().includes(search.toLowerCase()) ||
      (inv.summary && inv.summary.toLowerCase().includes(search.toLowerCase())) ||
      inv.id.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === 'ALL' || inv.status.toUpperCase() === statusFilter;
    const matchPri = priorityFilter === 'ALL' || inv.priority.toUpperCase() === priorityFilter;
    return matchSearch && matchStatus && matchPri;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <FolderLock className="w-7 h-7 text-[#00ff9d]" />
            Security Investigation Cases
          </h1>
          <p className="text-sm text-[#888] mt-1">
            Grounded attack-chain dossiers, interactive subgraphs, evidence management, and automated security stories.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-[#111] hover:bg-[#111] text-white rounded-none text-xs font-semibold flex items-center gap-2 transition-colors shadow-none shadow-indigo-950/40"
          >
            <Plus className="w-4 h-4" />
            New Investigation Case
          </button>
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
            placeholder="Search investigation cases by title, ID, or root entity..."
            className="w-full bg-[#050505] border border-[#333] rounded-none pl-10 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-[#00ff9d]"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="w-4 h-4 text-[#888]" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-[#ccc] focus:outline-none focus:border-[#00ff9d]"
          >
            <option value="ALL">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="CLOSED">Closed</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-[#ccc] focus:outline-none focus:border-[#00ff9d]"
          >
            <option value="ALL">All Priorities</option>
            <option value="CRITICAL">Critical Priority</option>
            <option value="HIGH">High Priority</option>
            <option value="MEDIUM">Medium Priority</option>
            <option value="LOW">Low Priority</option>
          </select>
        </div>
      </div>

      {/* Investigation Cases Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {loading ? (
          <div className="col-span-full p-12 text-center text-slate-500 font-mono text-xs animate-pulse">
            Loading investigation cases workbench...
          </div>
        ) : filtered.length === 0 ? (
          <div className="col-span-full p-12 text-center text-slate-500 text-xs">
            No investigation cases match your filter criteria.
          </div>
        ) : (
          filtered.map((inv) => (
            <div
              key={inv.id}
              onClick={() => navigate(`/investigations/${inv.id}`)}
              className="bg-[#0a0a0a] border border-[#333] hover:border-[#00ff9d] rounded-none p-5 flex flex-col justify-between space-y-4 cursor-pointer transition-all hover:shadow-none hover:shadow-indigo-950/20 group"
            >
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${getPriorityBadge(inv.priority)}`}>
                      {inv.priority}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${getStatusBadge(inv.status)}`}>
                      {inv.status}
                    </span>
                  </div>
                  <span className="font-mono text-xs font-bold text-amber-400 bg-amber-950/40 border border-amber-900/50 px-2 py-0.5 rounded">
                    Risk: {inv.risk_score}/100
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-100 group-hover:text-[#00ff9d] transition-colors line-clamp-1">
                  {inv.title}
                </h3>
                
                <p className="text-xs text-[#888] line-clamp-2">
                  {inv.summary || 'Security investigation initiated from correlated telemetry and alert indicators.'}
                </p>
              </div>

              <div className="space-y-3 pt-3 border-t border-[#333]">
                {/* Root Entities */}
                <div className="flex items-center gap-1.5 flex-wrap">
                  {inv.root_entities && inv.root_entities.slice(0, 3).map((ent, idx) => (
                    <span key={idx} className="px-1.5 py-0.5 bg-[#050505] border border-[#333] rounded font-mono text-[10px] text-[#ccc] truncate max-w-[120px]">
                      {ent}
                    </span>
                  ))}
                  {inv.root_entities && inv.root_entities.length > 3 && (
                    <span className="text-[10px] text-slate-500 font-mono">
                      +{inv.root_entities.length - 3} more
                    </span>
                  )}
                </div>

                {/* Footer stats */}
                <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                  <div className="flex items-center gap-3">
                    <span>Alerts: <strong className="text-[#ccc]">{inv.alerts_count || 0}</strong></span>
                    <span>Events: <strong className="text-[#ccc]">{inv.events_count || 0}</strong></span>
                  </div>
                  <div className="flex items-center gap-1 text-[#00ff9d] group-hover:translate-x-0.5 transition-transform">
                    <span>Open Workbench</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form onSubmit={handleCreate} className="bg-[#0a0a0a] border border-[#333] rounded-none max-w-lg w-full p-6 space-y-4 shadow-none">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <FolderLock className="w-5 h-5 text-[#00ff9d]" />
              Create Investigation Dossier
            </h3>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-[#ccc] mb-1">Case Title</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g., Investigation: Suspicious Administrative Access on LAB-PC-01"
                  className="w-full bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-[#00ff9d]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#ccc] mb-1">Priority</label>
                <select
                  value={newPriority}
                  onChange={(e) => setNewPriority(e.target.value)}
                  className="w-full bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-[#00ff9d]"
                >
                  <option value="CRITICAL">Critical</option>
                  <option value="HIGH">High</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="LOW">Low</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#ccc] mb-1">Root Entities (comma-separated)</label>
                <input
                  type="text"
                  value={newEntities}
                  onChange={(e) => setNewEntities(e.target.value)}
                  placeholder="e.g., USER:alice, HOST:LAB-PC-01, IP:10.10.10.50"
                  className="w-full bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-[#00ff9d] font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#ccc] mb-1">Initial Summary / Hypothesis</label>
                <textarea
                  rows={3}
                  value={newSummary}
                  onChange={(e) => setNewSummary(e.target.value)}
                  placeholder="Describe observed trigger conditions, initial alerts, and hypothesis..."
                  className="w-full bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-[#00ff9d]"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-[#333]">
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="px-3 py-1.5 rounded-none text-xs text-[#888] hover:text-slate-200 bg-[#111] hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={creating}
                className="px-4 py-1.5 rounded-none text-xs font-semibold text-white bg-[#111] hover:bg-[#111] disabled:opacity-50"
              >
                {creating ? 'Initializing...' : 'Create & Open Workbench'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

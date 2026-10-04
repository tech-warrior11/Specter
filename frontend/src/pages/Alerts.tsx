import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { AlertItem } from '../types';
import { 
  ShieldAlert, 
  Filter, 
  Search, 
  CheckCircle2, 
  XCircle, 
  FolderPlus, 
  ExternalLink,
  Layers,
  Clock,
  ChevronRight
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Alerts: React.FC = () => {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [selectedAlert, setSelectedAlert] = useState<AlertItem | null>(null);

  // False positive modal state
  const [showFpModal, setShowFpModal] = useState(false);
  const [fpReason, setFpReason] = useState('Authorized maintenance');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const data = await api.getAlerts();
      setAlerts(data);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (alertId: string, newStatus: string, reason?: string) => {
    setActionLoading(true);
    try {
      await api.updateAlertStatus(alertId, newStatus, reason);
      await loadAlerts();
      if (selectedAlert?.id === alertId) {
        setSelectedAlert(prev => prev ? { ...prev, status: newStatus } : null);
      }
      setShowFpModal(false);
    } catch (err) {
      console.error('Failed to update alert status:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCreateInvestigation = async (alert: AlertItem) => {
    try {
      const res = await api.createInvestigation({
        title: `Investigation: ${alert.title}`,
        priority: alert.severity.toUpperCase() === 'CRITICAL' ? 'CRITICAL' : 'HIGH',
        root_entities: alert.entity_ids,
        related_alerts: [alert.id],
        summary: `Escalated from detection alert: ${alert.description}`
      });
      navigate(`/investigations/${res.id}`);
    } catch (err) {
      console.error('Failed to create investigation:', err);
    }
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev.toLowerCase()) {
      case 'critical': return 'bg-rose-950/80 text-rose-400 border border-rose-800';
      case 'high': return 'bg-amber-950/80 text-amber-400 border border-amber-800';
      case 'medium': return 'bg-yellow-950/80 text-yellow-400 border border-yellow-800';
      default: return 'bg-[#111] text-[#888] border border-slate-700';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case 'NEW': return 'bg-sky-950 text-white border border-sky-800';
      case 'INVESTIGATING': return 'bg-[#111] text-[#00ff9d] border border-[#00ff9d]';
      case 'RESOLVED': return 'bg-emerald-950 text-emerald-400 border border-emerald-800';
      case 'FALSE_POSITIVE': return 'bg-[#111] text-slate-500 border border-slate-700';
      default: return 'bg-[#111] text-[#888] border border-slate-700';
    }
  };

  const filtered = alerts.filter(a => {
    const matchSearch = a.title.toLowerCase().includes(search.toLowerCase()) || 
      a.description.toLowerCase().includes(search.toLowerCase()) ||
      (a.mitre_tactic && a.mitre_tactic.toLowerCase().includes(search.toLowerCase()));
    const matchSev = severityFilter === 'ALL' || a.severity.toUpperCase() === severityFilter;
    const matchStat = statusFilter === 'ALL' || a.status.toUpperCase() === statusFilter;
    return matchSearch && matchSev && matchStat;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <ShieldAlert className="w-7 h-7 text-rose-400" />
            Detection Alerts & Triage Queue
          </h1>
          <p className="text-sm text-[#888] mt-1">
            Real-time multi-stage security detections with MITRE ATT&CK correlation, confidence scoring, and case escalation.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-none bg-[#0a0a0a] border border-[#333] text-xs font-mono text-[#ccc]">
            Active Alerts: <strong className="text-rose-400">{alerts.length}</strong>
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
            placeholder="Search alerts by title, description, rule ID, or MITRE tactic..."
            className="w-full bg-[#050505] border border-[#333] rounded-none pl-10 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="w-4 h-4 text-[#888]" />
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-[#ccc] focus:outline-none focus:border-sky-500"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical Severity</option>
            <option value="HIGH">High Severity</option>
            <option value="MEDIUM">Medium Severity</option>
            <option value="LOW">Low Severity</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-[#ccc] focus:outline-none focus:border-sky-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="NEW">New</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="RESOLVED">Resolved</option>
            <option value="FALSE_POSITIVE">False Positive</option>
          </select>
        </div>
      </div>

      {/* Grid Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Alerts Table */}
        <div className="lg:col-span-2 bg-[#0a0a0a] border border-[#333] rounded-none overflow-hidden flex flex-col">
          <div className="p-4 border-b border-[#333] flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <Layers className="w-4 h-4 text-rose-400" />
              Triage Queue ({filtered.length})
            </h2>
            <span className="text-xs text-slate-500">Live correlation pipeline</span>
          </div>

          <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
            {loading ? (
              <div className="p-8 text-center text-slate-500 font-mono text-xs animate-pulse">
                Fetching correlated alerts...
              </div>
            ) : filtered.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                No alerts match the selected filters.
              </div>
            ) : (
              <div className="divide-y divide-slate-800/60 font-sans">
                {filtered.map((alert) => {
                  const isSelected = selectedAlert?.id === alert.id;
                  return (
                    <div
                      key={alert.id}
                      onClick={() => setSelectedAlert(alert)}
                      className={`p-4 hover:bg-[#111] cursor-pointer transition-colors flex items-start justify-between gap-4 ${
                        isSelected ? 'bg-sky-950/20 border-l-2 border-sky-400' : ''
                      }`}
                    >
                      <div className="space-y-1.5 flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${getSeverityBadge(alert.severity)}`}>
                            {alert.severity.toUpperCase()}
                          </span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${getStatusBadge(alert.status)}`}>
                            {alert.status}
                          </span>
                          {alert.mitre_tactic && (
                            <span className="px-2 py-0.5 rounded bg-[#111] border border-[#00ff9d] text-[#00ff9d] text-[10px] font-mono">
                              {alert.mitre_tactic} {alert.mitre_technique ? `• ${alert.mitre_technique}` : ''}
                            </span>
                          )}
                        </div>
                        <h3 className="text-sm font-semibold text-slate-200 truncate">
                          {alert.title}
                        </h3>
                        <p className="text-xs text-[#888] line-clamp-1">
                          {alert.description}
                        </p>
                        <div className="flex items-center gap-4 text-[11px] text-slate-500 font-mono">
                          <span>Events: <strong className="text-[#ccc]">{alert.event_ids.length}</strong></span>
                          <span>Confidence: <strong className="text-white">{Math.round(alert.confidence * 100)}%</strong></span>
                          <span>Risk: <strong className="text-amber-400">{alert.risk_score}/100</strong></span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {new Date(alert.created_at).toLocaleTimeString()}
                          </span>
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-600 shrink-0 self-center" />
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Selected Alert Details */}
        <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-5 flex flex-col space-y-4">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2 border-b border-[#333] pb-3">
            <ShieldAlert className="w-4 h-4 text-rose-400" />
            Alert Detail & Response
          </h2>

          {selectedAlert ? (
            <div className="space-y-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2 py-0.5 rounded text-xs font-bold ${getSeverityBadge(selectedAlert.severity)}`}>
                    {selectedAlert.severity.toUpperCase()}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${getStatusBadge(selectedAlert.status)}`}>
                    {selectedAlert.status}
                  </span>
                </div>
                <h3 className="text-base font-bold text-slate-100">
                  {selectedAlert.title}
                </h3>
                <p className="text-xs text-[#888] mt-1">
                  {selectedAlert.description}
                </p>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-2.5 rounded bg-[#050505] border border-[#333]">
                  <div className="text-[10px] text-slate-500">Risk Score</div>
                  <div className="text-amber-400 font-bold text-sm mt-0.5">{selectedAlert.risk_score} / 100</div>
                </div>
                <div className="p-2.5 rounded bg-[#050505] border border-[#333]">
                  <div className="text-[10px] text-slate-500">Rule Confidence</div>
                  <div className="text-white font-bold text-sm mt-0.5">{Math.round(selectedAlert.confidence * 100)}%</div>
                </div>
              </div>

              {/* MITRE ATT&CK */}
              {selectedAlert.mitre_tactic && (
                <div className="p-3 rounded-none bg-[#111] border border-[#00ff9d] space-y-1">
                  <div className="text-[11px] font-semibold text-[#00ff9d] uppercase tracking-wider">MITRE ATT&CK Mapping</div>
                  <div className="text-xs text-slate-200 font-mono">
                    {selectedAlert.mitre_tactic} ({selectedAlert.mitre_technique || 'N/A'})
                  </div>
                </div>
              )}

              {/* Involved Entities */}
              <div>
                <div className="text-xs font-semibold text-[#888] mb-2">Involved Entities ({selectedAlert.entity_ids.length})</div>
                <div className="flex flex-wrap gap-1.5">
                  {selectedAlert.entity_ids.map((ent, idx) => (
                    <span key={idx} className="px-2 py-1 bg-[#050505] border border-[#333] rounded font-mono text-[11px] text-[#ccc]">
                      {ent}
                    </span>
                  ))}
                </div>
              </div>

              {/* Associated Events */}
              <div>
                <div className="text-xs font-semibold text-[#888] mb-2">Evidence Events ({selectedAlert.event_ids.length})</div>
                <div className="space-y-1 max-h-32 overflow-y-auto">
                  {selectedAlert.event_ids.map((evt, idx) => (
                    <div key={idx} className="p-1.5 rounded bg-[#050505] border border-[#333] font-mono text-[11px] text-[#888]">
                      {evt}
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-3 border-t border-[#333] space-y-2">
                <button
                  onClick={() => handleCreateInvestigation(selectedAlert)}
                  className="w-full py-2.5 px-3 bg-rose-600 hover:bg-rose-500 text-white rounded-none text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow-none shadow-rose-950/40"
                >
                  <FolderPlus className="w-4 h-4" />
                  Escalate to Investigation Case
                </button>

                <div className="grid grid-cols-2 gap-2">
                  <button
                    disabled={actionLoading || selectedAlert.status === 'RESOLVED'}
                    onClick={() => handleStatusChange(selectedAlert.id, 'RESOLVED')}
                    className="py-2 px-2 bg-emerald-950/40 hover:bg-emerald-900/50 border border-emerald-800 text-emerald-400 rounded-none text-xs font-medium flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Resolve Alert
                  </button>

                  <button
                    disabled={actionLoading || selectedAlert.status === 'FALSE_POSITIVE'}
                    onClick={() => setShowFpModal(true)}
                    className="py-2 px-2 bg-[#111] hover:bg-slate-700 text-[#ccc] border border-slate-700 rounded-none text-xs font-medium flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50"
                  >
                    <XCircle className="w-3.5 h-3.5 text-rose-400" />
                    Mark False Positive
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-slate-500">
              <ShieldAlert className="w-10 h-10 text-slate-700 mb-2" />
              <p className="text-xs">Select a detection alert from the triage queue to inspect telemetry, evidence events, and escalation options.</p>
            </div>
          )}
        </div>
      </div>

      {/* False Positive Modal */}
      {showFpModal && selectedAlert && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-[#0a0a0a] border border-[#333] rounded-none max-w-md w-full p-5 space-y-4 shadow-none">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <XCircle className="w-4 h-4 text-rose-400" />
              Classify as False Positive
            </h3>
            <p className="text-xs text-[#888]">
              Audited classification for alert <strong className="text-slate-200">"{selectedAlert.title}"</strong>. This reason will be logged for detection tuning analytics.
            </p>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-[#ccc]">Select Justification</label>
              <select
                value={fpReason}
                onChange={(e) => setFpReason(e.target.value)}
                className="w-full bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
              >
                <option value="Expected admin activity">Expected admin activity</option>
                <option value="Known scanner / security probe">Known scanner / security probe</option>
                <option value="Lab automation / CI runner">Lab automation / CI runner</option>
                <option value="Authorized maintenance window">Authorized maintenance window</option>
                <option value="Synthetic test benchmark">Synthetic test benchmark</option>
              </select>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setShowFpModal(false)}
                className="px-3 py-1.5 rounded-none text-xs text-[#888] hover:text-slate-200 bg-[#111] hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={() => handleStatusChange(selectedAlert.id, 'FALSE_POSITIVE', fpReason)}
                className="px-3 py-1.5 rounded-none text-xs font-semibold text-white bg-rose-600 hover:bg-rose-500"
              >
                Confirm False Positive
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

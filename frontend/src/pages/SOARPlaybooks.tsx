import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { ShieldAlert, ShieldCheck, Play, RotateCcw, Send, CheckCircle2, AlertTriangle, Zap, Server, Lock, UserX, Cpu } from 'lucide-react';

export const SOARPlaybooks: React.FC = () => {
  const [playbooks, setPlaybooks] = useState<any[]>([]);
  const [actions, setActions] = useState<any[]>([]);
  const [webhooks, setWebhooks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionType, setActionType] = useState('BLOCK_IP');
  const [target, setTarget] = useState('');
  const [reason, setReason] = useState('');
  const [executing, setExecuting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [webhookUrl, setWebhookUrl] = useState('https://hooks.slack.com/services/DEMO/WEBHOOK');
  const [testingWebhook, setTestingWebhook] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [pbks, acts, whs] = await Promise.all([
        api.getSOARPlaybooks().catch(() => []),
        api.getSOARActions().catch(() => []),
        api.getWebhooks().catch(() => [])
      ]);
      setPlaybooks(pbks);
      setActions(acts);
      setWebhooks(whs);
    } catch (err) {
      console.error('Failed to load SOAR data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteAction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!target) return;
    setExecuting(true);
    setSuccessMsg(null);
    try {
      const res = await api.executeSOARAction({
        action_type: actionType,
        target: target.trim(),
        reason: reason || 'Manual SOC containment triggered from Active Defense workbench'
      });
      setSuccessMsg(`✅ Containment Deployed: ${res.execution_output?.message || res.action_type}`);
      setTarget('');
      setReason('');
      await loadData();
    } catch (err: any) {
      alert(`Execution failed: ${err.message}`);
    } finally {
      setExecuting(false);
    }
  };

  const handleRollback = async (actionId: string) => {
    if (!confirm('Are you sure you want to lift this containment rule?')) return;
    try {
      await api.rollbackSOARAction(actionId);
      await loadData();
    } catch (err: any) {
      alert(`Rollback failed: ${err.message}`);
    }
  };

  const handleTestWebhook = async () => {
    setTestingWebhook(true);
    try {
      const res = await api.testWebhook({
        url: webhookUrl,
        webhook_type: 'SLACK',
        message: '🚨 Specter X Alert: Critical APT Attack Chain Blocked by Automated SOAR Playbook!'
      });
      alert(`Webhook Test Status: ${res.status}`);
    } catch (err: any) {
      alert(`Webhook test error: ${err.message}`);
    } finally {
      setTestingWebhook(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <ShieldAlert className="w-7 h-7 text-red-400" />
            SOAR Active Defense & Containment Engine
          </h1>
          <p className="text-[#888] text-sm mt-1">
            Automated threat containment playbooks, 1-click endpoint isolation, perimeter firewall drop rules & webhooks.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Active Response Online
          </span>
        </div>
      </div>

      {successMsg && (
        <div className="p-4 rounded-none bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 flex items-center justify-between">
          <span className="text-sm font-medium">{successMsg}</span>
          <button onClick={() => setSuccessMsg(null)} className="text-xs text-emerald-400 hover:underline">Dismiss</button>
        </div>
      )}

      {/* Grid: 1-Click Containment & Notification Webhooks */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Action Dispatcher */}
        <div className="lg:col-span-2 bg-[#0d1322] border border-[#333] rounded-none p-6 shadow-none relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-[#0a0a0a]   "></div>
          <h2 className="text-lg font-semibold text-slate-100 mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-400" />
            Instant Containment Action Dispatcher
          </h2>

          <form onSubmit={handleExecuteAction} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-[#888] mb-1">Containment Strategy</label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: 'BLOCK_IP', label: 'Block IP', icon: Lock },
                    { id: 'ISOLATE_HOST', label: 'Isolate Host', icon: Server },
                    { id: 'DISABLE_USER', label: 'Revoke User', icon: UserX },
                    { id: 'KILL_PROCESS', label: 'Kill Process', icon: Cpu }
                  ].map((act) => {
                    const Icon = act.icon;
                    const isSelected = actionType === act.id;
                    return (
                      <button
                        key={act.id}
                        type="button"
                        onClick={() => setActionType(act.id)}
                        className={`p-3 rounded-none border text-left flex items-center gap-2 transition-all ${
                          isSelected
                            ? 'bg-red-500/10 border-red-500 text-red-300 font-semibold'
                            : 'bg-[#0a0a0a] border-[#333] text-[#888] hover:border-slate-700'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                        <span className="text-xs">{act.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-[#888] mb-1">
                  Target Identifier ({actionType === 'BLOCK_IP' ? 'IP Address' : actionType === 'ISOLATE_HOST' ? 'Hostname' : actionType === 'DISABLE_USER' ? 'Username' : 'Process Name'})
                </label>
                <input
                  type="text"
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  placeholder={
                    actionType === 'BLOCK_IP' ? 'e.g. 198.51.100.25' :
                    actionType === 'ISOLATE_HOST' ? 'e.g. LAB-PC-01' :
                    actionType === 'DISABLE_USER' ? 'e.g. testuser' : 'e.g. powershell.exe'
                  }
                  required
                  className="w-full bg-[#0a0a0a] border border-slate-700 rounded-none px-3 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-red-500"
                />

                <label className="block text-xs font-medium text-[#888] mt-3 mb-1">SOC Justification / Reason</label>
                <input
                  type="text"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="e.g. Active C2 beaconing observed during multi-stage incident"
                  className="w-full bg-[#0a0a0a] border border-slate-700 rounded-none px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-red-500"
                />
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                type="submit"
                disabled={executing || !target}
                className="px-5 py-2.5 rounded-none bg-red-600 hover:bg-red-500 text-white font-medium text-sm flex items-center gap-2 transition-all shadow-none shadow-red-600/20 disabled:opacity-50"
              >
                {executing ? <RotateCcw className="w-4 h-4 animate-spin" /> : <ShieldAlert className="w-4 h-4" />}
                {executing ? 'Deploying Rule...' : 'Deploy Immediate Containment'}
              </button>
            </div>
          </form>
        </div>

        {/* Live Webhook Notifications Channel */}
        <div className="bg-[#0d1322] border border-[#333] rounded-none p-6 shadow-none flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-100 mb-2 flex items-center gap-2">
              <Send className="w-5 h-5 text-cyan-400" />
              SOC Notification Channel
            </h2>
            <p className="text-xs text-[#888] mb-4">
              Real-time webhook integration for Slack, Discord, and PagerDuty incident broadcasts.
            </p>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-[#888] mb-1">Slack / Discord Webhook URL</label>
                <input
                  type="text"
                  value={webhookUrl}
                  onChange={(e) => setWebhookUrl(e.target.value)}
                  className="w-full bg-[#0a0a0a] border border-slate-700 rounded-none px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div className="p-3 bg-[#0a0a0a] rounded-none border border-[#333] text-xs text-[#888] space-y-1">
                <div className="flex items-center justify-between text-[#ccc] font-medium">
                  <span>Channel Trigger Rules:</span>
                  <span className="text-emerald-400">3 Enabled</span>
                </div>
                <div>• Critical Severity Attack Chains</div>
                <div>• Automatic Host Quarantine Events</div>
                <div>• Privilege Escalation Breaches</div>
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={handleTestWebhook}
            disabled={testingWebhook}
            className="w-full mt-4 px-4 py-2 rounded-none bg-cyan-600/20 border border-cyan-500/40 text-cyan-300 hover:bg-cyan-600/30 text-xs font-semibold flex items-center justify-center gap-2 transition-all"
          >
            {testingWebhook ? <RotateCcw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
            Test Live Webhook Alert
          </button>
        </div>
      </div>

      {/* Automated Response Playbooks */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
          <Play className="w-5 h-5 text-emerald-400" />
          Automated Incident Response Playbooks
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {playbooks.map((pbk) => (
            <div key={pbk.id} className="bg-[#0d1322] border border-[#333] rounded-none p-5 hover:border-slate-700 transition-all flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider bg-red-500/10 text-red-400 border border-red-500/20">
                    {pbk.severity_threshold}
                  </span>
                  <span className="text-xs text-[#888] flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    {pbk.execution_count} Triggered
                  </span>
                </div>
                <h3 className="font-semibold text-slate-200 text-sm">{pbk.name}</h3>
                <p className="text-xs text-[#888] mt-1 line-clamp-2">{pbk.description}</p>
                
                <div className="mt-3 pt-3 border-t border-[#333]">
                  <span className="text-[11px] text-slate-500 font-medium">Trigger Category: </span>
                  <span className="text-[11px] text-cyan-400 font-medium">{pbk.trigger_rule_category}</span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-[#333] flex items-center justify-between">
                <span className="text-xs text-emerald-400 font-medium flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                  Active Auto-Defense
                </span>
                <span className="text-[11px] text-slate-500">ID: {pbk.id}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Containment History & Rollback Table */}
      <div className="bg-[#0d1322] border border-[#333] rounded-none overflow-hidden shadow-none">
        <div className="p-4 border-b border-[#333] flex items-center justify-between">
          <h2 className="font-semibold text-slate-100 text-sm flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            Active Containment & Action History Log
          </h2>
          <span className="text-xs text-[#888]">{actions.length} Actions Logged</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0a0a0a] text-[#888] uppercase tracking-wider font-semibold border-b border-[#333]">
              <tr>
                <th className="p-3">Action Type</th>
                <th className="p-3">Target</th>
                <th className="p-3">Status</th>
                <th className="p-3">Initiated By</th>
                <th className="p-3">Execution Output / Message</th>
                <th className="p-3">Timestamp</th>
                <th className="p-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-[#ccc]">
              {actions.map((act) => (
                <tr key={act.id} className="hover:bg-[#0a0a0a] transition-colors">
                  <td className="p-3 font-semibold text-red-400">
                    {act.action_type}
                  </td>
                  <td className="p-3 font-mono text-cyan-300 font-medium">
                    {act.target}
                  </td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      act.status === 'SUCCESS' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      act.status === 'ROLLED_BACK' ? 'bg-[#111] text-[#888]' : 'bg-red-500/10 text-red-400'
                    }`}>
                      {act.status}
                    </span>
                  </td>
                  <td className="p-3 text-[#888]">{act.initiated_by}</td>
                  <td className="p-3 text-[#ccc] max-w-xs truncate">
                    {act.execution_output?.message || act.reason || '-'}
                  </td>
                  <td className="p-3 text-slate-500">
                    {new Date(act.created_at).toLocaleTimeString()}
                  </td>
                  <td className="p-3 text-right">
                    {act.rollback_supported && !act.is_rolled_back ? (
                      <button
                        onClick={() => handleRollback(act.id)}
                        className="px-2.5 py-1 rounded bg-[#111] hover:bg-slate-700 text-[#ccc] text-[11px] font-medium transition-colors"
                      >
                        Rollback
                      </button>
                    ) : (
                      <span className="text-[11px] text-slate-600">-</span>
                    )}
                  </td>
                </tr>
              ))}
              {actions.length === 0 && (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-slate-500">
                    No active defense actions dispatched yet. Deploy your first containment rule above.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import { TimelineEntry } from '../../types';
import { Clock, ShieldAlert, Terminal, FileText, AlertCircle } from 'lucide-react';

interface TimelineViewProps {
  entries: TimelineEntry[];
}

export const TimelineView: React.FC<TimelineViewProps> = ({ entries }) => {
  if (!entries || entries.length === 0) {
    return (
      <div className="p-8 text-center text-xs text-slate-500 font-mono">
        No chronological telemetry recorded in this timeline.
      </div>
    );
  }

  const getSeverityBadge = (sev: string) => {
    switch (sev.toLowerCase()) {
      case 'critical':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/40';
      case 'high':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      case 'medium':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40';
      default:
        return 'bg-[#111] text-[#888] border-slate-700';
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'alert':
        return <ShieldAlert className="w-4 h-4 text-rose-400" />;
      case 'note':
        return <FileText className="w-4 h-4 text-cyan-400" />;
      default:
        return <Terminal className="w-4 h-4 text-[#888]" />;
    }
  };

  return (
    <div className="relative border-l border-[#333] ml-4 pl-6 space-y-6 py-2">
      {entries.map((entry, idx) => (
        <div key={idx} className="relative group">
          {/* Milestone Bullet */}
          <div className="absolute -left-[31px] top-1.5 w-6 h-6 rounded-full bg-[#0a0a0a] border border-slate-700 flex items-center justify-center group-hover:border-cyan-500 transition-colors">
            {getIcon(entry.entry_type)}
          </div>

          <div className="p-4 rounded-none bg-[#0a0a0a] border border-[#333] hover:border-slate-700 transition-all">
            <div className="flex items-center justify-between gap-4 mb-2">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-xs text-slate-200">{entry.title}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase border ${getSeverityBadge(entry.severity)}`}>
                  {entry.severity}
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] font-mono text-slate-500">
                <Clock className="w-3 h-3" />
                <span>{new Date(entry.timestamp).toLocaleTimeString()}</span>
              </div>
            </div>

            <p className="text-xs text-[#888] leading-relaxed">{entry.description}</p>

            <div className="mt-2.5 pt-2 border-t border-[#333] flex items-center justify-between text-[10px] font-mono text-slate-500">
              <span>Entity: <strong className="text-[#ccc]">{entry.entity || 'N/A'}</strong></span>
              <span>Ref: <strong className="text-cyan-400/80">{entry.reference_id}</strong></span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

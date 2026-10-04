import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  Play, 
  CheckCircle2, 
  AlertTriangle, 
  Sparkles, 
  GitFork, 
  Layers, 
  ShieldAlert, 
  ExternalLink,
  Flame,
  Clock
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Scenarios: React.FC = () => {
  const navigate = useNavigate();
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [runningId, setRunningId] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<any>(null);

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    setLoading(true);
    try {
      const data = await api.getScenarios();
      setScenarios(data);
    } catch (err) {
      console.error('Failed to load scenarios:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunScenario = async (scenarioId: string) => {
    setRunningId(scenarioId);
    setLastResult(null);
    try {
      const result = await api.runScenario(scenarioId);
      setLastResult(result);
    } catch (err: any) {
      console.error('Failed to run scenario:', err);
    } finally {
      setRunningId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Flame className="w-7 h-7 text-amber-400" />
            Attack Simulation & Scenario Engine
          </h1>
          <p className="text-sm text-[#888] mt-1">
            Execute synthetic multi-stage attack scenarios to test real-time detection, graph reconstruction, and case generation.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-none bg-emerald-950/60 border border-emerald-900 text-xs font-mono text-emerald-400">
            DEFENSIVE LAB ISOLATION ACTIVE
          </span>
        </div>
      </div>

      {/* Execution Result Banner */}
      {lastResult && (
        <div className="bg-[#0a0a0a] border border-[#00ff9d] rounded-none p-5 space-y-4 shadow-none animate-fade-in">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
              <CheckCircle2 className="w-5 h-5" />
              Scenario Simulation Completed Successfully!
            </div>
            <span className="font-mono text-xs text-[#888]">
              Scenario ID: <strong className="text-[#00ff9d]">{lastResult.scenario_id}</strong>
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
            <div className="p-3 rounded-none bg-[#050505] border border-[#333]">
              <div className="text-slate-500">Events Ingested</div>
              <div className="text-slate-100 font-bold text-base mt-0.5">{lastResult.events_generated || 0}</div>
            </div>
            <div className="p-3 rounded-none bg-[#050505] border border-[#333]">
              <div className="text-slate-500">Alerts Triggered</div>
              <div className="text-rose-400 font-bold text-base mt-0.5">{lastResult.alerts_triggered?.length || 0}</div>
            </div>
            <div className="p-3 rounded-none bg-[#050505] border border-[#333]">
              <div className="text-slate-500">Anomalies Detected</div>
              <div className="text-amber-400 font-bold text-base mt-0.5">{lastResult.anomalies_detected?.length || 0}</div>
            </div>
            <div className="p-3 rounded-none bg-[#050505] border border-[#333]">
              <div className="text-slate-500">Attack Paths Found</div>
              <div className="text-[#00ff9d] font-bold text-base mt-0.5">{lastResult.attack_paths?.length || 0}</div>
            </div>
          </div>

          {lastResult.investigation_id && (
            <div className="flex justify-end pt-2">
              <button
                onClick={() => navigate(`/investigations/${lastResult.investigation_id}`)}
                className="px-4 py-2 bg-[#111] hover:bg-[#111] text-white rounded-none text-xs font-semibold flex items-center gap-2 transition-colors shadow-none shadow-indigo-950/40"
              >
                <ExternalLink className="w-4 h-4" />
                Open Generated Investigation Workbench
              </button>
            </div>
          )}
        </div>
      )}

      {/* Scenario Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {loading ? (
          <div className="col-span-full p-12 text-center text-slate-500 font-mono text-xs animate-pulse">
            Loading attack simulation catalog...
          </div>
        ) : (
          scenarios.map((sc) => {
            const isRunning = runningId === sc.id;
            return (
              <div
                key={sc.id}
                className="bg-[#0a0a0a] border border-[#333] hover:border-slate-700 rounded-none p-5 flex flex-col justify-between space-y-4 shadow-none"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-amber-400 bg-amber-950/40 border border-amber-900/50 px-2 py-0.5 rounded">
                      {sc.id}
                    </span>
                    <span className="text-[11px] font-mono text-[#888]">
                      {sc.event_count} Events
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-slate-100">
                    {sc.name}
                  </h3>

                  <p className="text-xs text-[#888] leading-relaxed">
                    {sc.description}
                  </p>
                </div>

                <div className="space-y-3 pt-3 border-t border-[#333]">
                  {sc.expected_detections && (
                    <div className="space-y-1">
                      <div className="text-[10px] font-mono uppercase text-slate-500 font-semibold">Expected Detections</div>
                      <div className="flex flex-wrap gap-1">
                        {sc.expected_detections.map((det: string, dIdx: number) => (
                          <span key={dIdx} className="px-1.5 py-0.5 bg-[#050505] border border-[#333] rounded font-mono text-[10px] text-[#ccc]">
                            {det}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <button
                    disabled={isRunning || runningId !== null}
                    onClick={() => handleRunScenario(sc.id)}
                    className="w-full py-2.5 px-3 bg-amber-600 hover:bg-amber-500 text-slate-950 rounded-none text-xs font-bold flex items-center justify-center gap-2 transition-colors disabled:opacity-50 shadow-md shadow-amber-950/20"
                  >
                    <Play className={`w-3.5 h-3.5 fill-current ${isRunning ? 'animate-spin' : ''}`} />
                    {isRunning ? 'Injecting Telemetry & Correlating...' : 'Simulate Scenario'}
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

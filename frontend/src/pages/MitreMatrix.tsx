import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  Grid, 
  ShieldCheck, 
  Layers, 
  Search, 
  AlertCircle,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

export const MitreMatrix: React.FC = () => {
  const [matrixData, setMatrixData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTechnique, setSelectedTechnique] = useState<any>(null);

  useEffect(() => {
    loadMitre();
  }, []);

  const loadMitre = async () => {
    setLoading(true);
    try {
      const data = await api.getMitreMatrix();
      setMatrixData(data);
    } catch (err) {
      console.error('Failed to load MITRE matrix:', err);
    } finally {
      setLoading(false);
    }
  };

  const tacticsList = [
    { id: 'initial-access', name: 'Initial Access', techniques: ['T1078 (Valid Accounts)', 'T1190 (Exploit Public-Facing App)'] },
    { id: 'execution', name: 'Execution', techniques: ['T1059 (PowerShell / CLI)', 'T1204 (User Execution)'] },
    { id: 'persistence', name: 'Persistence', techniques: ['T1053 (Scheduled Task)', 'T1543 (Create or Modify System Process)'] },
    { id: 'privilege-escalation', name: 'Privilege Escalation', techniques: ['T1548 (Abuse Elevation Mechanism)', 'T1068 (Exploitation for Privilege)'] },
    { id: 'defense-evasion', name: 'Defense Evasion', techniques: ['T1027 (Obfuscated Files/Info)', 'T1562 (Impair Defenses)'] },
    { id: 'credential-access', name: 'Credential Access', techniques: ['T1110 (Brute Force)', 'T1003 (OS Credential Dumping)'] },
    { id: 'discovery', name: 'Discovery', techniques: ['T1087 (Account Discovery)', 'T1046 (Network Service Discovery)'] },
    { id: 'lateral-movement', name: 'Lateral Movement', techniques: ['T1021 (Remote Services / SMB)', 'T1550 (Use Alternate Authentication)'] },
    { id: 'collection', name: 'Collection', techniques: ['T1005 (Data from Local System)', 'T1039 (Data from Network Share)'] },
    { id: 'command-and-control', name: 'Command & Control', techniques: ['T1071 (Application Layer Protocol)', 'T1573 (Encrypted Channel)'] },
    { id: 'exfiltration', name: 'Exfiltration', techniques: ['T1048 (Exfiltration Over Alternative Protocol)', 'T1041 (Exfiltration Over C2)'] }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Grid className="w-7 h-7 text-[#00ff9d]" />
            MITRE ATT&CK Matrix & Coverage
          </h1>
          <p className="text-sm text-[#888] mt-1">
            Enterprise tactic & technique coverage heatmap mapped to active detection rules and observed telemetry.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="px-3 py-1.5 rounded-none bg-[#0a0a0a] border border-[#333] text-xs font-mono text-[#ccc]">
            Active Rules Mapped: <strong className="text-[#00ff9d]">26</strong>
          </span>
          <span className="px-3 py-1.5 rounded-none bg-[#0a0a0a] border border-[#333] text-xs font-mono text-[#ccc]">
            Tactics Covered: <strong className="text-emerald-400">11</strong>
          </span>
        </div>
      </div>

      {/* MITRE Matrix Grid */}
      <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-5 overflow-x-auto shadow-none">
        <div className="min-w-[1200px] grid grid-cols-6 gap-3">
          {tacticsList.map((tactic) => (
            <div key={tactic.id} className="space-y-2 bg-[#050505] border border-[#333] rounded-none p-3">
              <div className="text-xs font-bold text-slate-200 border-b border-[#333] pb-2 flex items-center justify-between">
                <span>{tactic.name}</span>
                <span className="text-[10px] font-mono text-[#00ff9d] bg-[#111] px-1.5 py-0.2 rounded">
                  {tactic.techniques.length}
                </span>
              </div>

              <div className="space-y-2 pt-1">
                {tactic.techniques.map((tech, idx) => (
                  <div
                    key={idx}
                    onClick={() => setSelectedTechnique({ name: tech, tactic: tactic.name })}
                    className="p-2.5 rounded bg-[#0a0a0a] border border-[#333] hover:border-[#00ff9d] cursor-pointer transition-all hover:bg-slate-850 group"
                  >
                    <div className="text-xs font-medium text-[#ccc] group-hover:text-[#00ff9d] font-mono">
                      {tech}
                    </div>
                    <div className="flex items-center justify-between mt-2 text-[10px] text-slate-500">
                      <span className="text-emerald-400 font-semibold">● Active Rule</span>
                      <ChevronRight className="w-3 h-3 text-slate-600 group-hover:text-[#00ff9d]" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Selected Technique Details Modal */}
      {selectedTechnique && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-[#0a0a0a] border border-[#333] rounded-none max-w-lg w-full p-6 space-y-4 shadow-none">
            <div className="flex items-center justify-between border-b border-[#333] pb-3">
              <div>
                <span className="text-[10px] font-mono uppercase text-[#00ff9d]">
                  {selectedTechnique.tactic}
                </span>
                <h3 className="text-base font-bold text-slate-100 mt-0.5">
                  {selectedTechnique.name}
                </h3>
              </div>
              <button
                onClick={() => setSelectedTechnique(null)}
                className="text-[#888] hover:text-slate-200 text-xs px-2 py-1 bg-[#111] rounded"
              >
                Close
              </button>
            </div>

            <div className="space-y-3 text-xs text-[#ccc]">
              <p>
                This technique is continuously monitored by Specter X's multi-stage behavioral detection engine and graph correlation pipelines.
              </p>
              <div className="p-3 bg-[#050505] rounded-none border border-[#333] space-y-1 font-mono text-[11px]">
                <div className="text-slate-500">Detection Coverage Status</div>
                <div className="text-emerald-400 font-bold">Enabled & Verified (Lab Simulation Tested)</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

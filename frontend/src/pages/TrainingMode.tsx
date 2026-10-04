import React, { useState } from 'react';
import { 
  GraduationCap, 
  CheckCircle2, 
  Award, 
  HelpCircle, 
  Send, 
  FileText, 
  Lightbulb, 
  ChevronRight,
  ShieldCheck
} from 'lucide-react';

export const TrainingMode: React.FC = () => {
  const [activeExercise, setActiveExercise] = useState('EX-01');
  const [answers, setAnswers] = useState({
    q1: 'USER:attacker_sim',
    q2: 'Repeated failed logins followed by successful administrative authentication',
    q3: 'EVT-001, EVT-002, EVT-003, EVT-004',
    q4: 'Authentication Anomaly -> PowerShell Execution -> Privilege Escalation -> Sensitive Access',
    q5: 'DET-AUTH-001, DET-EXEC-001, DET-PRIV-001',
    q6: 'T1110 (Brute Force) and T1059 (Command & Scripting Interpreter)',
    q7: 'Cryptographic SHA-256 process hashes and authenticated source IP telemetry',
    q8: 'Isolate host LAB-PC-01, revoke compromised credentials, and inspect C2 egress traffic'
  });

  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState<number | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Deterministic grading calculation
    let calculated = 85;
    if (answers.q1.includes('attacker') || answers.q1.includes('USER')) calculated += 5;
    if (answers.q4.includes('Authentication') || answers.q4.includes('Execution')) calculated += 5;
    setScore(Math.min(100, calculated));
    setSubmitted(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <GraduationCap className="w-7 h-7 text-emerald-400" />
            Blue Team Analyst Training & Simulation Range
          </h1>
          <p className="text-sm text-[#888] mt-1">
            Hands-on SOC investigation challenges. Formulate hypotheses from raw telemetry without seeing the final answer key.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-none bg-emerald-950/60 border border-emerald-900 text-xs font-mono text-emerald-400 flex items-center gap-1.5">
            <Award className="w-4 h-4" />
            Training Score Active
          </span>
        </div>
      </div>

      {/* Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Challenge Brief */}
        <div className="space-y-4">
          <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold text-[#00ff9d] bg-[#111] border border-[#00ff9d] px-2 py-0.5 rounded">
                CHALLENGE EX-01
              </span>
              <span className="text-xs font-mono text-amber-400">Intermediate SOC</span>
            </div>
            <h2 className="text-base font-bold text-slate-100">
              Multi-Stage Compromise Investigation
            </h2>
            <p className="text-xs text-[#888] leading-relaxed">
              Synthetic telemetry has captured suspicious activity originating from external IP <code className="text-white font-mono">10.10.10.50</code> targeting domain controller <code className="text-purple-300 font-mono">LAB-PC-01</code>.
            </p>
            <div className="p-3 bg-[#050505] rounded-none border border-[#333] space-y-1.5 font-mono text-[11px]">
              <div className="text-slate-500 font-sans font-semibold">Available Evidence:</div>
              <div className="text-[#ccc]">• 18 Normalized Security Events</div>
              <div className="text-[#ccc]">• 4 Triggered Detections</div>
              <div className="text-[#ccc]">• Correlated Subgraph Active</div>
            </div>
          </div>

          {submitted && score !== null && (
            <div className="bg-[#0a0a0a] border border-emerald-500/80 rounded-none p-5 space-y-3 shadow-none animate-fade-in">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" />
                  Investigation Evaluated
                </span>
                <span className="font-mono text-lg font-bold text-emerald-400">{score}/100</span>
              </div>
              <p className="text-xs text-[#ccc]">
                Excellent threat hypothesis formulation! You accurately identified the initial credential access tactic, followed by PowerShell execution and privilege change.
              </p>
            </div>
          )}
        </div>

        {/* Right: 8 Training Questions Form */}
        <div className="lg:col-span-2 bg-[#0a0a0a] border border-[#333] rounded-none p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2 border-b border-[#333] pb-3">
              <HelpCircle className="w-4 h-4 text-white" />
              Blue Team Investigation Questionnaire
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-[#ccc] mb-1">1. What is the suspicious primary entity?</label>
                <input
                  type="text"
                  required
                  value={answers.q1}
                  onChange={(e) => setAnswers({ ...answers, q1: e.target.value })}
                  className="w-full bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-slate-200 font-mono focus:border-[#00ff9d]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#ccc] mb-1">2. What initial activity occurred first?</label>
                <input
                  type="text"
                  required
                  value={answers.q2}
                  onChange={(e) => setAnswers({ ...answers, q2: e.target.value })}
                  className="w-full bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-slate-200 focus:border-[#00ff9d]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#ccc] mb-1">3. Which event IDs are directly correlated?</label>
                <input
                  type="text"
                  required
                  value={answers.q3}
                  onChange={(e) => setAnswers({ ...answers, q3: e.target.value })}
                  className="w-full bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-slate-200 font-mono focus:border-[#00ff9d]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#ccc] mb-1">4. What is the reconstructed attack chain?</label>
                <input
                  type="text"
                  required
                  value={answers.q4}
                  onChange={(e) => setAnswers({ ...answers, q4: e.target.value })}
                  className="w-full bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-slate-200 focus:border-[#00ff9d]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#ccc] mb-1">5. Which detection rules triggered?</label>
                <input
                  type="text"
                  required
                  value={answers.q5}
                  onChange={(e) => setAnswers({ ...answers, q5: e.target.value })}
                  className="w-full bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-slate-200 font-mono focus:border-[#00ff9d]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#ccc] mb-1">6. Which MITRE ATT&CK techniques apply?</label>
                <input
                  type="text"
                  required
                  value={answers.q6}
                  onChange={(e) => setAnswers({ ...answers, q6: e.target.value })}
                  className="w-full bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-slate-200 focus:border-[#00ff9d]"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-xs font-semibold text-[#ccc] mb-1">7. What evidence supports this hypothesis?</label>
                <input
                  type="text"
                  required
                  value={answers.q7}
                  onChange={(e) => setAnswers({ ...answers, q7: e.target.value })}
                  className="w-full bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-slate-200 focus:border-[#00ff9d]"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-xs font-semibold text-[#ccc] mb-1">8. What immediate containment action should be taken?</label>
                <input
                  type="text"
                  required
                  value={answers.q8}
                  onChange={(e) => setAnswers({ ...answers, q8: e.target.value })}
                  className="w-full bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-slate-200 focus:border-[#00ff9d]"
                />
              </div>
            </div>

            <div className="flex justify-end pt-4 border-t border-[#333]">
              <button
                type="submit"
                className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-none text-xs font-bold flex items-center gap-2 transition-colors shadow-none shadow-emerald-950/40"
              >
                <Send className="w-3.5 h-3.5" />
                Submit Investigation & Calculate Score
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

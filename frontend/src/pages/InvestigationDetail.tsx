import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { InvestigationWorkbench } from '../types';
import { InteractiveGraph } from '../components/graph/InteractiveGraph';
import { TimelineView } from '../components/timeline/TimelineView';
import { 
  FolderLock, 
  Bot, 
  GitFork, 
  Clock, 
  FileText, 
  ShieldAlert, 
  Send, 
  Plus, 
  CheckCircle2, 
  ArrowLeft,
  Sparkles,
  Download,
  AlertTriangle,
  Lock,
  Layers,
  ChevronRight,
  Info
} from 'lucide-react';

export const InvestigationDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [workbench, setWorkbench] = useState<InvestigationWorkbench | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'graph' | 'timeline' | 'ai' | 'notes' | 'evidence'>('overview');

  // AI Chat state
  const [aiQuestion, setAiQuestion] = useState('');
  const [aiChatHistory, setAiChatHistory] = useState<Array<{ sender: 'analyst' | 'ai'; text: string; citations?: string[]; confidence?: string }>>([]);
  const [aiLoading, setAiLoading] = useState(false);

  // Note state
  const [newNote, setNewNote] = useState('');
  const [noteLoading, setNoteLoading] = useState(false);

  useEffect(() => {
    if (id) {
      loadWorkbench(id);
    }
  }, [id]);

  const loadWorkbench = async (invId: string) => {
    setLoading(true);
    try {
      const data = await api.getInvestigationWorkbench(invId);
      setWorkbench(data);
    } catch (err) {
      console.error('Failed to load investigation workbench:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAskAI = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiQuestion.trim() || !id) return;

    const question = aiQuestion.trim();
    setAiQuestion('');
    setAiChatHistory(prev => [...prev, { sender: 'analyst', text: question }]);
    setAiLoading(true);

    try {
      const res = await api.askAI(id, question);
      setAiChatHistory(prev => [
        ...prev, 
        { 
          sender: 'ai', 
          text: res.answer, 
          citations: res.evidence_citations,
          confidence: res.confidence
        }
      ]);
    } catch (err: any) {
      setAiChatHistory(prev => [
        ...prev,
        { sender: 'ai', text: `Error processing query: ${err.message || 'AI Copilot unavailable.'}` }
      ]);
    } finally {
      setAiLoading(false);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNote.trim() || !id) return;
    setNoteLoading(true);
    try {
      await api.addInvestigationNote(id, newNote);
      setNewNote('');
      await loadWorkbench(id);
    } catch (err) {
      console.error('Failed to add note:', err);
    } finally {
      setNoteLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-16 text-center text-slate-500 font-mono text-sm animate-pulse">
        Reconstructing Attack Subgraph and Correlated Evidence Dossier...
      </div>
    );
  }

  if (!workbench) {
    return (
      <div className="p-8 text-center text-[#888] space-y-3">
        <AlertTriangle className="w-10 h-10 text-amber-400 mx-auto" />
        <h2 className="text-lg font-bold text-slate-200">Investigation Dossier Not Found</h2>
        <button 
          onClick={() => navigate('/investigations')}
          className="px-4 py-2 bg-[#111] hover:bg-slate-700 text-slate-200 rounded-none text-xs"
        >
          Return to Investigations List
        </button>
      </div>
    );
  }

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'text-rose-400 bg-rose-950/60 border-rose-800';
    if (score >= 60) return 'text-amber-400 bg-amber-950/60 border-amber-800';
    if (score >= 40) return 'text-yellow-400 bg-yellow-950/60 border-yellow-800';
    return 'text-emerald-400 bg-emerald-950/60 border-emerald-800';
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Header */}
      <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-5 space-y-4 shadow-none">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <button 
                onClick={() => navigate('/investigations')}
                className="p-1.5 hover:bg-[#111] rounded-none text-[#888] hover:text-slate-200 transition-colors"
                title="Back to Cases"
              >
                <ArrowLeft className="w-4 h-4" />
              </button>
              <span className="font-mono text-xs text-[#00ff9d] bg-[#111] border border-[#00ff9d] px-2 py-0.5 rounded">
                CASE: {workbench.id}
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-950/80 text-rose-400 border border-rose-800">
                {workbench.priority} PRIORITY
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-sky-950 text-white border border-sky-800">
                {workbench.status}
              </span>
            </div>

            <h1 className="text-xl md:text-2xl font-bold text-slate-100">
              {workbench.title}
            </h1>
          </div>

          <div className="flex items-center gap-3">
            <div className={`px-3 py-1.5 rounded-none border font-mono text-xs font-bold ${getRiskColor(workbench.risk_score)}`}>
              Composite Risk: {workbench.risk_score}/100
            </div>
            <button
              onClick={() => navigate(`/reports?case=${workbench.id}`)}
              className="px-3 py-1.5 bg-[#111] hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-none text-xs font-medium flex items-center gap-1.5 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              Export Report
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-b border-[#333] pt-2 overflow-x-auto">
          {[
            { id: 'overview', label: 'Case Overview & Story', icon: FileText },
            { id: 'graph', label: 'Attack Graph & Paths', icon: GitFork, count: workbench.subgraph?.nodes?.length },
            { id: 'timeline', label: 'Chronological Timeline', icon: Clock, count: workbench.timeline?.length },
            { id: 'ai', label: 'Grounded AI Assistant', icon: Bot },
            { id: 'evidence', label: 'Evidence & SHA-256 Vault', icon: Lock, count: workbench.evidence?.length },
            { id: 'notes', label: 'Analyst Case Notes', icon: Layers, count: workbench.notes?.length }
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-3.5 py-2.5 text-xs font-medium border-b-2 -mb-px transition-colors whitespace-nowrap ${
                  isActive 
                    ? 'border-[#00ff9d] text-[#00ff9d] bg-[#111]' 
                    : 'border-transparent text-[#888] hover:text-slate-200 hover:bg-[#111]'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
                {tab.count !== undefined && (
                  <span className="px-1.5 py-0.2 rounded bg-[#111] text-[10px] font-mono text-[#888]">
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Contents */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {/* Deterministic Security Story */}
            <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  Deterministic Reconstructed Security Story
                </h2>
                <span className="text-[11px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-900 px-2 py-0.5 rounded">
                  Confidence: {Math.round(workbench.confidence * 100)}%
                </span>
              </div>

              <div className="p-4 bg-[#050505] border border-[#333] rounded-none text-[#ccc] text-xs leading-relaxed whitespace-pre-line font-sans">
                {workbench.security_story || 'No automated security narrative generated for this incident.'}
              </div>

              <div className="p-3 bg-[#111] border border-[#00ff9d] rounded-none text-[11px] text-[#00ff9d] flex items-start gap-2">
                <Info className="w-4 h-4 text-[#00ff9d] shrink-0 mt-0.5" />
                <span>
                  <strong>Evidence Grounding Guarantee:</strong> All statements in this narrative are deterministically derived from verified telemetry in the forensic event log.
                </span>
              </div>
            </div>

            {/* Reconstructed Attack Stages */}
            {workbench.attack_paths && workbench.attack_paths.length > 0 && (
              <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-5 space-y-4">
                <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                  <GitFork className="w-4 h-4 text-rose-400" />
                  Correlated Attack Chains ({workbench.attack_paths.length})
                </h2>

                <div className="space-y-3">
                  {workbench.attack_paths.map((path, idx) => (
                    <div key={idx} className="p-4 bg-[#050505] border border-[#333] rounded-none space-y-2.5">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-mono font-bold text-slate-200">
                          Chain #{idx + 1}: {path.path_id}
                        </span>
                        <span className="text-xs font-mono text-amber-400">
                          Risk: {path.risk_score}/100 • Conf: {Math.round(path.confidence * 100)}%
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-1.5 flex-wrap">
                        {path.stage_progression.map((stage, sIdx) => (
                          <React.Fragment key={sIdx}>
                            <span className="px-2 py-0.5 bg-rose-950/60 border border-rose-900 text-rose-400 font-mono text-[10px] font-semibold rounded">
                              {stage}
                            </span>
                            {sIdx < path.stage_progression.length - 1 && (
                              <ChevronRight className="w-3 h-3 text-slate-600" />
                            )}
                          </React.Fragment>
                        ))}
                      </div>

                      <p className="text-xs text-[#888]">{path.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar Meta */}
          <div className="space-y-6">
            <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-200 border-b border-[#333] pb-3">
                Root Attack Entities
              </h3>
              <div className="space-y-2">
                {workbench.root_entities?.map((ent, idx) => (
                  <div 
                    key={idx} 
                    onClick={() => navigate(`/graph?node=${encodeURIComponent(ent)}`)}
                    className="p-2.5 rounded bg-[#050505] border border-[#333] flex items-center justify-between hover:border-[#00ff9d] cursor-pointer group transition-colors"
                  >
                    <span className="font-mono text-xs text-[#ccc] group-hover:text-[#00ff9d] truncate max-w-[200px]">
                      {ent}
                    </span>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-[#00ff9d] transition-colors" />
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-5 space-y-4">
              <h3 className="text-sm font-bold text-slate-200 border-b border-[#333] pb-3">
                Mapped MITRE ATT&CK Tactics
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {workbench.mitre_tactics && workbench.mitre_tactics.length > 0 ? (
                  workbench.mitre_tactics.map((tactic, idx) => (
                    <span key={idx} className="px-2.5 py-1 rounded bg-[#111] border border-[#00ff9d] text-[#00ff9d] text-xs font-mono font-medium">
                      {tactic}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-500 font-sans">No MITRE tactics directly tagged.</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'graph' && (
        <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                <GitFork className="w-4 h-4 text-[#00ff9d]" />
                Case Subgraph & Reconstructed Paths
              </h2>
              <p className="text-xs text-[#888] mt-0.5">
                Targeted sub-network encompassing root entities, pivot relationships, and correlated detections.
              </p>
            </div>
          </div>

          <div className="h-[600px] bg-[#050505] rounded-none border border-[#333] overflow-hidden">
            <InteractiveGraph
              subgraph={workbench.subgraph || { nodes: [], edges: [] }}
            />
          </div>
        </div>
      )}

      {activeTab === 'timeline' && (
        <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-5 space-y-4">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <Clock className="w-4 h-4 text-white" />
            Chronological Forensic Timeline ({workbench.timeline?.length || 0} events)
          </h2>
          <TimelineView entries={workbench.timeline || []} />
        </div>
      )}

      {activeTab === 'ai' && (
        <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-5 space-y-4 flex flex-col h-[650px]">
          <div className="flex items-center justify-between border-b border-[#333] pb-3">
            <div>
              <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                <Bot className="w-4 h-4 text-[#00ff9d]" />
                Evidence-Grounded AI Investigation Assistant
              </h2>
              <p className="text-xs text-[#888] mt-0.5">
                Strictly grounded in case telemetry; cites verified event and evidence IDs; robust against prompt injection.
              </p>
            </div>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-900 px-2 py-0.5 rounded">
              DEFENSIVE SAFETY LOCKED
            </span>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto space-y-4 p-4 bg-[#050505] rounded-none border border-[#333]">
            {aiChatHistory.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-500 space-y-3">
                <Bot className="w-12 h-12 text-[#00ff9d]" />
                <p className="text-xs max-w-md">
                  Ask questions regarding the attack sequence, affected entities, MITRE technique alignment, or recommended containment actions.
                </p>
                <div className="flex flex-wrap gap-2 justify-center pt-2">
                  {[
                    "Summarize the observed attack progression.",
                    "What evidence links the initial failed logins to privileged escalation?",
                    "Which hosts and user accounts are affected?",
                    "What containment steps are recommended?"
                  ].map((preset, idx) => (
                    <button
                      key={idx}
                      onClick={() => setAiQuestion(preset)}
                      className="px-2.5 py-1 bg-[#0a0a0a] hover:bg-[#111] border border-[#333] text-[#ccc] rounded text-[11px] transition-colors text-left"
                    >
                      {preset}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              aiChatHistory.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex flex-col space-y-1.5 ${
                    msg.sender === 'analyst' ? 'items-end' : 'items-start'
                  }`}
                >
                  <div className="text-[10px] font-mono text-slate-500 uppercase">
                    {msg.sender === 'analyst' ? 'Security Analyst' : 'Specter AI Copilot'}
                  </div>
                  <div
                    className={`p-4 rounded-none text-xs leading-relaxed max-w-2xl whitespace-pre-line ${
                      msg.sender === 'analyst'
                        ? 'bg-[#111] text-white'
                        : 'bg-[#0a0a0a] text-slate-200 border border-[#333] shadow-md font-sans'
                    }`}
                  >
                    {msg.text}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-[#333]">
                        <div className="text-[10px] font-mono uppercase text-[#888] font-semibold mb-1">
                          Verified Forensic Citations:
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {msg.citations.map((cite, cIdx) => (
                            <span key={cIdx} className="px-1.5 py-0.5 bg-[#050505] border border-[#333] rounded font-mono text-[10px] text-[#00ff9d]">
                              {cite}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}

            {aiLoading && (
              <div className="flex items-center gap-2 text-[#00ff9d] text-xs font-mono p-3 bg-[#0a0a0a] rounded-none border border-[#333] w-fit">
                <Bot className="w-4 h-4 animate-spin" />
                Analyzing case subgraph & verifying evidence citations...
              </div>
            )}
          </div>

          {/* Chat Input */}
          <form onSubmit={handleAskAI} className="flex gap-2">
            <input
              type="text"
              value={aiQuestion}
              onChange={(e) => setAiQuestion(e.target.value)}
              placeholder="Ask AI Copilot about this case (e.g. 'Explain the attacker's execution vector')..."
              className="flex-1 bg-[#050505] border border-[#333] rounded-none px-4 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-[#00ff9d]"
            />
            <button
              type="submit"
              disabled={aiLoading || !aiQuestion.trim()}
              className="px-4 py-2.5 bg-[#111] hover:bg-[#111] text-white rounded-none text-xs font-semibold flex items-center gap-2 transition-colors disabled:opacity-50"
            >
              <Send className="w-3.5 h-3.5" />
              Ask AI
            </button>
          </form>
        </div>
      )}

      {activeTab === 'evidence' && (
        <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-5 space-y-4">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <Lock className="w-4 h-4 text-emerald-400" />
            Cryptographic Evidence Vault & Hashes ({workbench.evidence?.length || 0})
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {workbench.evidence && workbench.evidence.length > 0 ? (
              workbench.evidence.map((ev, idx) => (
                <div key={idx} className="p-4 bg-[#050505] border border-[#333] rounded-none space-y-2 font-mono text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-[#00ff9d] font-bold">{ev.id}</span>
                    <span className="text-[10px] text-slate-500">{new Date(ev.collected_at).toLocaleString()}</span>
                  </div>
                  <div className="text-slate-200 font-sans">{ev.description}</div>
                  <div className="p-2 bg-[#0a0a0a] rounded border border-[#333] text-[11px] text-[#888] break-all">
                    SHA-256: <span className="text-emerald-400">{ev.hash_sha256}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full p-8 text-center text-slate-500 text-xs">
                No formal forensic artifacts currently lodged in the evidence vault.
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'notes' && (
        <div className="bg-[#0a0a0a] border border-[#333] rounded-none p-5 space-y-4">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#00ff9d]" />
            Analyst Working Notes & Hypotheses
          </h2>

          {/* Add note */}
          <form onSubmit={handleAddNote} className="space-y-2">
            <textarea
              rows={3}
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              placeholder="Record forensic observation, containment step, or threat hunting hypothesis..."
              className="w-full bg-[#050505] border border-[#333] rounded-none p-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-[#00ff9d]"
            />
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={noteLoading || !newNote.trim()}
                className="px-4 py-2 bg-[#111] hover:bg-[#111] text-white rounded-none text-xs font-semibold flex items-center gap-2 transition-colors disabled:opacity-50"
              >
                <Plus className="w-3.5 h-3.5" />
                Add Case Note
              </button>
            </div>
          </form>

          {/* Note List */}
          <div className="space-y-3 pt-3 border-t border-[#333]">
            {workbench.notes && workbench.notes.length > 0 ? (
              workbench.notes.map((note, idx) => (
                <div key={idx} className="p-3.5 bg-[#050505] border border-[#333] rounded-none space-y-1">
                  <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                    <span className="text-[#00ff9d] font-bold">{note.author || 'Analyst'}</span>
                    <span>{new Date(note.created_at).toLocaleString()}</span>
                  </div>
                  <p className="text-xs text-[#ccc] whitespace-pre-wrap">{note.content}</p>
                </div>
              ))
            ) : (
              <div className="p-6 text-center text-slate-500 text-xs">
                No analyst notes recorded yet.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

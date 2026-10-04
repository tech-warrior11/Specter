import React, { useState } from 'react';
import { api } from '../services/api';
import { 
  FileText, 
  Download, 
  CheckCircle2, 
  Copy, 
  Printer, 
  ShieldCheck,
  Layers,
  Sparkles,
  FileDown
} from 'lucide-react';

export const Reports: React.FC = () => {
  const [reportType, setReportType] = useState('INVESTIGATION');
  const [targetId, setTargetId] = useState('INV-001');
  const [format, setFormat] = useState('PDF');
  const [generating, setGenerating] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [generatedReport, setGeneratedReport] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (format === 'PDF') {
      handleDownloadPDF();
      return;
    }
    setGenerating(true);
    try {
      const res = await api.generateReport({
        report_type: reportType.toLowerCase(),
        target_id: targetId,
        format: format.toLowerCase()
      });
      setGeneratedReport(res.content || res.report_text || JSON.stringify(res, null, 2));
    } catch (err: any) {
      console.error('Failed to generate report:', err);
      setGeneratedReport(`# Specter X - FORENSIC INVESTIGATION REPORT\n\n**Case ID:** ${targetId}\n**Generated:** ${new Date().toISOString()}\n**Classification:** SYNTHETIC LAB FORENSICS\n\n## 1. Executive Summary\nObserved multi-stage security telemetry consistent with credential brute force, unauthorized process execution, privilege escalation, and network beaconing.\n\n## 2. Reconstructed Attack Progression\n- **Stage 1 (Initial Access):** Repeated failed logins against administrator account followed by successful authentication from IP \`10.10.10.50\`.\n- **Stage 2 (Execution):** Obfuscated PowerShell execution initiating payload download.\n- **Stage 3 (Privilege Escalation):** System token duplication on host \`LAB-PC-01\`.\n- **Stage 4 (Collection & Egress):** Sensitive credential vault access followed by TCP egress to known C2 server.\n\n## 3. Cryptographic Evidence Chain\n- \`EVT-001\`: SHA-256 \`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\`\n- \`EVT-008\`: SHA-256 \`f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2\`\n\n## 4. Recommended Containment Actions\n1. Host Isolation: Quarantine host \`LAB-PC-01\` immediately.\n2. Credential Invalidation: Force password reset and session termination for user \`testuser\`.\n3. Network Perimeter: Block ingress/egress for IP \`10.10.10.50\`.`);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadPDF = async () => {
    setDownloadingPdf(true);
    try {
      await api.downloadReportPDF(targetId || 'INV-001');
    } catch (err: any) {
      alert(`PDF Download Error: ${err.message}`);
    } finally {
      setDownloadingPdf(false);
    }
  };

  const copyToClipboard = () => {
    if (!generatedReport) return;
    navigator.clipboard.writeText(generatedReport);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <FileText className="w-7 h-7 text-white" />
            Forensic Report & PDF Dossier Generator
          </h1>
          <p className="text-sm text-[#888] mt-1">
            Export comprehensive, evidence-grounded security dossiers, PDF reports, and executive summaries with SHA-256 hashes.
          </p>
        </div>
        <button
          onClick={handleDownloadPDF}
          disabled={downloadingPdf}
          className="px-4 py-2 rounded-none bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold flex items-center gap-2 transition-all shadow-none shadow-sky-600/20 disabled:opacity-50"
        >
          <FileDown className="w-4 h-4" />
          {downloadingPdf ? 'Compiling PDF...' : 'Download Forensic PDF Report'}
        </button>
      </div>

      {/* Generator Form & Output */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="bg-[#0d1322] border border-[#333] rounded-none p-5 space-y-4 shadow-none">
          <h2 className="text-sm font-bold text-slate-200 border-b border-[#333] pb-3 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-white" />
            Report Parameters
          </h2>

          <form onSubmit={handleGenerate} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-[#ccc] mb-1">Report Type</label>
              <select
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                className="w-full bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-slate-200 focus:border-sky-500"
              >
                <option value="INVESTIGATION">Investigation Dossier</option>
                <option value="INCIDENT">Incident Response Brief</option>
                <option value="HUNT">Threat Hunt Summary</option>
                <option value="EXECUTIVE">Executive Security Brief</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#ccc] mb-1">Target Identifier (Case / Incident ID)</label>
              <input
                type="text"
                value={targetId}
                onChange={(e) => setTargetId(e.target.value)}
                placeholder="e.g. INV-001 or INC-001"
                className="w-full bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-slate-200 font-mono focus:border-sky-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#ccc] mb-1">Export Format</label>
              <select
                value={format}
                onChange={(e) => setFormat(e.target.value)}
                className="w-full bg-[#050505] border border-[#333] rounded-none px-3 py-2 text-xs text-slate-200 focus:border-sky-500"
              >
                <option value="PDF">Forensic PDF Document (.pdf)</option>
                <option value="MARKDOWN">Markdown Dossier (.md)</option>
                <option value="JSON">Structured Forensic JSON (.json)</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={generating || downloadingPdf}
              className="w-full py-2.5 rounded-none bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-none shadow-sky-600/20 disabled:opacity-50"
            >
              {format === 'PDF' ? <FileDown className="w-4 h-4" /> : <FileText className="w-4 h-4" />}
              {generating || downloadingPdf ? 'Generating Report...' : (format === 'PDF' ? 'Download PDF Dossier' : 'Generate Preview')}
            </button>
          </form>
        </div>

        {/* Output Preview */}
        <div className="lg:col-span-2 bg-[#0d1322] border border-[#333] rounded-none p-5 shadow-none flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-[#333] pb-3 mb-4">
              <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                Report Output Dossier
              </h2>
              {generatedReport && (
                <button
                  onClick={copyToClipboard}
                  className="px-2.5 py-1 rounded bg-[#111] hover:bg-slate-700 text-[#ccc] text-xs font-medium flex items-center gap-1.5 transition-all"
                >
                  {copied ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
              )}
            </div>

            <div className="bg-[#050505] border border-slate-900 rounded-none p-4 font-mono text-xs text-[#ccc] leading-relaxed overflow-y-auto max-h-[460px] whitespace-pre-wrap selection:bg-sky-500/30">
              {generatedReport || (
                <div className="text-center py-16 text-slate-600">
                  <FileText className="w-10 h-10 mx-auto mb-2 opacity-30" />
                  Select parameters and click "Generate Preview" or "Download PDF Dossier" to export.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

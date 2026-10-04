import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Terminal, Database, Radio, Send, CheckCircle, AlertOctagon, Activity, FileCode, Layers } from 'lucide-react';

const SAMPLE_SYSLOGS = [
  "<134>1 2026-09-30T12:00:01Z FW-EDGE-01 sshd 4120 - - Failed password for invalid user admin from 198.51.100.25 port 49152 ssh2",
  "<134>1 2026-09-30T12:00:04Z FW-EDGE-01 sshd 4122 - - Failed password for invalid user admin from 198.51.100.25 port 49154 ssh2",
  "<134>1 2026-09-30T12:00:08Z FW-EDGE-01 sshd 4125 - - Accepted password for alice from 10.10.10.50 port 50221 ssh2",
  "<86>1 2026-09-30T12:00:15Z LAB-PC-01 sudo 1289 - - alice : TTY=pts/0 ; COMMAND=/usr/bin/cat /etc/shadow"
];

const SAMPLE_WINDOWS_EVENT = [
  {
    "EventID": 1,
    "Computer": "WORKSTATION-01",
    "EventData": {
      "TargetUserName": "alice",
      "ProcessName": "powershell.exe",
      "CommandLine": "powershell.exe -NonI -W Hidden -Enc SQBFAFgA...",
      "SourceIp": "198.51.100.25",
      "DestinationIp": "10.10.10.20"
    }
  },
  {
    "EventID": 3,
    "Computer": "WORKSTATION-01",
    "EventData": {
      "TargetUserName": "alice",
      "ProcessName": "curl.exe",
      "SourceIp": "10.10.10.20",
      "DestinationIp": "198.51.100.25"
    }
  }
];

export const LogCollectors: React.FC = () => {
  const [collectorStats, setCollectorStats] = useState<any>(null);
  const [syslogInput, setSyslogInput] = useState(SAMPLE_SYSLOGS.join('\n'));
  const [ingesting, setIngesting] = useState(false);
  const [ingestResult, setIngestResult] = useState<any>(null);
  const [selectedFormat, setSelectedFormat] = useState<'syslog' | 'windows' | 'cloudtrail'>('syslog');

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const stats = await api.getCollectorStats();
      setCollectorStats(stats);
    } catch (err) {
      console.error('Failed to load collector stats', err);
    }
  };

  const handleIngestSyslog = async () => {
    setIngesting(true);
    setIngestResult(null);
    try {
      const lines = syslogInput.split('\n').filter(l => l.trim().length > 0);
      const res = await api.ingestSyslog(lines, 'enterprise-syslog-ingest');
      setIngestResult(res);
    } catch (err: any) {
      alert(`Ingestion failed: ${err.message}`);
    } finally {
      setIngesting(false);
    }
  };

  const handleIngestWindows = async () => {
    setIngesting(true);
    setIngestResult(null);
    try {
      const res = await api.ingestWindowsEvents(SAMPLE_WINDOWS_EVENT);
      setIngestResult(res);
    } catch (err: any) {
      alert(`Ingestion failed: ${err.message}`);
    } finally {
      setIngesting(false);
    }
  };

  const handleIngestCloudTrail = async () => {
    setIngesting(true);
    setIngestResult(null);
    try {
      const res = await api.ingestWebhookTelemetry({
        event_type: 'privilege',
        action: 'AssumeRoleWithWebIdentity',
        source_ip: '198.51.100.25',
        host: 'us-east-1-vpc',
        user: 'service-account-ci',
        process: 'AWS::STS::AssumeRole'
      }, 'AWS-CloudTrail');
      setIngestResult({ status: 'success', events_created: 1, alerts_triggered: res.alerts_triggered || 0 });
    } catch (err: any) {
      alert(`CloudTrail ingestion failed: ${err.message}`);
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Radio className="w-7 h-7 text-cyan-400 animate-pulse" />
            Live Log Collectors & Telemetry Ingestion
          </h1>
          <p className="text-[#888] text-sm mt-1">
            Real-time RFC 5424/3164 Syslog listeners, Windows EVTX/Sysmon event parsers, and Cloud Webhooks.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Activity className="w-3.5 h-3.5" />
            3 Active Collectors
          </span>
        </div>
      </div>

      {/* Ingest Result Banner */}
      {ingestResult && (
        <div className="p-4 rounded-none bg-cyan-950/40 border border-cyan-500/30 text-cyan-200 flex items-center justify-between shadow-none">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-cyan-400" />
            <div>
              <div className="text-sm font-semibold">Telemetry Ingested Successfully!</div>
              <div className="text-xs text-cyan-300/80">
                Created <b>{ingestResult.events_created || ingestResult.messages_received || 1}</b> normalized events & triggered <b>{ingestResult.alerts_triggered || 0}</b> detection alerts into Security Graph.
              </div>
            </div>
          </div>
          <button onClick={() => setIngestResult(null)} className="text-xs text-cyan-400 hover:underline">Clear</button>
        </div>
      )}

      {/* Collector Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          {
            title: 'Syslog UDP/TCP (RFC 5424/3164)',
            port: 'Port 514 / REST API',
            endpoint: '/api/collectors/syslog',
            status: 'ONLINE',
            codecs: 'Linux Auth, Firewalls, SSHD'
          },
          {
            title: 'Windows Event / Sysmon',
            port: 'EVTX / JSON Streaming',
            endpoint: '/api/collectors/windows-event',
            status: 'ONLINE',
            codecs: 'EventID 1, 3, 4624, 4625, 4672'
          },
          {
            title: 'Cloud Security Webhooks',
            port: 'HTTPS REST Webhook',
            endpoint: '/api/collectors/webhook',
            status: 'ONLINE',
            codecs: 'AWS CloudTrail, Okta, GitHub'
          }
        ].map((c, i) => (
          <div key={i} className="bg-[#0d1322] border border-[#333] rounded-none p-5 shadow-none">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                {c.status}
              </span>
              <span className="text-[11px] font-mono text-slate-500">{c.port}</span>
            </div>
            <h3 className="font-semibold text-slate-200 text-sm">{c.title}</h3>
            <div className="mt-2 text-xs text-cyan-400/90 font-mono bg-[#0a0a0a] px-2.5 py-1 rounded border border-[#333] truncate">
              {c.endpoint}
            </div>
            <div className="mt-3 text-[11px] text-[#888]">
              Supported: <span className="text-[#ccc] font-medium">{c.codecs}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Interactive Log Ingestion Console */}
      <div className="bg-[#0d1322] border border-[#333] rounded-none p-6 shadow-none space-y-4">
        <div className="flex items-center justify-between border-b border-[#333] pb-4">
          <div className="flex items-center gap-2">
            <Terminal className="w-5 h-5 text-cyan-400" />
            <h2 className="text-lg font-semibold text-slate-100">Live Log Ingestion & Normalizer Console</h2>
          </div>
          <div className="flex items-center gap-2">
            {(['syslog', 'windows', 'cloudtrail'] as const).map((fmt) => (
              <button
                key={fmt}
                onClick={() => setSelectedFormat(fmt)}
                className={`px-3 py-1.5 rounded-none text-xs font-medium transition-all ${
                  selectedFormat === fmt
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                    : 'bg-[#0a0a0a] text-[#888] border border-[#333] hover:text-slate-200'
                }`}
              >
                {fmt === 'syslog' ? 'Syslog Messages' : fmt === 'windows' ? 'Windows Sysmon' : 'AWS CloudTrail'}
              </button>
            ))}
          </div>
        </div>

        {selectedFormat === 'syslog' && (
          <div className="space-y-3">
            <label className="block text-xs font-medium text-[#888]">
              Raw Syslog Stream (RFC 5424 / RFC 3164 Standard)
            </label>
            <textarea
              rows={6}
              value={syslogInput}
              onChange={(e) => setSyslogInput(e.target.value)}
              className="w-full bg-[#050505] font-mono text-xs text-emerald-400/90 border border-[#333] rounded-none p-4 focus:outline-none focus:border-cyan-500 leading-relaxed"
            />
            <div className="flex justify-between items-center pt-2">
              <span className="text-xs text-slate-500">Auto-detects IP addresses, SSH failures, sudo commands & processes</span>
              <button
                onClick={handleIngestSyslog}
                disabled={ingesting}
                className="px-5 py-2.5 rounded-none bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-sm flex items-center gap-2 transition-all shadow-none shadow-cyan-600/20 disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
                {ingesting ? 'Streaming to Core...' : 'Ingest & Correlate Live Logs'}
              </button>
            </div>
          </div>
        )}

        {selectedFormat === 'windows' && (
          <div className="space-y-3">
            <label className="block text-xs font-medium text-[#888]">
              Windows Security & Sysmon Event JSON Array
            </label>
            <pre className="w-full bg-[#050505] font-mono text-xs text-cyan-300 border border-[#333] rounded-none p-4 overflow-x-auto max-h-48">
              {JSON.stringify(SAMPLE_WINDOWS_EVENT, null, 2)}
            </pre>
            <div className="flex justify-between items-center pt-2">
              <span className="text-xs text-slate-500">Maps Process Creation (EventID 1) & Network Connect (EventID 3)</span>
              <button
                onClick={handleIngestWindows}
                disabled={ingesting}
                className="px-5 py-2.5 rounded-none bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-sm flex items-center gap-2 transition-all shadow-none shadow-cyan-600/20 disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
                {ingesting ? 'Processing EVTX...' : 'Ingest Windows Sysmon Events'}
              </button>
            </div>
          </div>
        )}

        {selectedFormat === 'cloudtrail' && (
          <div className="space-y-3">
            <label className="block text-xs font-medium text-[#888]">
              Cloud Webhook Payload (AWS CloudTrail / Okta System Log)
            </label>
            <div className="bg-[#050505] font-mono text-xs text-amber-300 border border-[#333] rounded-none p-4">
              {JSON.stringify({
                source: "AWS-CloudTrail",
                eventName: "AssumeRoleWithWebIdentity",
                sourceIPAddress: "198.51.100.25",
                userIdentity: { userName: "service-account-ci" },
                awsRegion: "us-east-1"
              }, null, 2)}
            </div>
            <div className="flex justify-between items-center pt-2">
              <span className="text-xs text-slate-500">Extracts Cloud Identity & anomalous geo-IP endpoints</span>
              <button
                onClick={handleIngestCloudTrail}
                disabled={ingesting}
                className="px-5 py-2.5 rounded-none bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-sm flex items-center gap-2 transition-all shadow-none shadow-cyan-600/20 disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
                {ingesting ? 'Dispatching Webhook...' : 'Ingest CloudTrail Telemetry'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

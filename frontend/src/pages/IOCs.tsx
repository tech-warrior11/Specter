import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { 
  Database, Search, Filter, Globe, Hash, Tag, RefreshCw, Zap
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const IOCs: React.FC = () => {
  const navigate = useNavigate();
  const [iocs, setIocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL');

  const [liveQuery, setLiveQuery] = useState('198.51.100.25');
  const [liveResult, setLiveResult] = useState<any>(null);
  const [queryingLive, setQueryingLive] = useState(false);
  const [syncingFeeds, setSyncingFeeds] = useState(false);

  useEffect(() => {
    loadIOCs();
  }, []);

  const loadIOCs = async () => {
    setLoading(true);
    try {
      const data = await api.getIOCs();
      setIocs(data);
    } catch (err) {
      console.error('Failed to load IOCs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLiveLookup = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!liveQuery) return;
    setQueryingLive(true);
    try {
      const res = await api.liveIOCLookup(liveQuery.trim());
      setLiveResult(res);
    } catch (err: any) {
      alert(`Live Lookup failed: ${err.message}`);
    } finally {
      setQueryingLive(false);
    }
  };

  const handleSyncFeeds = async () => {
    setSyncingFeeds(true);
    try {
      const res = await api.syncLiveFeeds('ALL');
      alert(`CTI Feed Sync Complete! Synced ${res.iocs_added || res.total_synced_sample} community threat indicators.`);
      await loadIOCs();
    } catch (err: any) {
      alert(`Feed sync failed: ${err.message}`);
    } finally {
      setSyncingFeeds(false);
    }
  };

  const getIocIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'ip': return <Globe className="w-4 h-4 text-[#00ff9d]" />;
      case 'domain': return <Globe className="w-4 h-4 text-[#00ff9d]" />;
      case 'hash': case 'sha256': return <Hash className="w-4 h-4 text-[#00ff9d]" />;
      default: return <Tag className="w-4 h-4 text-[#888]" />;
    }
  };

  const filtered = iocs.filter(ioc => {
    const val = (ioc.value || '').toLowerCase();
    const type = (ioc.ioc_type || ioc.type || '').toUpperCase();
    const matchSearch = val.includes(search.toLowerCase()) ||
      (ioc.source && ioc.source.toLowerCase().includes(search.toLowerCase()));
    const matchType = typeFilter === 'ALL' || type === typeFilter;
    return matchSearch && matchType;
  });

  return (
    <div className="space-y-6 font-mono text-sm max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 bg-[#0a0a0a] border border-[#333]">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2 uppercase tracking-widest">
            <Database className="w-5 h-5 text-[#00ff9d]" />
            Intel Feeds
          </h1>
          <p className="text-xs text-[#888] mt-1 uppercase tracking-wide">
            Real-time reputation feeds & automated correlation.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleSyncFeeds}
            disabled={syncingFeeds}
            className="px-4 py-2 bg-[#111] border border-[#333] hover:border-[#00ff9d] text-[#ccc] text-[10px] font-bold uppercase tracking-widest flex items-center gap-2 transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncingFeeds ? 'animate-spin' : ''}`} />
            {syncingFeeds ? 'SYNCING...' : 'SYNC FEEDS'}
          </button>
          <span className="px-3 py-2 bg-[#111] border border-[#333] text-[10px] uppercase text-[#888]">
            IOCs: <strong className="text-[#00ff9d]">{iocs.length}</strong>
          </span>
        </div>
      </div>

      {/* Live Threat Reputation Checker Box */}
      <div className="bg-[#0a0a0a] border border-[#333] p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2 uppercase tracking-widest">
            <Zap className="w-4 h-4 text-[#00ff9d]" />
            Live Reputation Lookup
          </h2>
        </div>

        <form onSubmit={handleLiveLookup} className="flex gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#555]" />
            <input
              type="text"
              value={liveQuery}
              onChange={(e) => setLiveQuery(e.target.value)}
              placeholder="ENTER IP, DOMAIN, HASH..."
              className="w-full bg-[#111] border border-[#333] pl-10 pr-4 py-2 text-xs text-[#ccc] placeholder-[#555] focus:outline-none focus:border-[#00ff9d] uppercase"
            />
          </div>
          <button
            type="submit"
            disabled={queryingLive}
            className="px-6 py-2 bg-white text-black hover:bg-[#00ff9d] font-bold text-[10px] uppercase tracking-widest flex items-center gap-2 transition-all disabled:opacity-50"
          >
            {queryingLive ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            CHECK
          </button>
        </form>

        {/* Live Result Display */}
        {liveResult && (
          <div className="mt-4 p-4 bg-[#111] border border-[#222] flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-bold text-[#fff] text-xs">{liveResult.query_value}</span>
                <span className={`px-2 py-0.5 text-[9px] font-bold uppercase tracking-widest ${
                  liveResult.risk_rating === 'CRITICAL' ? 'bg-[#ff4444]/10 text-[#ff4444] border border-[#ff4444]/30' :
                  liveResult.risk_rating === 'HIGH' ? 'bg-[#ffaa00]/10 text-[#ffaa00] border border-[#ffaa00]/30' :
                  'bg-[#00ff9d]/10 text-[#00ff9d] border border-[#00ff9d]/30'
                }`}>
                  {liveResult.risk_rating} ({liveResult.reputation_score}/100)
                </span>
                <span className="text-[10px] text-[#888] uppercase tracking-widest">Type: {liveResult.detected_type}</span>
              </div>
              <div className="text-[10px] text-[#aaa] uppercase tracking-widest mt-2">
                Actor: <b className="text-[#ff4444]">{liveResult.threat_actor}</b> | Categories: {liveResult.categories.join(', ')}
              </div>
            </div>

            <div className="text-right text-[10px] text-[#555] uppercase tracking-widest space-y-1">
              <div>Providers: <span className="text-[#aaa]">{liveResult.providers_queried.join(', ')}</span></div>
              <div>Confidence: <span className="text-[#00ff9d] font-bold">{Math.round(liveResult.confidence * 100)}%</span></div>
            </div>
          </div>
        )}
      </div>

      {/* Filter Bar */}
      <div className="bg-[#0a0a0a] border border-[#333] p-4 flex flex-col md:flex-row items-center gap-4">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#555]" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="SEARCH IOC CATALOG..."
            className="w-full bg-[#111] border border-[#333] pl-10 pr-4 py-2 text-xs text-[#ccc] placeholder-[#555] focus:outline-none focus:border-[#00ff9d] uppercase"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="w-4 h-4 text-[#555]" />
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-[#111] border border-[#333] px-3 py-2 text-xs text-[#ccc] focus:outline-none focus:border-[#00ff9d] uppercase"
          >
            <option value="ALL">ALL TYPES</option>
            <option value="IP">IPS</option>
            <option value="DOMAIN">DOMAINS</option>
            <option value="HASH">HASHES</option>
          </select>
        </div>
      </div>

      {/* IOC Catalog Table */}
      <div className="bg-[#0a0a0a] border border-[#333] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-[#111] text-[#888] uppercase tracking-widest font-bold border-b border-[#333]">
              <tr>
                <th className="p-3">Type</th>
                <th className="p-3">Indicator</th>
                <th className="p-3">Class</th>
                <th className="p-3">Confidence</th>
                <th className="p-3">Source</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#222] text-[#ccc]">
              {filtered.map((ioc) => (
                <tr key={ioc.id || ioc.value} className="hover:bg-[#111] transition-colors">
                  <td className="p-3 flex items-center gap-2">
                    {getIocIcon(ioc.ioc_type || ioc.type || 'ip')}
                    <span className="font-bold uppercase text-[10px] tracking-widest">{ioc.ioc_type || ioc.type}</span>
                  </td>
                  <td className="p-3 font-bold text-white">
                    {ioc.value}
                  </td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 text-[9px] font-bold uppercase tracking-widest ${
                      (ioc.classification || '').toLowerCase() === 'malicious' ? 'bg-[#ff4444]/10 text-[#ff4444] border border-[#ff4444]/30' :
                      (ioc.classification || '').toLowerCase() === 'suspicious' ? 'bg-[#ffaa00]/10 text-[#ffaa00] border border-[#ffaa00]/30' :
                      'bg-[#222] text-[#888]'
                    }`}>
                      {ioc.classification || 'suspicious'}
                    </span>
                  </td>
                  <td className="p-3">
                    <div className="flex items-center gap-3">
                      <div className="flex gap-[1px] w-20 h-2">
                        {Array.from({ length: 100 }).map((_, i) => (
                          <div 
                            key={i} 
                            className={`flex-1 h-full ${i < Math.round((ioc.confidence || 0.8) * 100) ? 'bg-[#00ff9d]' : 'bg-[#1a1a1a]'}`} 
                          />
                        ))}
                      </div>
                      <span className="text-[9px] font-bold text-[#888]">{Math.round((ioc.confidence || 0.8) * 100)}%</span>
                    </div>
                  </td>
                  <td className="p-3 text-[10px] uppercase tracking-widest text-[#888]">{ioc.source || 'Specter-Core'}</td>
                  <td className="p-3 text-right">
                    <button
                      onClick={() => navigate(`/hunting`)}
                      className="px-3 py-1.5 bg-[#111] hover:bg-[#1a1a1a] border border-[#333] hover:border-[#00ff9d] text-[#ccc] text-[9px] font-bold uppercase tracking-widest transition-all inline-flex items-center gap-2"
                    >
                      <Search className="w-3 h-3" />
                      Hunt
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

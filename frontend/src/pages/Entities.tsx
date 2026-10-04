import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { EntityItem } from '../types';
import { 
  Users, Server, Globe, Terminal, FileText, Search, ShieldAlert, ExternalLink, Crosshair, Filter
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const Entities: React.FC = () => {
  const navigate = useNavigate();
  const [entities, setEntities] = useState<EntityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedType, setSelectedType] = useState('ALL');
  const [selectedCriticality, setSelectedCriticality] = useState('ALL');
  const [selectedEntity, setSelectedEntity] = useState<EntityItem | null>(null);

  useEffect(() => {
    loadEntities();
  }, []);

  const loadEntities = async () => {
    setLoading(true);
    try {
      const data = await api.fetchApi<EntityItem[]>('/entities');
      setEntities(data);
    } catch (err) {
      console.error('Failed to load entities:', err);
    } finally {
      setLoading(false);
    }
  };

  const getEntityIcon = (type: string) => {
    switch (type.toUpperCase()) {
      case 'USER': return <Users className="w-4 h-4 text-[#00ff9d]" />;
      case 'HOST': return <Server className="w-4 h-4 text-[#00ff9d]" />;
      case 'IP': return <Globe className="w-4 h-4 text-[#00ff9d]" />;
      case 'PROCESS': return <Terminal className="w-4 h-4 text-[#00ff9d]" />;
      case 'FILE': return <FileText className="w-4 h-4 text-[#00ff9d]" />;
      default: return <Server className="w-4 h-4 text-[#888]" />;
    }
  };

  const filtered = entities.filter(e => {
    const matchSearch = e.value.toLowerCase().includes(search.toLowerCase()) || e.id.toLowerCase().includes(search.toLowerCase());
    const matchType = selectedType === 'ALL' || e.entity_type.toUpperCase() === selectedType;
    const matchCrit = selectedCriticality === 'ALL' || e.criticality.toUpperCase() === selectedCriticality;
    return matchSearch && matchType && matchCrit;
  });

  return (
    <div className="space-y-6 font-mono text-sm max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 bg-[#0a0a0a] border border-[#333]">
        <div>
          <h1 className="text-xl font-bold text-white uppercase tracking-widest flex items-center gap-2">
            <Users className="w-5 h-5 text-[#00ff9d]" />
            Asset Directory
          </h1>
          <p className="text-xs text-[#888] mt-1 uppercase tracking-wide">
            Correlated entity catalog, continuous risk scoring, and graph pivots.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 bg-[#111] border border-[#333] text-[10px] uppercase text-[#888]">
            Total Assets: <strong className="text-[#00ff9d]">{entities.length}</strong>
          </span>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-[#0a0a0a] border border-[#333] p-4 flex flex-col md:flex-row items-center gap-4">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#555]" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="SEARCH IDENTITY, HOSTNAME, IP, PROCESS..."
            className="w-full bg-[#111] border border-[#333] pl-10 pr-4 py-2 text-xs text-[#ccc] placeholder-[#555] focus:outline-none focus:border-[#00ff9d] uppercase"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="w-4 h-4 text-[#555]" />
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="bg-[#111] border border-[#333] px-3 py-2 text-xs text-[#ccc] focus:outline-none focus:border-[#00ff9d] uppercase"
          >
            <option value="ALL">ALL TYPES</option>
            <option value="USER">USERS</option>
            <option value="HOST">HOSTS</option>
            <option value="IP">IPS</option>
            <option value="DOMAIN">DOMAINS</option>
            <option value="PROCESS">PROCESSES</option>
            <option value="FILE">FILES</option>
          </select>

          <select
            value={selectedCriticality}
            onChange={(e) => setSelectedCriticality(e.target.value)}
            className="bg-[#111] border border-[#333] px-3 py-2 text-xs text-[#ccc] focus:outline-none focus:border-[#00ff9d] uppercase"
          >
            <option value="ALL">ALL CRITICALITY</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>
        </div>
      </div>

      {/* Grid Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Entity Table */}
        <div className="lg:col-span-2 bg-[#0a0a0a] border border-[#333] overflow-hidden flex flex-col">
          <div className="p-4 border-b border-[#333] flex items-center justify-between">
            <h2 className="text-sm font-bold text-white flex items-center gap-2 uppercase tracking-widest">
              <Filter className="w-4 h-4 text-[#00ff9d]" />
              Assets ({filtered.length})
            </h2>
          </div>

          <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
            {loading ? (
              <div className="p-8 text-center text-[#00ff9d] font-mono text-xs animate-pulse uppercase tracking-widest">
                Querying asset catalog...
              </div>
            ) : filtered.length === 0 ? (
              <div className="p-8 text-center text-[#555] text-xs uppercase tracking-widest">
                No assets matched current filter criteria.
              </div>
            ) : (
              <table className="w-full text-left text-xs border-collapse">
                <thead className="bg-[#111] sticky top-0 text-[#888] font-bold uppercase tracking-widest border-b border-[#333]">
                  <tr>
                    <th className="p-3">Type</th>
                    <th className="p-3">Identifier</th>
                    <th className="p-3">Criticality</th>
                    <th className="p-3 text-right">Risk</th>
                    <th className="p-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#222]">
                  {filtered.map((entity) => {
                    const isSelected = selectedEntity?.id === entity.id;
                    return (
                      <tr 
                        key={entity.id}
                        onClick={() => setSelectedEntity(entity)}
                        className={`hover:bg-[#111] cursor-pointer transition-colors ${isSelected ? 'bg-[#1a1a1a] border-l-2 border-[#00ff9d]' : ''}`}
                      >
                        <td className="p-3 flex items-center gap-2">
                          {getEntityIcon(entity.entity_type)}
                          <span className="text-[#ccc] text-[10px] uppercase tracking-widest">{entity.entity_type}</span>
                        </td>
                        <td className="p-3 font-bold text-[#eee] max-w-[200px] truncate" title={entity.value}>
                          {entity.value}
                        </td>
                        <td className="p-3">
                          <span className={`px-2 py-0.5 text-[9px] font-bold uppercase tracking-widest ${
                            entity.criticality === 'CRITICAL' ? 'bg-[#ff4444]/10 text-[#ff4444] border border-[#ff4444]/30' :
                            entity.criticality === 'HIGH' ? 'bg-[#ffaa00]/10 text-[#ffaa00] border border-[#ffaa00]/30' :
                            'bg-[#222] text-[#888]'
                          }`}>
                            {entity.criticality}
                          </span>
                        </td>
                        <td className="p-3 text-right">
                          <span className="text-xs font-bold text-[#ff4444]">
                            {entity.risk_score}/100
                          </span>
                        </td>
                        <td className="p-3 text-right">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/graph?node=${encodeURIComponent(entity.id)}`);
                            }}
                            className="p-1.5 hover:bg-[#222] text-[#555] hover:text-[#00ff9d] transition-colors"
                            title="Explore in Graph"
                          >
                            <ExternalLink className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Selected Entity Details Panel */}
        <div className="bg-[#0a0a0a] border border-[#333] p-5 flex flex-col space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2 border-b border-[#333] pb-3 uppercase tracking-widest">
            <ShieldAlert className="w-4 h-4 text-[#00ff9d]" />
            Dossier
          </h2>

          {selectedEntity ? (
            <div className="space-y-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  {getEntityIcon(selectedEntity.entity_type)}
                  <span className="text-[10px] uppercase tracking-widest text-[#888]">
                    {selectedEntity.entity_type}
                  </span>
                </div>
                <div className="text-sm font-bold text-white break-all">
                  {selectedEntity.value}
                </div>
              </div>

              {/* Risk Gauge */}
              <div className="p-3.5 bg-[#111] border border-[#333] space-y-2">
                <div className="flex justify-between items-center text-[10px] uppercase tracking-widest">
                  <span className="text-[#888]">Risk Index</span>
                  <span className="font-bold text-[#ff4444]">
                    {selectedEntity.risk_score} / 100
                  </span>
                </div>
                <div className="flex gap-[2px] w-full h-3">
                  {Array.from({ length: 100 }).map((_, i) => (
                    <div 
                      key={i} 
                      className={`flex-1 h-full ${i < selectedEntity.risk_score ? 'bg-[#ff4444]' : 'bg-[#1a1a1a]'}`} 
                    />
                  ))}
                </div>
                <p className="text-[9px] text-[#555] uppercase tracking-widest mt-2">
                  Factor derived from alerts & graph centrality.
                </p>
              </div>

              {/* Timestamps */}
              <div className="grid grid-cols-2 gap-2 text-[10px] uppercase tracking-widest">
                <div className="p-2.5 bg-[#111] border border-[#222]">
                  <div className="text-[#555]">First Seen</div>
                  <div className="text-[#ccc] mt-0.5 truncate">{new Date(selectedEntity.first_seen).toLocaleString()}</div>
                </div>
                <div className="p-2.5 bg-[#111] border border-[#222]">
                  <div className="text-[#555]">Last Seen</div>
                  <div className="text-[#ccc] mt-0.5 truncate">{new Date(selectedEntity.last_seen).toLocaleString()}</div>
                </div>
              </div>

              {/* Quick Pivots */}
              <div className="pt-2 space-y-2">
                <h3 className="text-[10px] font-bold text-[#555] uppercase tracking-widest">Pivots</h3>
                <div className="grid grid-cols-1 gap-2">
                  <button
                    onClick={() => navigate(`/graph?node=${encodeURIComponent(selectedEntity.id)}`)}
                    className="w-full py-2 px-3 bg-[#111] hover:bg-[#1a1a1a] border border-[#333] hover:border-[#00ff9d] text-[#ccc] text-[10px] font-bold uppercase tracking-widest flex items-center justify-center gap-2 transition-all"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    Inspect Graph
                  </button>
                  <button
                    onClick={() => navigate(`/hunting`)}
                    className="w-full py-2 px-3 bg-[#111] hover:bg-[#1a1a1a] border border-[#333] hover:border-[#00ff9d] text-[#ccc] text-[10px] font-bold uppercase tracking-widest flex items-center justify-center gap-2 transition-all"
                  >
                    <Crosshair className="w-3.5 h-3.5 text-[#00ff9d]" />
                    Hunt Telemetry
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-[#555]">
              <Users className="w-10 h-10 text-[#333] mb-2" />
              <p className="text-[10px] uppercase tracking-widest">Select an asset.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('Specter_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {})
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  fetchApi,

  // Dashboard
  getDashboardSummary: () => fetchApi<any>('/dashboard/summary'),
  getDashboardTimeline: () => fetchApi<any>('/dashboard/timeline'),

  // Events
  getEvents: (params: string = '') => fetchApi<any[]>(`/events?${params}`),
  getEventById: (id: string) => fetchApi<any>(`/events/${id}`),

  // Entities
  getEntities: (params: string = '') => fetchApi<any[]>(`/entities?${params}`),
  getEntityById: (id: string) => fetchApi<any>(`/entities/${id}`),

  // Graph
  getNeighborhood: (nodeId: string, depth: number = 1) =>
    fetchApi<any>(`/graph/neighborhood?node_id=${encodeURIComponent(nodeId)}&depth=${depth}`),
  getAttackPath: (source: string, target: string) =>
    fetchApi<any>(`/graph/path?source_id=${encodeURIComponent(source)}&target_id=${encodeURIComponent(target)}`),
  getGraphStats: () => fetchApi<any>('/graph/stats'),

  // Threat Hunting
  searchHunt: (query: string, timeWindowHours: number = 48) =>
    fetchApi<any>('/hunting/search', {
      method: 'POST',
      body: JSON.stringify({ query, time_window_hours: timeWindowHours })
    }),
  getSavedHunts: () => fetchApi<any[]>('/hunting/saved'),

  // Detections & Alerts
  getDetectionRules: () => fetchApi<any[]>('/detections/rules'),
  getAlerts: (params: string = '') => fetchApi<any[]>(`/alerts?${params}`),
  updateAlertStatus: (id: string, status: string, fpReason?: string) =>
    fetchApi<any>(`/alerts/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status, fp_reason: fpReason })
    }),

  // Investigations & Incidents
  getInvestigations: () => fetchApi<any[]>('/investigations'),
  getInvestigationWorkbench: (id: string) => fetchApi<any>(`/investigations/${id}`),
  createInvestigation: (data: any) =>
    fetchApi<any>('/investigations', { method: 'POST', body: JSON.stringify(data) }),
  addInvestigationNote: (id: string, content: string) =>
    fetchApi<any>(`/investigations/${id}/notes`, { method: 'POST', body: JSON.stringify({ content }) }),
  getIncidents: () => fetchApi<any[]>('/incidents'),

  // MITRE & IOCs
  getMitreMatrix: () => fetchApi<any>('/mitre/coverage'),
  getIOCs: () => fetchApi<any[]>('/iocs'),
  getAnomalies: () => fetchApi<any[]>('/behavior/anomalies'),

  // Scenarios & Training
  getScenarios: () => fetchApi<any[]>('/scenarios'),
  runScenario: (scenarioId: string) =>
    fetchApi<any>(`/scenarios/${scenarioId}/run`, { method: 'POST' }),
  submitTraining: (scenarioId: string, data: any) =>
    fetchApi<any>(`/scenarios/${scenarioId}/training_submit`, { method: 'POST', body: JSON.stringify(data) }),

  // Grounded AI
  askAI: (investigationId: string, question: string) =>
    fetchApi<any>('/ai/investigate', {
      method: 'POST',
      body: JSON.stringify({ investigation_id: investigationId, question })
    }),

  // Reports & PDF
  generateReport: (data: any) =>
    fetchApi<any>('/reports/generate', { method: 'POST', body: JSON.stringify(data) }),
  downloadReportPDF: async (investigationId: string = 'INV-001') => {
    const token = localStorage.getItem('Specter_token');
    const headers: Record<string, string> = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const response = await fetch(`${API_BASE}/reports/${investigationId}/pdf`, { headers });
    if (!response.ok) throw new Error('PDF download failed');
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Specter_forensic_report_${investigationId}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  },

  // SOAR Active Defense & Playbooks
  getSOARActions: () => fetchApi<any[]>('/soar/actions'),
  executeSOARAction: (data: any) =>
    fetchApi<any>('/soar/execute', { method: 'POST', body: JSON.stringify(data) }),
  rollbackSOARAction: (actionId: string) =>
    fetchApi<any>(`/soar/actions/${actionId}/rollback`, { method: 'POST' }),
  getSOARPlaybooks: () => fetchApi<any[]>('/soar/playbooks'),
  getWebhooks: () => fetchApi<any[]>('/soar/webhooks'),
  testWebhook: (data: any) =>
    fetchApi<any>('/soar/webhooks/test', { method: 'POST', body: JSON.stringify(data) }),

  // Live Threat Intelligence (CTI)
  liveIOCLookup: (value: string, iocType?: string) =>
    fetchApi<any>(`/iocs/live-lookup?value=${encodeURIComponent(value)}${iocType ? `&ioc_type=${iocType}` : ''}`, { method: 'POST' }),
  syncLiveFeeds: (feedName: string = 'ALL') =>
    fetchApi<any>(`/iocs/sync-feeds?feed_name=${feedName}`, { method: 'POST' }),

  // Log Collectors & Real Telemetry Ingestion
  getCollectorStats: () => fetchApi<any>('/collectors/stats'),
  ingestSyslog: (rawMessages: string[], sourceTag: string = 'firewall-syslog') =>
    fetchApi<any>('/collectors/syslog', {
      method: 'POST',
      body: JSON.stringify({ raw_messages: rawMessages, source_tag: sourceTag })
    }),
  ingestWindowsEvents: (events: any[]) =>
    fetchApi<any>('/collectors/windows-event', {
      method: 'POST',
      body: JSON.stringify(events)
    }),
  ingestWebhookTelemetry: (payload: any, source: string = 'CloudTrail') =>
    fetchApi<any>('/collectors/webhook', {
      method: 'POST',
      body: JSON.stringify({ source, payload })
    })
};


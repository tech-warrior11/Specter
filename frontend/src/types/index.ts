export interface EventItem {
  id: string;
  timestamp: string;
  source: string;
  event_type: string;
  action: string;
  user_identity?: string;
  host?: string;
  source_ip?: string;
  destination_ip?: string;
  domain?: string;
  process_name?: string;
  parent_process?: string;
  file_path?: string;
  severity: string;
}

export interface GraphNode {
  id: string;
  label: string;
  properties: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relation_type: string;
  properties: Record<string, any>;
}

export interface SubGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface AttackPath {
  path_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  confidence: number;
  risk_score: number;
  stage_progression: string[];
  evidence_event_ids: string[];
  description: string;
}

export interface AlertItem {
  id: string;
  rule_id?: string;
  title: string;
  description: string;
  severity: string;
  confidence: number;
  risk_score: number;
  status: string;
  event_ids: string[];
  entity_ids: string[];
  mitre_tactic?: string;
  mitre_technique?: string;
  first_seen: string;
  last_seen: string;
  created_at: string;
}

export interface EntityItem {
  id: string;
  entity_type: string;
  value: string;
  risk_score: number;
  criticality: string;
  first_seen: string;
  last_seen: string;
}

export interface InvestigationItem {
  id: string;
  title: string;
  status: string;
  priority: string;
  summary?: string;
  risk_score: number;
  root_entities: string[];
  alerts_count: number;
  events_count: number;
  created_at: string;
  updated_at: string;
}

export interface TimelineEntry {
  timestamp: string;
  entry_type: string;
  title: string;
  description: string;
  entity?: string;
  severity: string;
  reference_id: string;
}

export interface InvestigationWorkbench {
  id: string;
  title: string;
  status: string;
  priority: string;
  summary?: string;
  confidence: number;
  risk_score: number;
  assigned_to?: string;
  root_entities: string[];
  related_events: string[];
  related_alerts: string[];
  mitre_tactics: string[];
  created_at: string;
  updated_at: string;
  subgraph: SubGraph;
  attack_paths: AttackPath[];
  timeline: TimelineEntry[];
  notes: any[];
  evidence: any[];
  security_story: string;
}

export interface DashboardSummary {
  kpis: {
    total_events: number;
    total_alerts: number;
    open_investigations: number;
    open_incidents: number;
    anomalies_detected: number;
    active_iocs: number;
    graph_nodes: number;
    graph_edges: number;
  };
  alerts_by_severity: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    informational: number;
  };
  mitre_distribution: { tactic: string; count: number }[];
  high_risk_entities: { id: string; type: string; value: string; risk_score: number; criticality: string }[];
}

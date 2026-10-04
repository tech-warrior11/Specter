import networkx as nx
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from app.schemas.graph import GraphNode, GraphEdge, SubGraph

logger = logging.getLogger("specter.graph.in_memory")


class InMemoryGraphEngine:
    """High-performance NetworkX Directed MultiGraph implementation for Security Graph analysis."""

    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def clear(self):
        self.graph.clear()

    def add_or_update_node(self, node_id: str, label: str, properties: Optional[Dict[str, Any]] = None):
        """Idempotently adds or updates a node in the security graph."""
        props = properties or {}
        if self.graph.has_node(node_id):
            existing_props = self.graph.nodes[node_id].get("properties", {})
            existing_props.update(props)
            self.graph.nodes[node_id]["properties"] = existing_props
            self.graph.nodes[node_id]["label"] = label
        else:
            self.graph.add_node(node_id, label=label, properties=props)

    def add_or_update_edge(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: Optional[Dict[str, Any]] = None,
        edge_id: Optional[str] = None
    ):
        """Idempotently creates or increments a directed relationship."""
        props = properties or {}
        eid = edge_id or f"rel:{source_id}->{target_id}:{relation_type}"

        # Ensure endpoints exist
        if not self.graph.has_node(source_id):
            self.add_or_update_node(source_id, label="Unknown")
        if not self.graph.has_node(target_id):
            self.add_or_update_node(target_id, label="Unknown")

        # Check for existing edge with the same key
        if self.graph.has_edge(source_id, target_id, key=eid):
            existing_props = self.graph.edges[source_id, target_id, eid].get("properties", {})
            existing_props.update(props)
            existing_props["weight"] = existing_props.get("weight", 1) + 1
            self.graph.edges[source_id, target_id, eid]["properties"] = existing_props
        else:
            self.graph.add_edge(
                source_id,
                target_id,
                key=eid,
                relation_type=relation_type,
                properties=props
            )

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        if not self.graph.has_node(node_id):
            return None
        data = self.graph.nodes[node_id]
        return GraphNode(
            id=node_id,
            label=data.get("label", "Entity"),
            properties=data.get("properties", {})
        )

    def get_neighborhood(self, node_id: str, depth: int = 1, max_nodes: int = 100) -> SubGraph:
        """Extracts k-hop neighborhood around a node (both in and out directions)."""
        if not self.graph.has_node(node_id):
            return SubGraph(nodes=[], edges=[])

        # Subgraph via BFS up to depth
        sub_nodes = {node_id}
        current_layer = {node_id}

        for _ in range(depth):
            next_layer = set()
            for n in current_layer:
                successors = set(self.graph.successors(n))
                predecessors = set(self.graph.predecessors(n))
                next_layer.update(successors | predecessors)
            sub_nodes.update(next_layer)
            current_layer = next_layer
            if len(sub_nodes) >= max_nodes:
                break

        # Build SubGraph Pydantic model
        nodes_list = []
        for n in list(sub_nodes)[:max_nodes]:
            ndata = self.graph.nodes[n]
            nodes_list.append(GraphNode(
                id=n,
                label=ndata.get("label", "Entity"),
                properties=ndata.get("properties", {})
            ))

        edges_list = []
        for u, v, key, data in self.graph.edges(sub_nodes, data=True, keys=True):
            if u in sub_nodes and v in sub_nodes:
                edges_list.append(GraphEdge(
                    id=key,
                    source=u,
                    target=v,
                    relation_type=data.get("relation_type", "RELATED_TO"),
                    properties=data.get("properties", {})
                ))

        return SubGraph(nodes=nodes_list, edges=edges_list)

    def find_shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """Finds shortest undirected path between source and target (attack chains can be bidirectional)."""
        if not self.graph.has_node(source_id) or not self.graph.has_node(target_id):
            return None
        try:
            undirected_graph = self.graph.to_undirected()
            return nx.shortest_path(undirected_graph, source=source_id, target=target_id)
        except nx.NetworkXNoPath:
            return None

    def calculate_centrality(self) -> Dict[str, float]:
        """Calculates degree centrality for identifying high-influence pivot entities."""
        if len(self.graph) == 0:
            return {}
        return nx.degree_centrality(self.graph)

    def get_stats(self) -> Dict[str, int]:
        return {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges()
        }


# Global singleton in-memory graph instance
in_memory_graph = InMemoryGraphEngine()

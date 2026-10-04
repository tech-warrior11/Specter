import pytest
from app.graph.in_memory_graph import InMemoryGraphEngine
from app.graph.graph_algorithms import GraphAlgorithms


@pytest.fixture
def graph_engine():
    engine = InMemoryGraphEngine()
    engine.clear()
    return engine


def test_node_and_edge_management(graph_engine: InMemoryGraphEngine):
    # Add nodes
    graph_engine.add_or_update_node("user:alice", label="User", properties={"risk": 20})
    graph_engine.add_or_update_node("host:LAB-01", label="Host", properties={"os": "Linux"})

    # Add edge
    graph_engine.add_or_update_edge("user:alice", "host:LAB-01", "ACCESSED_HOST", properties={"method": "ssh"})

    node = graph_engine.get_node("user:alice")
    assert node is not None
    assert node.label == "User"
    assert node.properties["risk"] == 20

    stats = graph_engine.get_stats()
    assert stats["node_count"] == 2
    assert stats["edge_count"] == 1


def test_neighborhood_traversal(graph_engine: InMemoryGraphEngine):
    graph_engine.add_or_update_node("ip:10.10.10.50", "IP")
    graph_engine.add_or_update_node("user:alice", "User")
    graph_engine.add_or_update_node("host:LAB-01", "Host")
    graph_engine.add_or_update_node("proc:powershell", "Process")

    graph_engine.add_or_update_edge("ip:10.10.10.50", "user:alice", "AUTH_TARGET")
    graph_engine.add_or_update_edge("user:alice", "host:LAB-01", "ACCESSED_HOST")
    graph_engine.add_or_update_edge("host:LAB-01", "proc:powershell", "EXECUTED_PROCESS")

    subgraph = graph_engine.get_neighborhood("user:alice", depth=1)
    node_ids = [n.id for n in subgraph.nodes]
    assert "user:alice" in node_ids
    assert "ip:10.10.10.50" in node_ids
    assert "host:LAB-01" in node_ids
    assert len(subgraph.edges) == 2


def test_attack_path_reconstruction(graph_engine: InMemoryGraphEngine):
    # Build complete multi-hop attack chain
    graph_engine.add_or_update_node("ip:198.51.100.25", "IP")
    graph_engine.add_or_update_node("user:admin", "User")
    graph_engine.add_or_update_node("host:DC-01", "Host")
    graph_engine.add_or_update_node("file:passwords.txt", "File")

    graph_engine.add_or_update_edge("ip:198.51.100.25", "user:admin", "LOGGED_FROM_IP", properties={"event_id": "evt-1"})
    graph_engine.add_or_update_edge("user:admin", "host:DC-01", "ACCESSED_HOST", properties={"event_id": "evt-2"})
    graph_engine.add_or_update_edge("host:DC-01", "file:passwords.txt", "ACCESSED_FILE", properties={"event_id": "evt-3"})

    path = GraphAlgorithms.detect_attack_path("ip:198.51.100.25", "file:passwords.txt", engine=graph_engine)
    assert path is not None
    assert len(path.nodes) == 4
    assert len(path.edges) == 3
    assert len(path.evidence_event_ids) == 3
    assert "INITIAL_ACCESS" in path.stage_progression
    assert path.risk_score >= 80


def test_blast_radius_calculation(graph_engine: InMemoryGraphEngine):
    graph_engine.add_or_update_node("user:compromised", "User")
    graph_engine.add_or_update_node("host:srv1", "Host")
    graph_engine.add_or_update_node("host:srv2", "Host")

    graph_engine.add_or_update_edge("user:compromised", "host:srv1", "ACCESSED_HOST")
    graph_engine.add_or_update_edge("user:compromised", "host:srv2", "ACCESSED_HOST")

    blast = GraphAlgorithms.calculate_blast_radius("user:compromised", depth=1, engine=graph_engine)
    assert blast["root_entity"] == "user:compromised"
    assert blast["hosts_count"] == 2
    assert blast["total_impacted_entities"] == 3

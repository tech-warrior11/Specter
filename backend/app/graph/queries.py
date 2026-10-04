"""Parameterized Cypher queries for Neo4j production clusters."""

CYPHER_GET_NEIGHBORHOOD = """
MATCH (n {id: $node_id})-[r]-(m)
RETURN n, r, m
LIMIT $limit
"""

CYPHER_SHORTEST_PATH = """
MATCH (start {id: $source_id}), (end {id: $target_id})
MATCH p = shortestPath((start)-[*..10]->(end))
RETURN p
"""

CYPHER_COUNT_STATS = """
MATCH (n)
OPTIONAL MATCH ()-[r]->()
RETURN count(DISTINCT n) as node_count, count(DISTINCT r) as edge_count
"""

from typing import Dict, Any, List, Optional
import logging
from neo4j import GraphDatabase, AsyncGraphDatabase, AsyncDriver
from app.config import settings
from app.schemas.graph import GraphNode, GraphEdge, SubGraph
from app.graph.in_memory_graph import in_memory_graph

logger = logging.getLogger("specter.graph.neo4j")


class Neo4jClient:
    def __init__(self):
        self.driver: Optional[AsyncDriver] = None
        self.use_in_memory = settings.USE_IN_MEMORY_GRAPH

    async def connect(self):
        if self.use_in_memory:
            logger.info("Operating in In-Memory Security Graph mode.")
            return

        try:
            self.driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
            )
            # Verify connectivity
            async with self.driver.session() as session:
                result = await session.run("RETURN 1 as test")
                record = await result.single()
                if record and record["test"] == 1:
                    logger.info("Successfully established connection to Neo4j Security Graph database.")
        except Exception as e:
            logger.warning(f"Neo4j connection failed: {e}. Falling back to In-Memory Security Graph.")
            self.use_in_memory = True

    async def close(self):
        if self.driver:
            await self.driver.close()

    async def merge_node(self, label: str, node_id: str, properties: Dict[str, Any]):
        """Idempotently creates or updates a node using parameterized Cypher."""
        # Always update in-memory graph for lightning fast hybrid queries
        in_memory_graph.add_or_update_node(node_id, label, properties)

        if not self.use_in_memory and self.driver:
            query = f"""
            MERGE (n:`{label}` {{id: $node_id}})
            ON CREATE SET n += $props, n.created_at = timestamp()
            ON MATCH SET n += $props, n.updated_at = timestamp()
            """
            try:
                async with self.driver.session() as session:
                    await session.run(query, node_id=node_id, props=properties)
            except Exception as e:
                logger.error(f"Error merging Neo4j node {node_id}: {e}")

    async def merge_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: Dict[str, Any]
    ):
        """Idempotently creates or updates a relationship using parameterized Cypher."""
        in_memory_graph.add_or_update_edge(source_id, target_id, relation_type, properties)

        if not self.use_in_memory and self.driver:
            query = f"""
            MATCH (a {{id: $source_id}})
            MATCH (b {{id: $target_id}})
            MERGE (a)-[r:`{relation_type}`]->(b)
            ON CREATE SET r += $props, r.weight = 1
            ON MATCH SET r += $props, r.weight = coalesce(r.weight, 1) + 1
            """
            try:
                async with self.driver.session() as session:
                    await session.run(query, source_id=source_id, target_id=target_id, props=properties)
            except Exception as e:
                logger.error(f"Error merging Neo4j relationship {source_id}->{target_id}: {e}")

    async def get_neighborhood(self, node_id: str, depth: int = 1, max_nodes: int = 100) -> SubGraph:
        """Fetches k-hop neighborhood from graph."""
        if self.use_in_memory or not self.driver:
            return in_memory_graph.get_neighborhood(node_id, depth=depth, max_nodes=max_nodes)
            
        query = f"""
        MATCH (n {{id: $node_id}})
        OPTIONAL MATCH path = (n)-[*1..{depth}]-(m)
        WITH collect(distinct n) + collect(distinct m) as nodes, collect(path) as paths
        UNWIND nodes as node
        WITH node, paths WHERE node IS NOT NULL
        WITH collect(distinct node) as final_nodes, paths
        UNWIND (CASE paths WHEN [] THEN [null] ELSE paths END) as p
        UNWIND (CASE p WHEN null THEN [] ELSE relationships(p) END) as rel
        RETURN final_nodes as nodes, collect(distinct rel) as edges
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(query, node_id=node_id)
                record = await result.single()
                
                nodes_list = []
                edges_list = []
                
                if record:
                    neo_nodes = record.get("nodes", [])
                    neo_edges = record.get("edges", [])
                    
                    for n in neo_nodes[:max_nodes]:
                        if n is not None:
                            labels = list(n.labels)
                            label = labels[0] if labels else "Entity"
                            n_id = n.get("id", "unknown")
                            props = dict(n.items())
                            nodes_list.append(GraphNode(id=n_id, label=label, properties=props))
                            
                    for r in neo_edges:
                        if r is not None:
                            try:
                                src_id = r.nodes[0].get("id", "unknown")
                                tgt_id = r.nodes[1].get("id", "unknown")
                            except Exception:
                                src_id = "unknown"
                                tgt_id = "unknown"
                                
                            edges_list.append(GraphEdge(
                                id=f"rel:{src_id}->{tgt_id}:{r.type}",
                                source=src_id,
                                target=tgt_id,
                                relation_type=r.type,
                                properties=dict(r.items())
                            ))
                            
                return SubGraph(nodes=nodes_list, edges=edges_list)
        except Exception as e:
            logger.error(f"Error querying Neo4j neighborhood: {e}")
            return in_memory_graph.get_neighborhood(node_id, depth=depth, max_nodes=max_nodes)


neo4j_client = Neo4jClient()

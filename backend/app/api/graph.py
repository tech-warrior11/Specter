from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, Dict, Any

from app.schemas.graph import SubGraph, AttackPath
from app.graph.in_memory_graph import in_memory_graph
from app.graph.neo4j_client import neo4j_client
from app.graph.graph_algorithms import graph_algorithms

router = APIRouter(prefix="/graph", tags=["Graph Explorer"])


@router.get("/neighborhood", response_model=SubGraph)
async def get_graph_neighborhood(
    node_id: str = Query(..., description="Root entity identifier (e.g., 'user:alice')"),
    depth: int = Query(1, ge=1, le=3),
    max_nodes: int = Query(100, ge=10, le=500)
):
    """Retrieves subgraph neighborhood centered at a designated entity."""
    return await neo4j_client.get_neighborhood(node_id, depth=depth, max_nodes=max_nodes)


@router.get("/path", response_model=AttackPath)
async def get_attack_path(
    source_id: str = Query(..., description="Starting entity ID (e.g. 'ip:198.51.100.25')"),
    target_id: str = Query(..., description="Destination entity ID (e.g. 'file:c:/passwords.txt')")
):
    """Computes shortest directed attack path and reconstructs stage progression."""
    path = await graph_algorithms.detect_attack_path(source_id, target_id)
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No security path observed between {source_id} and {target_id}"
        )
    return path


@router.get("/stats")
async def get_graph_statistics():
    """Returns global graph topology metrics and top central pivot nodes."""
    stats = in_memory_graph.get_stats()
    centrality = in_memory_graph.calculate_centrality()
    top_pivots = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "node_count": stats["node_count"],
        "edge_count": stats["edge_count"],
        "top_pivot_entities": [{"id": k, "centrality_score": round(v, 4)} for k, v in top_pivots]
    }

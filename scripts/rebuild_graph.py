"""ThreatGraph X - Graph Rebuild Utility
Iterates through all historical normalized security events in PostgreSQL and reconstructs graph topology.
"""

import asyncio
import sys
import os
from sqlalchemy import select

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database.database import AsyncSessionLocal
from app.models.event import Event
from app.services.entity_extractor import entity_extractor
from app.services.graph_builder import graph_builder
from app.graph.in_memory_graph import in_memory_graph


async def rebuild_graph():
    print("[*] Rebuilding ThreatGraph X Security Graph from Event Store...")
    in_memory_graph.clear()

    async with AsyncSessionLocal() as session:
        stmt = select(Event).order_by(Event.timestamp)
        result = await session.execute(stmt)
        events = result.scalars().all()

        print(f"[*] Processing {len(events)} events for graph reconstruction...")
        total_ents = 0
        total_edges = 0

        for i, ev in enumerate(events, 1):
            entities = entity_extractor.extract_entities(ev)
            relationships = entity_extractor.extract_relationships(ev)

            ents_c, edges_c = await graph_builder.process_entities_and_relationships(
                session=session,
                entities=entities,
                relationships=relationships
            )
            total_ents += ents_c
            total_edges += edges_c

            if i % 1000 == 0 or i == len(events):
                print(f"    -> Processed {i}/{len(events)} events...")

        await session.commit()

        stats = in_memory_graph.get_stats()
        print(f"\n[+] Graph Rebuild Complete!")
        print(f"    Total Nodes:         {stats['node_count']}")
        print(f"    Total Relationships: {stats['edge_count']}")


if __name__ == "__main__":
    asyncio.run(rebuild_graph())

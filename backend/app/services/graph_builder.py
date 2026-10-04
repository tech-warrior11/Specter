from typing import List, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import logging
from app.models.entity import Entity, EntityRelationship
from app.schemas.entity import ExtractedEntity
from app.graph.neo4j_client import neo4j_client

logger = logging.getLogger("specter.services.graph_builder")


class GraphBuilder:
    """Synchronizes extracted entities and relationships across PostgreSQL and Neo4j/In-Memory graph."""

    @staticmethod
    async def process_entities_and_relationships(
        session: AsyncSession,
        entities: List[ExtractedEntity],
        relationships: List[Tuple[str, str, str, Dict[str, Any]]]
    ) -> Tuple[int, int]:
        entities_created = 0
        edges_created = 0
        now = datetime.now(timezone.utc)

        # 1. Process Nodes / Entities
        for ent in entities:
            # Update In-Memory Graph & Neo4j
            await neo4j_client.merge_node(
                label=ent.entity_type.capitalize(),
                node_id=ent.id,
                properties={"value": ent.value, "type": ent.entity_type}
            )

            # Check database for existing entity
            existing_ent = await session.get(Entity, ent.id)
            if existing_ent:
                existing_ent.last_seen = now
            else:
                new_ent = Entity(
                    id=ent.id,
                    entity_type=ent.entity_type,
                    value=ent.value,
                    risk_score=0.0,
                    criticality="medium",
                    first_seen=now,
                    last_seen=now
                )
                session.add(new_ent)
                await session.flush()
                entities_created += 1

        # 2. Process Relationships
        for src_id, tgt_id, rel_type, props in relationships:
            await neo4j_client.merge_relationship(
                source_id=src_id,
                target_id=tgt_id,
                relation_type=rel_type,
                properties=props
            )

            rel_id = f"rel:{src_id}->{tgt_id}:{rel_type}"
            existing_rel = await session.get(EntityRelationship, rel_id)

            if existing_rel:
                existing_rel.last_observed = now
                existing_rel.weight += 1
                ev_ids = list(existing_rel.evidence_event_ids or [])
                if "event_id" in props and props["event_id"] not in ev_ids:
                    ev_ids.append(props["event_id"])
                    existing_rel.evidence_event_ids = ev_ids
            else:
                ev_list = [props["event_id"]] if "event_id" in props else []
                new_rel = EntityRelationship(
                    id=rel_id,
                    source_entity_id=src_id,
                    target_entity_id=tgt_id,
                    relation_type=rel_type,
                    weight=1,
                    first_observed=now,
                    last_observed=now,
                    evidence_event_ids=ev_list
                )
                session.add(new_rel)
                await session.flush()
                edges_created += 1

        return entities_created, edges_created


graph_builder = GraphBuilder()

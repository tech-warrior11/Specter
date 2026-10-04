from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from app.schemas.event import EventCreate, BulkIngestionResponse
from app.models.event import Event
from app.services.normalization import normalization_engine
from app.services.entity_extractor import entity_extractor
from app.services.graph_builder import graph_builder

logger = logging.getLogger("specter.services.ingestion")


class IngestionService:
    """End-to-end ingestion pipeline for security telemetry."""

    @staticmethod
    async def ingest_event(session: AsyncSession, event_in: EventCreate) -> Tuple[Event, int, int]:
        # 1. Normalize
        normalized_event = normalization_engine.normalize(event_in)
        session.add(normalized_event)

        # 2. Extract Entities & Relationships
        entities = entity_extractor.extract_entities(normalized_event)
        relationships = entity_extractor.extract_relationships(normalized_event)

        # 3. Build Graph Nodes & Edges
        ents_created, edges_created = await graph_builder.process_entities_and_relationships(
            session=session,
            entities=entities,
            relationships=relationships
        )

        await session.commit()
        await session.refresh(normalized_event)

        return normalized_event, ents_created, edges_created

    @staticmethod
    async def ingest_bulk_events(session: AsyncSession, events_in: List[EventCreate]) -> BulkIngestionResponse:
        total_ents = 0
        total_edges = 0
        event_ids = []

        for event_in in events_in:
            normalized_event = normalization_engine.normalize(event_in)
            session.add(normalized_event)
            event_ids.append(normalized_event.id)

            entities = entity_extractor.extract_entities(normalized_event)
            relationships = entity_extractor.extract_relationships(normalized_event)

            ents_c, edges_c = await graph_builder.process_entities_and_relationships(
                session=session,
                entities=entities,
                relationships=relationships
            )
            total_ents += ents_c
            total_edges += edges_c

        await session.commit()

        return BulkIngestionResponse(
            received_count=len(events_in),
            ingested_count=len(events_in),
            extracted_entities_count=total_ents,
            graph_edges_created=total_edges,
            alerts_triggered_count=0,
            event_ids=event_ids
        )


ingestion_service = IngestionService()

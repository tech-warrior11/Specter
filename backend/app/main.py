from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging
from app.config import settings
from app.database.database import init_db

# Configure Structured Logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("specter.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Specter Security Core...")
    await init_db()
    
    # Load existing entity graph into in-memory graph engine
    try:
        from app.database.database import AsyncSessionLocal
        from app.models.entity import Entity, EntityRelationship
        from app.graph.in_memory_graph import in_memory_graph
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as session:
            ents = (await session.execute(select(Entity))).scalars().all()
            for e in ents:
                in_memory_graph.add_or_update_node(
                    node_id=e.id,
                    label=e.entity_type.capitalize(),
                    properties={"value": e.value, "type": e.entity_type, "risk_score": e.risk_score}
                )
            rels = (await session.execute(select(EntityRelationship))).scalars().all()
            for r in rels:
                in_memory_graph.add_or_update_edge(
                    source_id=r.source_entity_id,
                    target_id=r.target_entity_id,
                    relation_type=r.relation_type,
                    properties={"weight": r.weight},
                    edge_id=r.id
                )
            stats = in_memory_graph.get_stats()
            logger.info(f"Loaded {stats['node_count']} nodes and {stats['edge_count']} relationships into in-memory graph.")
    except Exception as e:
        logger.warning(f"Could not preload in-memory graph from database: {e}")

    logger.info("Specter Backend successfully initialized and ready for defense.")
    yield
    logger.info("Shutting down Specter Security Core...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Threat Hunting, Security Graph & Attack-Chain Intelligence Platform API",
    lifespan=lifespan
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security Headers & Latency Middleware
@app.middleware("http")
async def add_security_headers_and_metrics(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000

    # Defensive Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Process-Time-MS"] = f"{process_time:.2f}"
    return response


# Global Exception Handler (No sensitive leak)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred during processing. The incident has been audited.",
            "path": request.url.path
        }
    )


# Include Sub-Routers
from app.api.auth import router as auth_router
from app.api.events import router as events_router
from app.api.entities import router as entities_router
from app.api.graph import router as graph_router
from app.api.alerts import router as alerts_router
from app.api.detections import router as detections_router
from app.api.hunting import router as hunting_router
from app.api.behavior import router as behavior_router
from app.api.iocs import router as iocs_router
from app.api.mitre import router as mitre_router
from app.api.investigations import router as investigations_router
from app.api.incidents import router as incidents_router
from app.api.scenarios import router as scenarios_router
from app.api.ai import router as ai_router
from app.api.reports import router as reports_router
from app.api.dashboard import router as dashboard_router
from app.api.soar import router as soar_router
from app.api.collectors import router as collectors_router

app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(events_router, prefix=settings.API_V1_PREFIX)
app.include_router(entities_router, prefix=settings.API_V1_PREFIX)
app.include_router(graph_router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts_router, prefix=settings.API_V1_PREFIX)
app.include_router(detections_router, prefix=settings.API_V1_PREFIX)
app.include_router(hunting_router, prefix=settings.API_V1_PREFIX)
app.include_router(behavior_router, prefix=settings.API_V1_PREFIX)
app.include_router(iocs_router, prefix=settings.API_V1_PREFIX)
app.include_router(mitre_router, prefix=settings.API_V1_PREFIX)
app.include_router(investigations_router, prefix=settings.API_V1_PREFIX)
app.include_router(incidents_router, prefix=settings.API_V1_PREFIX)
app.include_router(scenarios_router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_router, prefix=settings.API_V1_PREFIX)
app.include_router(reports_router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)
app.include_router(soar_router, prefix=settings.API_V1_PREFIX)
app.include_router(collectors_router, prefix=settings.API_V1_PREFIX)


# Real-time WebSockets Stream for SOC Live Alerts
from fastapi import WebSocket, WebSocketDisconnect

class WebSocketManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

ws_manager = WebSocketManager()


@app.websocket("/ws/live-events")
async def websocket_live_stream(websocket: WebSocket):
    """WebSocket stream for real-time telemetry events and active alerts."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep-alive loop
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)



# Observability Endpoints
@app.get("/health", tags=["Observability"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "in_memory_graph": settings.USE_IN_MEMORY_GRAPH
    }


@app.get("/ready", tags=["Observability"])
async def readiness_check():
    return {
        "ready": True,
        "database": "connected",
        "graph": "connected" if not settings.USE_IN_MEMORY_GRAPH else "in-memory-active"
    }


@app.get("/metrics", tags=["Observability"])
async def system_metrics():
    return {
        "events_processed": 0,
        "alerts_generated": 0,
        "active_investigations": 0,
        "graph_nodes_count": 0,
        "graph_edges_count": 0
    }

@app.get("/seed", tags=["Setup"])
async def trigger_seeding():
    import asyncio
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from scripts.seed import seed_database
    # Run in background to avoid timeout
    asyncio.create_task(seed_database(100))
    return {"message": "Database seeding started in the background! Please wait 1-2 minutes before logging in."}


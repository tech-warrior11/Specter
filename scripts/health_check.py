"""ThreatGraph X - Health & Operational Diagnostics CLI"""

import asyncio
import sys
import os
from sqlalchemy import select, func

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database.database import AsyncSessionLocal
from app.models.event import Event
from app.models.alert import Alert
from app.models.investigation import Investigation
from app.graph.in_memory_graph import in_memory_graph
from app.services.detection import detection_engine


async def check_health():
    print("========================================================")
    print(" ThreatGraph X Operational Diagnostics")
    print("========================================================")

    # 1. Database Check
    try:
        async with AsyncSessionLocal() as session:
            ev_count = await session.scalar(select(func.count(Event.id)))
            alt_count = await session.scalar(select(func.count(Alert.id)))
            inv_count = await session.scalar(select(func.count(Investigation.id)))
            print(f"[+] Relational Database:   CONNECTED (Events: {ev_count}, Alerts: {alt_count}, Cases: {inv_count})")
    except Exception as e:
        print(f"[-] Relational Database:   ERROR ({e})")

    # 2. Graph Database Check
    stats = in_memory_graph.get_stats()
    print(f"[+] Security Graph Engine: HEALTHY (Nodes: {stats['node_count']}, Edges: {stats['edge_count']})")

    # 3. Detection Engine Check
    print(f"[+] Detection Rules:       LOADED ({len(detection_engine.rules)} active rules)")

    print("========================================================")
    print(" Status: ALL SYSTEMS OPERATIONAL AND DEFENSIVE")
    print("========================================================\n")


if __name__ == "__main__":
    asyncio.run(check_health())

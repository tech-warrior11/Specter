"""ThreatGraph X - Attack-Chain Scenario Simulation Runner CLI
Executes simulated multi-stage attack scenarios in a controlled defensive lab.
"""

import asyncio
import argparse
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database.database import AsyncSessionLocal, init_db
from app.services.scenario_runner import scenario_runner


async def main(scenario_id: str):
    await init_db()
    async with AsyncSessionLocal() as session:
        print(f"[*] Executing Attack Scenario: {scenario_id}...")
        try:
            result = await scenario_runner.run_scenario(session, scenario_id)
            print("\n========================================================")
            print(f" Scenario:            {result['scenario_name']} ({result['scenario_id']})")
            print(f" Status:              {result['status']}")
            print(f" Events Ingested:     {result['events_generated_count']}")
            print(f" Alerts Triggered:    {result['alerts_triggered_count']}")
            print(f" Risk Assessment:     {result['risk_assessment']['risk_score']}/100 ({result['risk_assessment']['category']})")
            print(f" Investigation ID:    {result['investigation_id']}")
            print("========================================================\n")
            print(result["security_story"])
        except Exception as e:
            print(f"[-] Error executing scenario: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ThreatGraph X Scenario")
    parser.add_argument("--scenario", type=str, default="SCENARIO-MULTI-001", help="Scenario ID or file prefix")
    args = parser.parse_args()
    asyncio.run(main(args.scenario))

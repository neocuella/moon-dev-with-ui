"""
Flow executor - Routes to mock or real executor based on configuration
"""

import asyncio
import logging
import time
import os
from datetime import datetime
from uuid import UUID
from typing import Dict, Any
from sqlalchemy.orm import Session

from src.database.connection import SessionLocal
from src.database.models import Execution, ExecutionStatus
from src.api.ws.manager import manager

logger = logging.getLogger(__name__)

# Configuration: Set to "real" to use real agents, "mock" for mock execution
EXECUTOR_MODE = os.getenv("EXECUTOR_MODE", "real")  # Default to real in Phase 2


async def run_flow_mock(execution_id: UUID, flow_definition: Dict[str, Any], db: Session):
    """
    Mock flow executor - simulates execution of nodes in sequence
    Kept for testing and fallback purposes
    """
    db = SessionLocal()  # Get fresh session for background task
    try:
        execution = db.query(Execution).filter(Execution.id == execution_id).first()
        if not execution:
            logger.error(f"❌ Execution not found: {execution_id}")
            return

        # Mark as running
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.utcnow()
        db.commit()

        logger.info(f"🚀 Starting mock execution {execution_id}")

        # Mock node processing
        nodes = flow_definition.get("nodes", [])
        results = {}
        start_time = time.time()
        logs = []

        for node in nodes:
            node_id = node.get("id", "unknown")
            node_type = node.get("data", {}).get("type", "unknown")

            log_msg = f"▶️  Executing node {node_id} ({node_type})"
            logs.append(log_msg)
            logger.info(log_msg)

            # Broadcast node start
            await manager.broadcast(
                str(execution_id),
                {
                    "type": "node_started",
                    "node_id": node_id,
                    "node_type": node_type,
                    "message": log_msg,
                }
            )

            # Simulate execution time
            await asyncio.sleep(0.5)

            # Mock result
            results[node_id] = {
                "status": "completed",
                "output": f"Mock output from {node_type}",
                "timestamp": datetime.utcnow().isoformat()
            }

            log_msg = f"✅ Node {node_id} completed"
            logs.append(log_msg)

            # Broadcast node completion
            await manager.broadcast(
                str(execution_id),
                {
                    "type": "node_completed",
                    "node_id": node_id,
                    "result": results[node_id],
                    "duration_ms": 500,
                }
            )

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Mark as completed
        execution.status = ExecutionStatus.COMPLETED
        execution.ended_at = datetime.utcnow()
        execution.duration_ms = duration_ms
        execution.node_results = results
        execution.logs = "\n".join(logs)

        db.commit()

        # Broadcast execution complete
        await manager.broadcast(
            str(execution_id),
            {
                "type": "execution_complete",
                "status": "completed",
                "duration_ms": duration_ms,
                "node_results": results,
            }
        )

        logger.info(f"✅ Mock execution completed: {execution_id} ({duration_ms}ms)")

    except Exception as e:
        logger.error(f"❌ Mock execution failed: {e}")
        execution = db.query(Execution).filter(Execution.id == execution_id).first()
        if execution:
            execution.status = ExecutionStatus.FAILED
            execution.ended_at = datetime.utcnow()
            execution.error = str(e)
            execution.logs = f"Execution failed: {str(e)}"
            db.commit()
    finally:
        db.close()


async def run_flow(execution_id: UUID, flow_definition: Dict[str, Any], db: Session):
    """
    Main flow executor - routes to real or mock executor based on EXECUTOR_MODE
    """
    if EXECUTOR_MODE == "mock":
        logger.info("📌 Using MOCK executor (Phase 1)")
        await run_flow_mock(execution_id, flow_definition, db)
    else:
        logger.info("📌 Using REAL executor (Phase 2)")
        # Import real executor here to avoid circular imports
        from src.api.orchestrator.real_executor import run_flow_real
        
        # Real executor needs fresh session
        db = SessionLocal()
        try:
            await run_flow_real(execution_id, flow_definition, db)
        finally:
            db.close()

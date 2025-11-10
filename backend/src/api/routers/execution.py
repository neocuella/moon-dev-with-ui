"""
Execution endpoints for running flows
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
import logging

from src.database.connection import get_db
from src.database.models import Flow, Execution, ExecutionStatus
from src.models.schemas import ExecutionCreate, ExecutionRead, ExecutionHistoryResponse
from src.api.orchestrator.executor import run_flow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/execution", tags=["execution"])


@router.post("/{flow_id}/run", response_model=ExecutionRead, status_code=201)
async def run_flow(
    flow_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start flow execution"""
    try:
        # Verify flow exists
        flow = db.query(Flow).filter(Flow.id == flow_id).first()
        if not flow:
            raise HTTPException(status_code=404, detail=f"Flow {flow_id} not found")
        
        # Create execution record
        execution = Execution(
            flow_id=flow_id,
            status=ExecutionStatus.PENDING,
            created_at=datetime.utcnow()
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        
        # Queue background task for execution (uses real or mock based on config)
        background_tasks.add_task(run_flow, execution.id, flow.definition, db)
        
        logger.info(f"✅ Execution started: {execution.id} for flow {flow_id}")
        return execution
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error starting execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{execution_id}", response_model=ExecutionRead)
async def get_execution(
    execution_id: UUID,
    db: Session = Depends(get_db)
):
    """Get execution status"""
    try:
        execution = db.query(Execution).filter(Execution.id == execution_id).first()
        if not execution:
            raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
        
        logger.info(f"✅ Retrieved execution: {execution_id}")
        return execution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{flow_id}/history", response_model=ExecutionHistoryResponse)
async def get_execution_history(
    flow_id: UUID,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get execution history for a flow"""
    try:
        # Verify flow exists
        flow = db.query(Flow).filter(Flow.id == flow_id).first()
        if not flow:
            raise HTTPException(status_code=404, detail=f"Flow {flow_id} not found")
        
        total = db.query(Execution).filter(Execution.flow_id == flow_id).count()
        executions = db.query(Execution).filter(
            Execution.flow_id == flow_id
        ).order_by(Execution.created_at.desc()).offset(offset).limit(limit).all()
        
        logger.info(f"✅ Retrieved execution history for flow {flow_id}")
        return ExecutionHistoryResponse(
            flow_id=flow_id,
            total=total,
            limit=limit,
            offset=offset,
            executions=executions
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving execution history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

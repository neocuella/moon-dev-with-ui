"""
Flow CRUD endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
import logging

from src.database.connection import get_db
from src.database.models import Flow
from src.models.schemas import FlowCreate, FlowUpdate, FlowRead, FlowListResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/flows", tags=["flows"])


@router.post("", response_model=FlowRead, status_code=201)
async def create_flow(
    flow_data: FlowCreate,
    db: Session = Depends(get_db)
):
    """Create a new flow"""
    try:
        flow = Flow(
            name=flow_data.name,
            description=flow_data.description,
            definition=flow_data.definition,
            tags=flow_data.tags
        )
        db.add(flow)
        db.commit()
        db.refresh(flow)
        logger.info(f"✅ Flow created: {flow.id} - {flow.name}")
        return flow
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creating flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=FlowListResponse)
async def list_flows(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List all flows with pagination"""
    try:
        total = db.query(Flow).count()
        flows = db.query(Flow).offset(offset).limit(limit).all()
        logger.info(f"✅ Listed {len(flows)} flows")
        return FlowListResponse(
            total=total,
            limit=limit,
            offset=offset,
            flows=flows
        )
    except Exception as e:
        logger.error(f"❌ Error listing flows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{flow_id}", response_model=FlowRead)
async def get_flow(
    flow_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific flow by ID"""
    try:
        flow = db.query(Flow).filter(Flow.id == flow_id).first()
        if not flow:
            raise HTTPException(status_code=404, detail=f"Flow {flow_id} not found")
        logger.info(f"✅ Retrieved flow: {flow_id}")
        return flow
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{flow_id}", response_model=FlowRead)
async def update_flow(
    flow_id: UUID,
    flow_data: FlowUpdate,
    db: Session = Depends(get_db)
):
    """Update a flow"""
    try:
        flow = db.query(Flow).filter(Flow.id == flow_id).first()
        if not flow:
            raise HTTPException(status_code=404, detail=f"Flow {flow_id} not found")
        
        # Update fields
        if flow_data.name is not None:
            flow.name = flow_data.name
        if flow_data.description is not None:
            flow.description = flow_data.description
        if flow_data.definition is not None:
            flow.definition = flow_data.definition
        if flow_data.tags is not None:
            flow.tags = flow_data.tags
        
        db.commit()
        db.refresh(flow)
        logger.info(f"✅ Flow updated: {flow_id}")
        return flow
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error updating flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{flow_id}", status_code=204)
async def delete_flow(
    flow_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a flow"""
    try:
        flow = db.query(Flow).filter(Flow.id == flow_id).first()
        if not flow:
            raise HTTPException(status_code=404, detail=f"Flow {flow_id} not found")
        
        db.delete(flow)
        db.commit()
        logger.info(f"✅ Flow deleted: {flow_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error deleting flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

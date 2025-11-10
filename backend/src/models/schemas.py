"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class ExecutionStatusEnum(str, Enum):
    """Execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


# ============= Flow Schemas =============

class FlowCreate(BaseModel):
    """Create flow request"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    definition: Dict[str, Any] = Field(..., description="Flow nodes and edges")
    tags: Optional[List[str]] = None


class FlowUpdate(BaseModel):
    """Update flow request"""
    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class FlowRead(BaseModel):
    """Flow response"""
    id: UUID
    name: str
    description: Optional[str]
    definition: Dict[str, Any]
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FlowListResponse(BaseModel):
    """Flow list response with pagination"""
    total: int
    limit: int
    offset: int
    flows: List[FlowRead]


# ============= Execution Schemas =============

class ExecutionCreate(BaseModel):
    """Create execution request"""
    flow_id: UUID
    override_config: Optional[Dict[str, Any]] = None


class ExecutionRead(BaseModel):
    """Execution response"""
    id: UUID
    flow_id: UUID
    status: ExecutionStatusEnum
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    logs: Optional[str]
    duration_ms: Optional[int]
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    
    # Phase 2 fields
    node_results: Optional[Dict[str, Any]] = None
    error_node_id: Optional[str] = None

    class Config:
        from_attributes = True


class ExecutionLogResponse(BaseModel):
    """Execution logs response"""
    execution_id: UUID
    logs: str
    created_at: datetime


class ExecutionHistoryResponse(BaseModel):
    """Execution history response with pagination"""
    flow_id: UUID
    total: int
    limit: int
    offset: int
    executions: List[ExecutionRead]


# ============= Agent Schemas =============

class AgentSchema(BaseModel):
    """Agent type definition"""
    type: str = Field(..., description="Agent type identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Agent description")
    configSchema: Dict[str, Any] = Field(..., description="JSON schema for configuration")
    inputs: List[str] = Field(default=[], description="Input field names")
    outputs: List[str] = Field(default=[], description="Output field names")


class AgentListResponse(BaseModel):
    """List of available agents"""
    agents: List[AgentSchema]
    total: int


# ============= Error Schemas =============

class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    code: str = Field(..., description="Error code for programmatic handling")
    details: Optional[Dict[str, Any]] = None


# ============= WebSocket Schemas =============

class WSMessage(BaseModel):
    """Base WebSocket message"""
    type: str  # "node_started", "node_completed", "log", "status_update"
    execution_id: UUID
    timestamp: datetime
    data: Dict[str, Any]


class WSNodeStarted(BaseModel):
    """Node started event"""
    type: str = "node_started"
    execution_id: UUID
    node_id: str
    node_type: str
    timestamp: datetime


class WSNodeCompleted(BaseModel):
    """Node completed event"""
    type: str = "node_completed"
    execution_id: UUID
    node_id: str
    result: Dict[str, Any]
    duration_ms: int
    timestamp: datetime


class WSLog(BaseModel):
    """Log event"""
    type: str = "log"
    execution_id: UUID
    message: str
    level: str = "info"  # info, warning, error
    timestamp: datetime


class WSExecutionComplete(BaseModel):
    """Execution complete event"""
    type: str = "execution_complete"
    execution_id: UUID
    status: ExecutionStatusEnum
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    duration_ms: int
    timestamp: datetime

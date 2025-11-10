"""
SQLAlchemy database models for flows and executions
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum

from .connection import Base


class ExecutionStatus(str, Enum):
    """Execution status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class Flow(Base):
    """Flow model - represents a workflow"""
    __tablename__ = "flows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    definition = Column(JSON, nullable=False)  # Nodes and edges
    tags = Column(JSON, nullable=True)  # ["trading", "risk-management"]
    flow_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' (reserved in SQLAlchemy)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    executions = relationship("Execution", back_populates="flow", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Flow(id={self.id}, name={self.name})>"


class Execution(Base):
    """Execution model - represents a flow execution"""
    __tablename__ = "executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flow_id = Column(UUID(as_uuid=True), ForeignKey("flows.id"), nullable=False, index=True)
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False)
    result = Column(JSON, nullable=True)  # Execution results/outputs
    error = Column(Text, nullable=True)  # Error message if failed
    logs = Column(Text, nullable=True)  # Execution logs
    duration_ms = Column(Integer, nullable=True)  # Total duration in milliseconds
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)

    # Phase 2 fields
    node_results = Column(JSON, nullable=True)  # Results from each node execution
    error_node_id = Column(String, nullable=True)  # Node ID where error occurred

    # Relationships
    flow = relationship("Flow", back_populates="executions")

    def __repr__(self):
        return f"<Execution(id={self.id}, flow_id={self.flow_id}, status={self.status})>"

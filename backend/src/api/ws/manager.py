"""
WebSocket connection manager for real-time execution updates
"""

import logging
from typing import Dict, List
from fastapi import WebSocket
import json
from datetime import datetime
from uuid import UUID

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for execution updates"""
    
    def __init__(self):
        # execution_id -> list of active connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, execution_id: str, websocket: WebSocket):
        """Register a new WebSocket connection"""
        await websocket.accept()
        
        if execution_id not in self.active_connections:
            self.active_connections[execution_id] = []
        
        self.active_connections[execution_id].append(websocket)
        logger.info(f"✅ WebSocket connected for execution {execution_id}")
    
    def disconnect(self, execution_id: str, websocket: WebSocket):
        """Unregister a WebSocket connection"""
        if execution_id in self.active_connections:
            self.active_connections[execution_id].remove(websocket)
            
            # Cleanup empty lists
            if not self.active_connections[execution_id]:
                del self.active_connections[execution_id]
            
            logger.info(f"✅ WebSocket disconnected for execution {execution_id}")
    
    async def broadcast(self, execution_id: str, message: Dict):
        """Broadcast message to all connected clients for an execution"""
        if execution_id not in self.active_connections:
            logger.debug(f"ℹ️  No active connections for execution {execution_id}")
            return
        
        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()
        
        disconnected = []
        for connection in self.active_connections[execution_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"❌ Error sending message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(execution_id, connection)
    
    def get_active_connections_count(self, execution_id: str) -> int:
        """Get count of active connections for an execution"""
        return len(self.active_connections.get(execution_id, []))


# Global connection manager instance
manager = ConnectionManager()

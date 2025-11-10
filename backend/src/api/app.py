"""
Moon Dev Flow UI - FastAPI Application
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager
from uuid import UUID

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routers
from src.api.routers import flows, agents, execution
from src.api.ws.manager import manager
from src.database.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info("🚀 Application startup")
    # Initialize database
    init_db()
    yield
    logger.info("🛑 Application shutdown")


# Create FastAPI app
app = FastAPI(
    title="Moon Dev Flow UI API",
    description="API for orchestrating AI trading agent flows",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(flows.router)
app.include_router(agents.router)
app.include_router(execution.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Moon Dev Flow UI API is running"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Moon Dev Flow UI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# WebSocket endpoint for real-time execution updates
@app.websocket("/ws/execution/{execution_id}")
async def websocket_endpoint(websocket: WebSocket, execution_id: str):
    """WebSocket endpoint for real-time execution updates"""
    await manager.connect(execution_id, websocket)
    try:
        while True:
            # Keep connection alive by receiving messages
            data = await websocket.receive_text()
            logger.debug(f"📨 Received from {execution_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(execution_id, websocket)
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        manager.disconnect(execution_id, websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

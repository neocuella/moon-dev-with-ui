"""
Agent listing and metadata endpoints
"""

from fastapi import APIRouter, HTTPException
import logging

from src.models.schemas import AgentSchema, AgentListResponse
from src.api.agents.loader import AgentLoader
from src.api.agents.agent_metadata import get_agent_metadata, can_connect, get_workflow_templates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/workflows")
async def list_workflow_templates():
    """Get pre-defined workflow templates"""
    try:
        templates = get_workflow_templates()
        logger.info(f"✅ Retrieved {len(templates)} workflow templates")
        return {"templates": templates, "total": len(templates)}
    except Exception as e:
        logger.error(f"❌ Error getting workflows: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflows: {str(e)}")


@router.post("/validate-connection")
async def validate_connection(request: dict):
    """Check if two agents can be connected"""
    try:
        source_agent = request.get("source_agent")
        target_agent = request.get("target_agent")
        result = can_connect(source_agent, target_agent)
        logger.info(f"✅ Connection validation: {source_agent} → {target_agent}: {result['valid']}")
        return result
    except Exception as e:
        logger.error(f"❌ Error validating connection: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("", response_model=AgentListResponse)
async def list_agents():
    """List all available agents from src/agents directory"""
    try:
        available_agents = AgentLoader.get_available_agents(refresh=True)
        
        # Convert to AgentSchema objects
        agents = []
        for agent_info in available_agents:
            # Try to get schema from agent module
            try:
                schema = AgentLoader.get_agent_config_schema(agent_info["name"])
            except Exception as e:
                logger.warning(f"Could not get schema for {agent_info['name']}: {e}")
                schema = {"type": "object", "properties": {}}
            
            # Get enhanced metadata from agent_metadata.py
            metadata = get_agent_metadata(agent_info["type"])
            
            agent = AgentSchema(
                type=agent_info["type"],
                name=agent_info.get("name", "").replace("_", " ").title(),
                description=metadata.get("description", agent_info.get("description", "")),
                configSchema=schema,
                inputs=metadata.get("inputs", []),
                outputs=metadata.get("outputs", [])
            )
            agents.append(agent)
        
        logger.info(f"✅ Listed {len(agents)} available agents")
        return AgentListResponse(
            agents=agents,
            total=len(agents)
        )
    
    except Exception as e:
        logger.error(f"❌ Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.get("/{agent_name}", response_model=AgentSchema)
async def get_agent_details(agent_name: str):
    """Get specific agent schema and metadata by name"""
    try:
        available = AgentLoader.get_available_agents()
        agent_info = next((a for a in available if a["name"] == agent_name), None)
        
        if not agent_info:
            logger.warning(f"⚠️  Agent not found: {agent_name}")
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        # Get schema from agent module
        schema = AgentLoader.get_agent_config_schema(agent_name)
        
        agent = AgentSchema(
            type=agent_info["type"],
            name=agent_info.get("name", agent_name).replace("_", " ").title(),
            description=agent_info.get("description", ""),
            configSchema=schema,
            inputs=[],
            outputs=[]
        )
        
        logger.info(f"✅ Retrieved agent details: {agent_name}")
        return agent
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting agent {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent details: {str(e)}")


@router.post("/{agent_name}/validate")
async def validate_agent_config(agent_name: str, config: dict):
    """Validate configuration for an agent"""
    try:
        is_valid, errors = AgentLoader.validate_agent_config(agent_name, config)
        
        return {
            "agent": agent_name,
            "valid": is_valid,
            "errors": errors
        }
    except Exception as e:
        logger.error(f"❌ Validation error for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

"""
Agent Loader - Dynamically discovers and loads Python trading agents
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class AgentLoader:
    """Discover, load, and manage Python trading agents"""

    # Cache for loaded agents
    _agent_cache: Dict[str, Any] = {}
    _available_agents_cache: Optional[List[Dict]] = None

    @staticmethod
    def get_available_agents(refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Scan src/agents/ directory and return list of available agents.

        Args:
            refresh: If True, re-scan directory instead of using cache

        Returns:
            List of dicts with agent metadata:
            [
                {
                    "name": "trading_agent",
                    "type": "trading",
                    "file_path": "src/agents/trading_agent.py"
                },
                ...
            ]
        """
        if AgentLoader._available_agents_cache and not refresh:
            return AgentLoader._available_agents_cache

        agents = []
        # Point to the main src/agents directory
        # From backend/src/api/agents/loader.py → go up 3 levels to backend/ → then ../src/agents
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent  # backend/
        agents_dir = project_root.parent / "src" / "agents"  # ../src/agents from backend/
        
        logger.info(f"🔍 Scanning for agents in: {agents_dir}")

        if not agents_dir.exists():
            logger.warning(f"Agents directory not found: {agents_dir}")
            logger.info(f"Current file: {current_file}")
            logger.info(f"Project root: {project_root}")
            return agents

        try:
            for file in sorted(agents_dir.glob("*_agent.py")):
                if file.name.startswith("_"):
                    continue

                agent_name = file.stem  # e.g., "trading_agent"
                agent_type = agent_name.replace("_agent", "")

                agents.append({
                    "name": agent_name,
                    "type": agent_type,
                    "file_path": str(file),
                    "description": f"{agent_type.replace('_', ' ').title()} Agent"
                })

                logger.debug(f"✅ Discovered agent: {agent_name}")

        except Exception as e:
            logger.error(f"❌ Error scanning agents directory: {e}")

        AgentLoader._available_agents_cache = agents
        return agents

    @staticmethod
    def load_agent(agent_name: str) -> Any:
        """
        Dynamically import and return an agent module.

        Args:
            agent_name: Name of agent (e.g., "trading_agent")

        Returns:
            Imported agent module

        Raises:
            ImportError: If agent module cannot be found or imported
            AttributeError: If agent module doesn't have main() function
        """
        # Return from cache if available
        if agent_name in AgentLoader._agent_cache:
            return AgentLoader._agent_cache[agent_name]

        try:
            # Import module
            module = importlib.import_module(f"src.agents.{agent_name}")

            # Verify module has main() function
            if not hasattr(module, "main"):
                raise AttributeError(
                    f"Agent {agent_name} doesn't have a main() function"
                )

            # Cache and return
            AgentLoader._agent_cache[agent_name] = module
            logger.debug(f"✅ Loaded agent: {agent_name}")
            return module

        except ImportError as e:
            logger.error(f"❌ Failed to import agent {agent_name}: {e}")
            raise
        except AttributeError as e:
            logger.error(f"❌ Agent validation failed for {agent_name}: {e}")
            raise

    @staticmethod
    def get_agent_config_schema(agent_name: str) -> Dict[str, Any]:
        """
        Get configuration schema for an agent.

        Returns dict with:
        {
            "parameters": [
                {
                    "name": "symbol",
                    "type": "string",
                    "required": True,
                    "description": "Trading pair symbol"
                },
                ...
            ]
        }

        Args:
            agent_name: Name of agent

        Returns:
            Configuration schema for agent
        """
        try:
            module = AgentLoader.load_agent(agent_name)

            # Check if agent has CONFIG_SCHEMA
            if hasattr(module, "CONFIG_SCHEMA"):
                return module.CONFIG_SCHEMA

            # Check if main() has type hints
            main_func = getattr(module, "main")
            sig = inspect.signature(main_func)

            parameters = []
            for param_name, param in sig.parameters.items():
                if param_name == "context":
                    continue

                param_info = {
                    "name": param_name,
                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "any",
                    "required": param.default == inspect.Parameter.empty,
                    "description": f"{param_name} parameter"
                }
                parameters.append(param_info)

            return {"parameters": parameters}

        except Exception as e:
            logger.warning(f"Could not determine schema for {agent_name}: {e}")
            return {"parameters": []}

    @staticmethod
    def validate_agent_config(agent_name: str, config: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate configuration against agent schema.

        Args:
            agent_name: Name of agent
            config: Configuration dict to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            schema = AgentLoader.get_agent_config_schema(agent_name)
            errors = []

            for param in schema.get("parameters", []):
                if param.get("required") and param["name"] not in config:
                    errors.append(f"Missing required parameter: {param['name']}")

            return len(errors) == 0, errors

        except Exception as e:
            return False, [f"Validation error: {str(e)}"]

    @staticmethod
    def clear_cache():
        """Clear the agent cache (useful for testing)"""
        AgentLoader._agent_cache.clear()
        AgentLoader._available_agents_cache = None
        logger.debug("🧹 Cleared agent cache")

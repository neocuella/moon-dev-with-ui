"""
Agent Context Handler - Intelligently calls agents with the right interface
Handles variations in agent signatures and parameter passing
"""

import inspect
import logging
from typing import Any, Dict, Callable

logger = logging.getLogger(__name__)


class AgentContextHandler:
    """
    Handles differences in agent interfaces.
    
    Different agents may expect:
    1. execution_context parameter: agent.main(execution_context={...})
    2. Individual config parameters: agent.main(symbol="BTC", amount=1000)
    3. config dict parameter: agent.main(config={...})
    4. No parameters: agent.main()
    """

    @staticmethod
    def call_agent(
        agent_module: Any,
        agent_name: str,
        config: Dict[str, Any],
        previous_results: Dict[str, Any],
        execution_id: str = None,
        node_id: str = None,
    ) -> Any:
        """
        Intelligently call an agent's main() function with appropriate parameters.

        Args:
            agent_module: Imported agent module
            agent_name: Name of agent (for logging)
            config: Configuration dict for the agent
            previous_results: Results from previous nodes
            execution_id: Current execution ID
            node_id: Current node ID

        Returns:
            Result from agent execution

        Raises:
            AttributeError: If agent doesn't have main() function
            TypeError: If can't determine valid calling signature
        """
        # Get the main function
        if not hasattr(agent_module, "main"):
            raise AttributeError(f"Agent {agent_name} doesn't have a main() function")

        main_func = getattr(agent_module, "main")
        sig = inspect.signature(main_func)
        parameters = list(sig.parameters.keys())

        logger.debug(f"🔍 Analyzing {agent_name}.main() signature: {parameters}")

        # Build execution context
        execution_context = {
            "execution_id": execution_id,
            "node_id": node_id,
            "config": config,
            "previous_results": previous_results,
        }

        # Strategy 1: Accept execution_context parameter
        if "execution_context" in parameters:
            logger.debug(f"✅ Calling {agent_name}.main(execution_context=...)")
            return main_func(execution_context=execution_context)

        # Strategy 2: Accept context parameter (alternative name)
        elif "context" in parameters:
            logger.debug(f"✅ Calling {agent_name}.main(context=...)")
            return main_func(context=execution_context)

        # Strategy 3: Accept config parameter
        elif "config" in parameters:
            logger.debug(f"✅ Calling {agent_name}.main(config=...)")
            return main_func(config=config)

        # Strategy 4: Unpack config as individual keyword arguments
        elif AgentContextHandler._can_unpack_config(main_func, config):
            logger.debug(f"✅ Calling {agent_name}.main(**config)")
            return main_func(**config)

        # Strategy 5: No parameters needed
        elif len(parameters) == 0:
            logger.debug(f"✅ Calling {agent_name}.main()")
            return main_func()

        # If we got here, we couldn't figure out how to call it
        raise TypeError(
            f"Cannot determine how to call {agent_name}.main(). "
            f"Parameters: {parameters}. "
            f"Expected one of: execution_context, context, config, or **kwargs unpacking."
        )

    @staticmethod
    def _can_unpack_config(func: Callable, config: Dict[str, Any]) -> bool:
        """
        Check if we can call func with **config.

        Args:
            func: Function to call
            config: Config dict to unpack

        Returns:
            True if func can accept **config, False otherwise
        """
        try:
            sig = inspect.signature(func)
            
            # Check if function accepts **kwargs
            for param in sig.parameters.values():
                if param.kind == inspect.Parameter.VAR_KEYWORD:
                    return True
            
            # Check if all config keys match parameter names
            for key in config.keys():
                if key not in sig.parameters:
                    return False
            
            return True
        except Exception as e:
            logger.warning(f"Could not check unpacking compatibility: {e}")
            return False

    @staticmethod
    def validate_agent_call(
        agent_module: Any,
        agent_name: str,
        config: Dict[str, Any],
    ) -> tuple[bool, str]:
        """
        Validate that we can call an agent with the given config.

        Args:
            agent_module: Imported agent module
            agent_name: Name of agent
            config: Configuration dict

        Returns:
            Tuple of (can_call: bool, error_message: str)
        """
        try:
            if not hasattr(agent_module, "main"):
                return False, f"Agent {agent_name} doesn't have main() function"

            main_func = getattr(agent_module, "main")
            sig = inspect.signature(main_func)
            parameters = list(sig.parameters.keys())

            # Check if any valid strategy applies
            if "execution_context" in parameters:
                return True, ""
            elif "context" in parameters:
                return True, ""
            elif "config" in parameters:
                return True, ""
            elif AgentContextHandler._can_unpack_config(main_func, config):
                return True, ""
            elif len(parameters) == 0:
                return True, ""

            return False, f"Cannot match agent signature: {parameters}"

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    @staticmethod
    def get_agent_interface_info(agent_module: Any) -> Dict[str, Any]:
        """
        Get information about how an agent's main() function expects to be called.

        Args:
            agent_module: Imported agent module

        Returns:
            Dict with interface information
        """
        try:
            if not hasattr(agent_module, "main"):
                return {"error": "No main() function found"}

            main_func = getattr(agent_module, "main")
            sig = inspect.signature(main_func)
            parameters = list(sig.parameters.keys())
            
            # Determine interface type
            interface_type = "unknown"
            if "execution_context" in parameters:
                interface_type = "execution_context"
            elif "context" in parameters:
                interface_type = "context"
            elif "config" in parameters:
                interface_type = "config"
            elif len(parameters) == 0:
                interface_type = "no_parameters"
            else:
                interface_type = "keyword_arguments"

            return {
                "interface_type": interface_type,
                "parameters": parameters,
                "return_annotation": str(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else "Any",
                "docstring": inspect.getdoc(main_func),
            }

        except Exception as e:
            return {"error": str(e)}

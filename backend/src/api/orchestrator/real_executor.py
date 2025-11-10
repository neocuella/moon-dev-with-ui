"""
Real Flow Executor - Actually runs the Python agents from src/agents/
"""

import asyncio
import logging
import time
import sys
import subprocess
import json
import tempfile
from pathlib import Path
from datetime import datetime
from uuid import UUID
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from src.database.models import Execution, ExecutionStatus
from src.api.ws.manager import manager

logger = logging.getLogger(__name__)


def topological_sort(nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
    """
    Sort nodes in execution order based on dependencies (edges)
    
    Returns nodes in order where dependencies come before dependents
    """
    # Build adjacency list (node_id -> list of dependent node_ids)
    node_map = {node["id"]: node for node in nodes}
    dependents = {node["id"]: [] for node in nodes}
    dependencies = {node["id"]: 0 for node in nodes}
    
    # Count incoming edges for each node
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source and target:
            dependents[source].append(target)
            dependencies[target] += 1
    
    # Start with nodes that have no dependencies
    queue = [node_id for node_id, count in dependencies.items() if count == 0]
    sorted_nodes = []
    
    while queue:
        # Process node
        node_id = queue.pop(0)
        sorted_nodes.append(node_map[node_id])
        
        # Reduce dependency count for dependents
        for dependent_id in dependents[node_id]:
            dependencies[dependent_id] -= 1
            if dependencies[dependent_id] == 0:
                queue.append(dependent_id)
    
    # Check for cycles
    if len(sorted_nodes) != len(nodes):
        raise ValueError("Cycle detected in flow! Cannot execute.")
    
    return sorted_nodes


async def execute_agent(agent_type: str, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single agent by running its Python file
    
    Args:
        agent_type: Type of agent (e.g., "risk", "trading", "sentiment")
        config: Node configuration from UI
        context: Execution context with outputs from previous nodes
    
    Returns:
        Dict with agent output
    """
    # Find agent file
    project_root = Path(__file__).parent.parent.parent.parent.parent
    agent_file = project_root / "src" / "agents" / f"{agent_type}_agent.py"
    
    if not agent_file.exists():
        raise FileNotFoundError(f"Agent file not found: {agent_file}")
    
    logger.info(f"📂 Executing agent: {agent_file}")
    
    # Create temporary file with context data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        context_file = f.name
        json.dump({
            "config": config,
            "context": context,
            "mode": "headless"  # Tell agent to run without user input
        }, f)
    
    try:
        # Run agent as subprocess
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(agent_file),
            "--context-file", context_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(project_root)
        )
        
        # Wait for completion with timeout
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300  # 5 minute timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            raise TimeoutError(f"Agent {agent_type} timed out after 5 minutes")
        
        # Parse output
        output_text = stdout.decode()
        error_text = stderr.decode()
        
        # Look for JSON output marker
        result = {
            "status": "completed" if process.returncode == 0 else "failed",
            "return_code": process.returncode,
            "stdout": output_text,
            "stderr": error_text
        }
        
        # Try to extract JSON result from output
        if "###RESULT###" in output_text:
            result_json = output_text.split("###RESULT###")[1].strip()
            try:
                result["data"] = json.loads(result_json)
            except json.JSONDecodeError:
                result["data"] = {"raw_output": result_json}
        else:
            result["data"] = {"raw_output": output_text}
        
        return result
        
    finally:
        # Cleanup temp file
        Path(context_file).unlink(missing_ok=True)


async def run_flow_real(execution_id: UUID, flow_definition: Dict[str, Any], db: Session):
    """
    Real flow executor - actually runs the Python agents
    
    Process:
    1. Topologically sort nodes based on connections
    2. Execute each agent in order
    3. Pass outputs from previous agents as context to next agents
    4. Stream progress via WebSocket
    5. Save results to database
    """
    try:
        execution = db.query(Execution).filter(Execution.id == execution_id).first()
        if not execution:
            logger.error(f"❌ Execution not found: {execution_id}")
            return
        
        # Mark as running
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"🚀 Starting REAL execution {execution_id}")
        
        # Extract nodes and edges
        nodes = flow_definition.get("nodes", [])
        edges = flow_definition.get("edges", [])
        
        if not nodes:
            raise ValueError("Flow has no nodes to execute")
        
        # Sort nodes by dependencies
        try:
            sorted_nodes = topological_sort(nodes, edges)
            logger.info(f"📊 Execution order: {[n['id'] for n in sorted_nodes]}")
        except ValueError as e:
            raise ValueError(f"Invalid flow structure: {str(e)}")
        
        # Execution context - stores outputs from previous nodes
        context = {}
        results = {}
        logs = []
        start_time = time.time()
        
        # Execute each node in order
        for idx, node in enumerate(sorted_nodes):
            node_id = node.get("id", "unknown")
            node_data = node.get("data", {})
            node_type = node_data.get("type", "unknown")
            node_config = node_data.get("config", {})
            
            log_msg = f"[{idx+1}/{len(sorted_nodes)}] ▶️  Executing {node_type} ({node_id})"
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
                    "progress": f"{idx}/{len(sorted_nodes)}"
                }
            )
            
            try:
                # Execute agent
                node_start = time.time()
                agent_result = await execute_agent(node_type, node_config, context)
                node_duration = int((time.time() - node_start) * 1000)
                
                # Store result in context for next nodes
                context[node_id] = agent_result.get("data", {})
                results[node_id] = {
                    "status": agent_result["status"],
                    "duration_ms": node_duration,
                    "output": agent_result.get("data"),
                    "return_code": agent_result.get("return_code"),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Log completion
                if agent_result["status"] == "completed":
                    log_msg = f"✅ {node_type} completed in {node_duration}ms"
                else:
                    log_msg = f"⚠️  {node_type} failed with code {agent_result['return_code']}"
                
                logs.append(log_msg)
                logger.info(log_msg)
                
                # Broadcast node completion
                await manager.broadcast(
                    str(execution_id),
                    {
                        "type": "node_completed",
                        "node_id": node_id,
                        "result": results[node_id],
                        "duration_ms": node_duration,
                    }
                )
                
            except Exception as e:
                error_msg = f"❌ {node_type} error: {str(e)}"
                logs.append(error_msg)
                logger.error(error_msg)
                
                results[node_id] = {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Broadcast node error
                await manager.broadcast(
                    str(execution_id),
                    {
                        "type": "node_error",
                        "node_id": node_id,
                        "error": str(e)
                    }
                )
                
                # Continue to next node (don't halt execution)
                continue
        
        # Calculate total duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Determine overall status
        failed_nodes = [nid for nid, res in results.items() if res["status"] == "failed"]
        overall_status = ExecutionStatus.FAILED if failed_nodes else ExecutionStatus.COMPLETED
        
        # Update execution record
        execution.status = overall_status
        execution.ended_at = datetime.utcnow()
        execution.duration_ms = duration_ms
        execution.node_results = results
        execution.logs = "\n".join(logs)
        
        if failed_nodes:
            execution.error = f"Failed nodes: {', '.join(failed_nodes)}"
        
        db.commit()
        
        # Broadcast execution complete
        await manager.broadcast(
            str(execution_id),
            {
                "type": "execution_complete",
                "status": overall_status.value,
                "duration_ms": duration_ms,
                "node_results": results,
                "failed_nodes": failed_nodes
            }
        )
        
        logger.info(f"✅ Execution completed: {execution_id} ({duration_ms}ms, status: {overall_status.value})")
        
    except Exception as e:
        logger.error(f"❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()
        
        execution = db.query(Execution).filter(Execution.id == execution_id).first()
        if execution:
            execution.status = ExecutionStatus.FAILED
            execution.ended_at = datetime.utcnow()
            execution.error = str(e)
            execution.logs = f"Execution failed: {str(e)}\n{traceback.format_exc()}"
            db.commit()
        
        # Broadcast error
        await manager.broadcast(
            str(execution_id),
            {
                "type": "execution_error",
                "error": str(e)
            }
        )

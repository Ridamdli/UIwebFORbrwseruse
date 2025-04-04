from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import Dict, List, Optional, Any

from app.services.agent_service import AgentService

# Create websocket router
websocket_router = APIRouter(tags=["websocket"])
agent_service = AgentService()

# Store active connections
active_connections: Dict[str, List[WebSocket]] = {}

@websocket_router.websocket("/ws/agent/{task_id}")
async def agent_websocket(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for real-time agent updates.
    Clients connect to this endpoint using the task_id returned from the run_agent API.
    """
    await websocket.accept()
    
    # Register the connection
    if task_id not in active_connections:
        active_connections[task_id] = []
    active_connections[task_id].append(websocket)
    
    try:
        # Check if the task exists
        if not await agent_service.task_exists(task_id):
            await websocket.send_json({"type": "error", "message": "Task not found"})
            await websocket.close()
            return
        
        # Subscribe to task updates
        agent_service.subscribe_to_task(task_id, websocket)
        
        # Send initial status
        status = await agent_service.get_agent_status(task_id)
        if status:
            await websocket.send_json({"type": "status", "data": status})
        
        # Handle incoming messages (like stop requests)
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data.get("action") == "stop":
                await agent_service.stop_agent_task(task_id)
            
    except WebSocketDisconnect:
        # Unregister the connection
        if task_id in active_connections:
            active_connections[task_id].remove(websocket)
            if not active_connections[task_id]:
                del active_connections[task_id]
        
        # Unsubscribe from task updates
        agent_service.unsubscribe_from_task(task_id, websocket)
    
    except Exception as e:
        # Handle other exceptions
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass

async def broadcast_to_task(task_id: str, message: Dict[str, Any]):
    """
    Broadcast a message to all websocket connections for a specific task.
    This is called by the agent service when there are updates to the task.
    """
    if task_id in active_connections:
        for connection in active_connections[task_id]:
            try:
                await connection.send_json(message)
            except Exception:
                # Connection might be closed
                pass 
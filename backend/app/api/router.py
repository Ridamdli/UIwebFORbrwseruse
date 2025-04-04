from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
import os
import json
import asyncio
from typing import Dict, List, Optional, Any

from app.models.requests import (
    AgentRunRequest, 
    ResearchRequest,
    GetRecordingsRequest
)
from app.models.responses import (
    AgentRunResponse,
    RecordingsResponse,
    HealthCheckResponse
)
from app.services.agent_service import AgentService
from app.services.browser_service import BrowserService

api_router = APIRouter(prefix="/api", tags=["api"])
agent_service = AgentService()
browser_service = BrowserService()

@api_router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint to verify API is running"""
    return {"status": "ok", "version": "1.0.0"}

@api_router.post("/agent/run", response_model=AgentRunResponse)
async def run_agent(
    request: AgentRunRequest,
    background_tasks: BackgroundTasks
):
    """
    Run an agent to perform a browser automation task.
    The agent runs asynchronously, and the client should connect to the WebSocket
    endpoint to receive real-time updates.
    """
    task_id = await agent_service.start_agent_task(request)
    return {"task_id": task_id, "status": "started"}

@api_router.get("/agent/status/{task_id}")
async def get_agent_status(task_id: str):
    """Get the current status of a running agent task"""
    status = await agent_service.get_agent_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status

@api_router.post("/agent/stop/{task_id}")
async def stop_agent(task_id: str):
    """Stop a running agent task"""
    success = await agent_service.stop_agent_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or already completed")
    return {"status": "stopped"}

@api_router.post("/research/run")
async def run_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Run a deep research agent to perform a complex research task.
    The research runs asynchronously, and the client should connect to the WebSocket
    endpoint to receive real-time updates.
    """
    task_id = await agent_service.start_research_task(request)
    return {"task_id": task_id, "status": "started"}

@api_router.get("/recordings")
async def list_recordings():
    """List all available recordings"""
    recordings = browser_service.get_recordings()
    return {"recordings": recordings}

@api_router.get("/recordings/{filename}")
async def get_recording(filename: str):
    """Get a specific recording file"""
    file_path = os.path.join("./tmp/record_videos", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Recording not found")
    return FileResponse(file_path)

@api_router.post("/config/save")
async def save_config(config: Dict[str, Any]):
    """Save a configuration to a file"""
    try:
        config_id = await agent_service.save_config(config)
        return {"config_id": config_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving configuration: {str(e)}")

@api_router.post("/config/load")
async def load_config(config_id: str):
    """Load a configuration from a file"""
    try:
        config = await agent_service.load_config(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading configuration: {str(e)}") 
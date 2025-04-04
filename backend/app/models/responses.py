from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class AgentRunResponse(BaseModel):
    """Response model for agent run endpoint"""
    task_id: str = Field(description="Unique identifier for the task")
    status: str = Field(description="Status of the task")

class AgentStatusResponse(BaseModel):
    """Response model for agent status endpoint"""
    task_id: str = Field(description="Unique identifier for the task")
    status: str = Field(description="Status of the task (running, completed, failed, or stopped)")
    final_result: Optional[str] = Field(default=None, description="Final result of the agent task")
    errors: Optional[str] = Field(default=None, description="Errors encountered during the task")
    model_actions: Optional[str] = Field(default=None, description="Actions taken by the model")
    model_thoughts: Optional[str] = Field(default=None, description="Thoughts of the model")
    recording_path: Optional[str] = Field(default=None, description="Path to the recording")
    trace_path: Optional[str] = Field(default=None, description="Path to the trace file")
    history_path: Optional[str] = Field(default=None, description="Path to the agent history file")
    screenshot: Optional[str] = Field(default=None, description="Base64 encoded screenshot")
    progress: float = Field(default=0.0, description="Progress of the task (0.0 to 1.0)")

class RecordingInfo(BaseModel):
    """Information about a recording"""
    filename: str = Field(description="Name of the recording file")
    url: str = Field(description="URL to access the recording")
    size: int = Field(description="Size of the recording in bytes")
    created_at: str = Field(description="Creation time of the recording")

class RecordingsResponse(BaseModel):
    """Response model for recordings endpoint"""
    recordings: List[RecordingInfo] = Field(default_factory=list, description="List of recordings")

class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field(description="Status of the API")
    version: str = Field(description="Version of the API")

class ConfigSaveResponse(BaseModel):
    """Response model for config save endpoint"""
    config_id: str = Field(description="Unique identifier for the saved configuration") 
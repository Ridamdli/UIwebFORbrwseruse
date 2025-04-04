import asyncio
import json
import os
import time
import uuid
import base64
from typing import Dict, List, Optional, Any, Set
from fastapi import WebSocket

from app.models.requests import AgentRunRequest, ResearchRequest
from app.api.websocket import broadcast_to_task
from app.core.agent_runner import run_browser_agent, run_deep_research

class AgentTask:
    """Class representing a running agent task"""
    def __init__(self, task_id: str, request: Any):
        self.task_id = task_id
        self.request = request
        self.status = "starting"
        self.final_result = None
        self.errors = None
        self.model_actions = None
        self.model_thoughts = None
        self.recording_path = None
        self.trace_path = None
        self.history_path = None
        self.screenshot = None
        self.progress = 0.0
        self.task = None
        self.subscribers: Set[WebSocket] = set()
        self.is_stopped = False

class AgentService:
    """Service for handling agent tasks"""
    def __init__(self):
        # Map of task_id to AgentTask objects
        self.tasks: Dict[str, AgentTask] = {}
        
    async def start_agent_task(self, request: AgentRunRequest) -> str:
        """Start a new agent task and return the task_id"""
        task_id = str(uuid.uuid4())
        
        # Create a new task object
        task_obj = AgentTask(task_id, request)
        self.tasks[task_id] = task_obj
        
        # Start the agent task in the background
        task_obj.task = asyncio.create_task(self._run_agent(task_id, request))
        
        return task_id
    
    async def start_research_task(self, request: ResearchRequest) -> str:
        """Start a new research task and return the task_id"""
        task_id = str(uuid.uuid4())
        
        # Create a new task object
        task_obj = AgentTask(task_id, request)
        self.tasks[task_id] = task_obj
        
        # Start the research task in the background
        task_obj.task = asyncio.create_task(self._run_research(task_id, request))
        
        return task_id
    
    async def _run_agent(self, task_id: str, request: AgentRunRequest) -> None:
        """Run the agent task and update the task status"""
        try:
            task_obj = self.tasks[task_id]
            task_obj.status = "running"
            
            # Update all subscribers
            await self._notify_subscribers(task_id)
            
            # Convert request to the format expected by run_browser_agent
            # This is where we adapt the new API to the existing code
            agent_kwargs = request.dict()
            
            # Run the agent
            result = await run_browser_agent(**agent_kwargs, on_update=lambda update: self._handle_agent_update(task_id, update))
            
            # Update task status
            task_obj = self.tasks[task_id]
            task_obj.status = "completed"
            task_obj.final_result = result.get("final_result", "")
            task_obj.errors = result.get("errors", "")
            task_obj.model_actions = result.get("model_actions", "")
            task_obj.model_thoughts = result.get("model_thoughts", "")
            task_obj.recording_path = result.get("recording_path", "")
            task_obj.trace_path = result.get("trace_path", "")
            task_obj.history_path = result.get("history_path", "")
            task_obj.progress = 1.0
            
            # Update all subscribers
            await self._notify_subscribers(task_id)
            
        except Exception as e:
            # Update task status
            if task_id in self.tasks:
                task_obj = self.tasks[task_id]
                task_obj.status = "failed"
                task_obj.errors = str(e)
                
                # Update all subscribers
                await self._notify_subscribers(task_id)
    
    async def _run_research(self, task_id: str, request: ResearchRequest) -> None:
        """Run the research task and update the task status"""
        try:
            task_obj = self.tasks[task_id]
            task_obj.status = "running"
            
            # Update all subscribers
            await self._notify_subscribers(task_id)
            
            # Convert request to the format expected by run_deep_research
            research_kwargs = {
                "research_task": request.research_task,
                "max_search_iteration": request.max_search_iteration,
                "max_query_per_iter": request.max_query_per_iter,
                "llm_provider": request.llm_provider,
                "llm_model_name": request.llm_model_name,
                "llm_num_ctx": request.llm_num_ctx,
                "llm_temperature": request.llm_temperature,
                "llm_base_url": request.llm_base_url,
                "llm_api_key": request.llm_api_key,
                "use_vision": request.use_vision,
                "use_own_browser": request.use_own_browser,
                "headless": request.headless,
                "chrome_cdp": request.chrome_cdp
            }
            
            # Run the research
            result = await run_deep_research(**research_kwargs, on_update=lambda update: self._handle_research_update(task_id, update))
            
            # Update task status
            task_obj = self.tasks[task_id]
            task_obj.status = "completed"
            task_obj.final_result = result.get("markdown_content", "")
            task_obj.errors = ""
            task_obj.progress = 1.0
            
            # Update all subscribers
            await self._notify_subscribers(task_id)
            
        except Exception as e:
            # Update task status
            if task_id in self.tasks:
                task_obj = self.tasks[task_id]
                task_obj.status = "failed"
                task_obj.errors = str(e)
                
                # Update all subscribers
                await self._notify_subscribers(task_id)
    
    def _handle_agent_update(self, task_id: str, update: Dict[str, Any]) -> None:
        """Handle updates from the agent task"""
        if task_id in self.tasks:
            task_obj = self.tasks[task_id]
            
            # Update the task object with the latest information
            if "screenshot" in update:
                task_obj.screenshot = update["screenshot"]
            if "progress" in update:
                task_obj.progress = update["progress"]
            if "model_actions" in update:
                task_obj.model_actions = update["model_actions"]
            if "model_thoughts" in update:
                task_obj.model_thoughts = update["model_thoughts"]
            
            # Schedule notification to subscribers
            asyncio.create_task(self._notify_subscribers(task_id))
    
    def _handle_research_update(self, task_id: str, update: Dict[str, Any]) -> None:
        """Handle updates from the research task"""
        if task_id in self.tasks:
            task_obj = self.tasks[task_id]
            
            # Update the task object with the latest information
            if "progress" in update:
                task_obj.progress = update["progress"]
            if "current_results" in update:
                task_obj.model_thoughts = update["current_results"]
            
            # Schedule notification to subscribers
            asyncio.create_task(self._notify_subscribers(task_id))
    
    async def _notify_subscribers(self, task_id: str) -> None:
        """Notify all subscribers of a task update"""
        if task_id in self.tasks:
            task_obj = self.tasks[task_id]
            
            # Prepare the message
            message = {
                "type": "update",
                "data": {
                    "task_id": task_id,
                    "status": task_obj.status,
                    "final_result": task_obj.final_result,
                    "errors": task_obj.errors,
                    "model_actions": task_obj.model_actions,
                    "model_thoughts": task_obj.model_thoughts,
                    "recording_path": task_obj.recording_path,
                    "trace_path": task_obj.trace_path,
                    "history_path": task_obj.history_path,
                    "screenshot": task_obj.screenshot,
                    "progress": task_obj.progress
                }
            }
            
            # Broadcast the message
            await broadcast_to_task(task_id, message)
    
    async def get_agent_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a task"""
        if task_id in self.tasks:
            task_obj = self.tasks[task_id]
            
            return {
                "task_id": task_id,
                "status": task_obj.status,
                "final_result": task_obj.final_result,
                "errors": task_obj.errors,
                "model_actions": task_obj.model_actions,
                "model_thoughts": task_obj.model_thoughts,
                "recording_path": task_obj.recording_path,
                "trace_path": task_obj.trace_path,
                "history_path": task_obj.history_path,
                "screenshot": task_obj.screenshot,
                "progress": task_obj.progress
            }
        
        return None
    
    async def stop_agent_task(self, task_id: str) -> bool:
        """Stop a running agent task"""
        if task_id in self.tasks:
            task_obj = self.tasks[task_id]
            
            # Mark the task as stopped
            task_obj.is_stopped = True
            
            # Cancel the task if it's running
            if task_obj.task and not task_obj.task.done():
                task_obj.task.cancel()
            
            # Update task status
            task_obj.status = "stopped"
            
            # Notify subscribers
            await self._notify_subscribers(task_id)
            
            return True
        
        return False
    
    async def task_exists(self, task_id: str) -> bool:
        """Check if a task exists"""
        return task_id in self.tasks
    
    def subscribe_to_task(self, task_id: str, websocket: WebSocket) -> None:
        """Subscribe to task updates"""
        if task_id in self.tasks:
            self.tasks[task_id].subscribers.add(websocket)
    
    def unsubscribe_from_task(self, task_id: str, websocket: WebSocket) -> None:
        """Unsubscribe from task updates"""
        if task_id in self.tasks:
            self.tasks[task_id].subscribers.discard(websocket)
    
    async def save_config(self, config: Dict[str, Any]) -> str:
        """Save a configuration to a file"""
        config_id = str(uuid.uuid4())
        os.makedirs("./tmp/webui_settings", exist_ok=True)
        config_file = os.path.join("./tmp/webui_settings", f"{config_id}.json")
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config_id
    
    async def load_config(self, config_id: str) -> Optional[Dict[str, Any]]:
        """Load a configuration from a file"""
        config_file = os.path.join("./tmp/webui_settings", f"{config_id}.json")
        
        if not os.path.exists(config_file):
            return None
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        return config 
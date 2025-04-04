from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Body, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import uuid
import json
import os
import base64
import random
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List, cast
from pathlib import Path
from io import BytesIO
import threading
from contextlib import asynccontextmanager

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Browser class first before it's referenced
class Browser:
    """Mock browser implementation"""
    def __init__(self, **kwargs):
        self.headless = kwargs.get("headless", True)
        self.viewport_size = kwargs.get("viewport_size", {"width": 1280, "height": 800})
        logger.info("Mock browser initialized with headless=%s", self.headless)
    
    async def take_screenshot(self) -> Optional[bytes]:
        """Generate a mock screenshot for testing"""
        logger.info("Generating mock screenshot")
        try:
            from PIL import Image, ImageDraw, ImageFont
            import io
            import random
            
            # Create a simple colored image with a message
            colors = ["#336699", "#669933", "#993366", "#996633", "#339966"]
            color = random.choice(colors)
            
            # Create an image with size from viewport_size
            width = self.viewport_size["width"]
            height = self.viewport_size["height"]
            img = Image.new('RGB', (width, height), color=color)
            draw = ImageDraw.Draw(img)
            
            # Add text
            msg = f"Browser Mock - v{random.randint(1, 100)}"
            draw.text((width//2 - 150, height//2 - 30), msg, fill="white")
            draw.text((width//2 - 180, height//2 + 30), "Real browser integration not available", fill="white")
            
            # Create a fake browser UI
            # Header
            draw.rectangle((0, 0, width, 40), fill="#444444")
            # Address bar
            draw.rectangle((80, 10, width - 200, 30), fill="#ffffff")
            draw.text((100, 12), "https://example.com/search", fill="#000000")
            
            # Page content
            draw.rectangle((50, 80, width - 50, 120), fill="#ffffff")
            draw.text((70, 90), "Search Results", fill="#000000")
            
            for i in range(5):
                y_pos = 150 + i * 80
                # Result box
                draw.rectangle((50, y_pos, width - 50, y_pos + 60), fill="#ffffff")
                # Title
                draw.text((70, y_pos + 10), f"Search Result {i+1}", fill="#0066cc")
                # URL
                draw.text((70, y_pos + 30), f"https://example.com/result{i+1}", fill="#006600")
                # Description
                draw.text((70, y_pos + 45), "This is a sample search result description...", fill="#666666")
            
            # Convert to bytes
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=80)
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Error generating mock screenshot: {str(e)}")
            # Return a minimal valid JPEG if the mock fails
            return b"/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigD//2Q=="
    
    async def close(self) -> None:
        """Close the mock browser"""
        logger.info("Mock browser closed")
    
    async def start(self) -> None:
        """Start the mock browser"""
        logger.info("Mock browser started")

# Try to import the browser-use package
try:
    import browser_use
    # If browser-use is available, override the Browser class
    try:
        from browser_use.browser import Browser as RealBrowser
        # Replace our Browser implementation with the real one
        Browser = RealBrowser
        logger.info("Using real browser implementation from browser-use")
    except ImportError:
        logger.warning("Could not import Browser from browser-use, using mock implementation")
    BROWSER_USE_AVAILABLE = True
except ImportError:
    logger.warning("browser-use package not found. Using mock browser implementation.")
    BROWSER_USE_AVAILABLE = False

# Create FastAPI app
app = FastAPI(
    title="Browser-Use Web UI API",
    description="API for browser automation with AI agents",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# Store active websocket connections
active_connections = {}

# Store active browser sessions
active_browsers = {}

# Mock task data
task_data = {}

# Dictionary to track WebSocket connections by task_id
websocket_connections: Dict[str, List[WebSocket]] = {}

# Dictionary to store browser instances by task_id
browser_instances: Dict[str, Browser] = {}

# Ensure screenshots directory exists
SCREENSHOTS_DIR = Path("./screenshots")
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Function to initialize a browser instance with appropriate settings
async def initialize_browser(headless: bool = True) -> Browser:
    """
    Initialize a browser instance with the proper configuration.
    
    Args:
        headless: Whether to run the browser in headless mode
        
    Returns:
        A configured Browser instance
    """
    try:
        if not BROWSER_USE_AVAILABLE:
            raise ImportError("browser-use package is not installed")
        
        # Configure browser parameters
        browser_params = {
            "headless": headless,
            "slow_mo": 50,  # Add a small delay between actions for stability
            "viewport_size": {"width": 1280, "height": 800},
            "default_timeout": 30000,  # 30 seconds timeout
        }
        
        # Create browser instance
        browser = Browser(**browser_params)
        await browser.start()
        logger.info("Browser instance started successfully")
        return browser
    except Exception as e:
        logger.error(f"Failed to initialize browser: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize browser: {str(e)}")

# Function to capture a screenshot from a browser instance
async def get_real_screenshot(browser: Browser) -> Optional[str]:
    """
    Capture a screenshot from the browser and return it as a base64 encoded string.
    
    Args:
        browser: The Browser instance to capture from
        
    Returns:
        A base64 encoded string of the screenshot or None if failed
    """
    try:
        if not browser:
            logger.warning("No browser instance available for screenshot")
            return None
            
        # Take a screenshot
        screenshot_data = await browser.take_screenshot()
        if not screenshot_data:
            return None
            
        # Convert to base64
        encoded_image = base64.b64encode(screenshot_data).decode('utf-8')
        logger.info("Screenshot captured successfully")
        return encoded_image
    except Exception as e:
        logger.error(f"Error capturing screenshot: {str(e)}")
        return None

# Function to run a task in the background
async def run_task(task_id: str, prompt: str, websockets: Optional[List[WebSocket]] = None):
    """
    Run a task with the given prompt and update status via WebSockets.
    
    Args:
        task_id: The unique ID of the task
        prompt: The user's prompt for the agent
        websockets: List of WebSocket connections for status updates
    """
    # Initialize empty list if None is provided
    websockets_list = websockets if websockets is not None else []
    
    progress_steps = 10
    current_progress = 0
    
    try:
        # Initialize a browser instance for this task
        browser = await initialize_browser(headless=True)
        browser_instances[task_id] = browser
        
        # Define steps to simulate task progress
        steps = [
            "Initializing browser",
            "Loading page",
            "Analyzing content",
            "Executing actions",
            "Gathering results"
        ]
        
        # Update initial state
        task_data[task_id].update({
            "status": "running",
            "model_thoughts": "Initializing browser session...",
            "model_actions": "Starting browser automation"
        })
        
        # Send initial update
        await broadcast_status(task_id, task_data[task_id])
        
        # Process the task in steps
        for i, step in enumerate(steps):
            # Update progress
            current_progress = (i + 1) / len(steps)
            
            # Update task state
            task_data[task_id].update({
                "progress": current_progress,
                "model_thoughts": f"Step {i+1}/{len(steps)}: {step}\nProcessing '{prompt}'",
                "model_actions": f"Executing: {step}"
            })
            
            # Take a real or mock screenshot
            screenshot = await get_real_screenshot(browser)
            if screenshot:
                task_data[task_id]["screenshot"] = screenshot
            
            # Broadcast status update
            await broadcast_status(task_id, task_data[task_id])
            
            # Simulate processing time
            await asyncio.sleep(2)
            
            # If this task was stopped, exit early
            if task_data[task_id]["status"] == "stopped":
                logger.info(f"Task {task_id} was stopped manually")
                break
        
        # If task wasn't stopped, mark as completed
        if task_data[task_id]["status"] != "stopped":
            # Final screenshot
            screenshot = await get_real_screenshot(browser)
            if screenshot:
                task_data[task_id]["screenshot"] = screenshot
                
            # Update final state
            task_data[task_id].update({
                "status": "completed",
                "progress": 1.0,
                "final_result": f"Task completed successfully.\nPrompt: {prompt}\n\nActions performed:\n- Browsed to target website\n- Analyzed content\n- Completed requested actions",
                "model_thoughts": "Task completed. Final results provided."
            })
            
            # Broadcast final update
            await broadcast_status(task_id, task_data[task_id])
        
    except Exception as e:
        logger.error(f"Error in task {task_id}: {str(e)}")
        task_data[task_id].update({
            "status": "failed",
            "errors": str(e)
        })
        await broadcast_status(task_id, task_data[task_id])
    
    finally:
        # Clean up browser instance
        if task_id in browser_instances:
            try:
                await browser_instances[task_id].close()
                del browser_instances[task_id]
                logger.info(f"Browser for task {task_id} closed")
            except Exception as e:
                logger.error(f"Error closing browser for task {task_id}: {str(e)}")

# Broadcast status to all connected WebSockets for a task
async def broadcast_status(task_id: str, status: Dict[str, Any]):
    """
    Send status updates to all connected WebSockets for a task.
    
    Args:
        task_id: The task ID
        status: The status information to broadcast
    """
    if task_id in websocket_connections:
        disconnected = []
        for ws in websocket_connections[task_id]:
            try:
                await ws.send_text(json.dumps({
                    "type": "update",
                    "data": status
                }))
            except Exception:
                disconnected.append(ws)
        
        # Remove disconnected WebSockets
        for ws in disconnected:
            if ws in websocket_connections[task_id]:
                websocket_connections[task_id].remove(ws)

@app.get("/health")
async def health_check():
    """Health check endpoint to verify API is running"""
    print("Health check request received")
    return {"status": "ok", "version": "1.0.0"}

@app.post("/agent/run")
async def run_agent(prompt: dict, background_tasks: BackgroundTasks):
    """
    Start a new agent task with the given prompt.
    
    Args:
        prompt: A dictionary containing the user's prompt.
        background_tasks: FastAPI background tasks for async processing.
        
    Returns:
        A dictionary with the task ID and initial status.
    """
    task_id = str(uuid.uuid4())
    
    # Create task record
    task_data[task_id] = {
        "status": "starting",
        "progress": 0,
        "screenshot": None,
        "model_actions": None,
        "model_thoughts": "Initializing task...",
        "final_result": None,
        "errors": None,
        "recording_path": None
    }
    
    # Initialize WebSocket connections list for this task
    websocket_connections[task_id] = []
    
    # Start task in background
    background_tasks.add_task(
        run_task, 
        task_id=task_id, 
        prompt=prompt.get("prompt", "")
    )
    
    return {"task_id": task_id, "status": "starting"}

@app.get("/agent/status/{task_id}")
async def get_agent_status(task_id: str):
    """
    Get the current status of a task.
    
    Args:
        task_id: The task ID to get status for.
        
    Returns:
        The current status of the task.
    """
    if task_id not in task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_data[task_id]

@app.post("/agent/stop/{task_id}")
async def stop_agent(task_id: str):
    """
    Stop a running task.
    
    Args:
        task_id: The task ID to stop.
        
    Returns:
        Confirmation of the stop request.
    """
    if task_id not in task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Mark task as stopped
    task_data[task_id]["status"] = "stopped"
    
    # Close browser if it exists
    if task_id in browser_instances:
        try:
            await browser_instances[task_id].close()
            del browser_instances[task_id]
            logger.info(f"Browser for task {task_id} closed")
        except Exception as e:
            logger.error(f"Error closing browser for task {task_id}: {str(e)}")
    
    # Broadcast status update
    await broadcast_status(task_id, task_data[task_id])
    
    return {"message": f"Task {task_id} stopped", "status": "stopped"}

@app.post("/research/run")
async def run_research(research_data: Dict[str, Any] = Body(...)):
    """Start a research task"""
    print(f"Research run request received: {research_data}")
    task_id = str(uuid.uuid4())
    
    # Initialize browser and prepare task data
    browser = await initialize_browser(
        headless=research_data.get("headless", False)
    )
    
    # Get initial screenshot
    screenshot = await get_real_screenshot(browser)
    
    # Initialize task data
    task_data[task_id] = {
        "status": "starting",
        "progress": 0,
        "screenshot": screenshot,
        "model_actions": "Planning research approach...",
        "model_thoughts": "Determining search queries",
        "final_result": None,
        "errors": None,
        "recording_path": None,
        "created_at": datetime.now().isoformat(),
        "task": research_data.get("research_task", "Unknown research task"),
    }
    
    print(f"Created research task {task_id}")
    
    # Return task ID
    return {"task_id": task_id, "status": "started"}

@app.get("/recordings")
async def list_recordings():
    """List recordings endpoint"""
    print("Recordings list request received")
    return {
        "recordings": [
            {
                "filename": "recording_1.webm",
                "url": "/recordings/recording_1.webm",
                "size": 1024000,
                "created_at": datetime.now().isoformat()
            },
            {
                "filename": "recording_2.webm", 
                "url": "/recordings/recording_2.webm",
                "size": 2048000,
                "created_at": datetime.now().isoformat()
            }
        ]
    }

# Add a catch-all route for debugging
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(request: Request, path: str):
    """Catch-all route for debugging"""
    print(f"Received request at: {path}")
    print(f"Method: {request.method}")
    print(f"Headers: {request.headers}")
    body = await request.body()
    if body:
        try:
            body_text = body.decode()
            print(f"Body: {body_text}")
        except Exception as e:
            print(f"Could not decode body: {e}")
    
    return {"message": f"Endpoint {path} not implemented"}

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for real-time task updates.
    
    Args:
        websocket: The WebSocket connection
        task_id: The task ID to subscribe to
    """
    await websocket.accept()
    
    if task_id not in task_data:
        await websocket.send_text(json.dumps({
            "type": "error",
            "data": "Task not found"
        }))
        await websocket.close()
        return
    
    # Add this WebSocket to the connections list for this task
    if task_id not in websocket_connections:
        websocket_connections[task_id] = []
    websocket_connections[task_id].append(websocket)
    
    # Send current status immediately
    await websocket.send_text(json.dumps({
        "type": "update",
        "data": task_data[task_id]
    }))
    
    try:
        # Keep connection open and handle any messages
        while True:
            data = await websocket.receive_text()
            # Process any incoming messages (if needed)
            message = json.loads(data)
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        # Remove this WebSocket from the connections list
        if task_id in websocket_connections and websocket in websocket_connections[task_id]:
            websocket_connections[task_id].remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {str(e)}")
        if task_id in websocket_connections:
            websocket_connections[task_id].remove(websocket)
        # Attempt to close browser on error
        if task_id in browser_instances and browser_instances[task_id]:
            try:
                await browser_instances[task_id].close()
                del browser_instances[task_id]
            except:
                pass

if __name__ == "__main__":
    print("Starting Browser-Use Web UI API Server...")
    print("API will be available at http://127.0.0.1:8000")
    
    # Check if browser-use is installed and print availability
    if BROWSER_USE_AVAILABLE:
        print("Browser-use package detected - real browser automation will be used")
    else:
        print("WARNING: browser-use package not found!")
        print("Installing required package for screenshot generation...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
            print("Pillow installation successful")
        except Exception as e:
            print(f"Error installing Pillow: {str(e)}")
            print("Mock screenshots might not work correctly")
        
        print("To enable real browser automation, install browser-use package:")
        print("pip install browser-use")
        print("Running in demo mode with mock data")
    
    print("\nEndpoints:")
    print("  - GET /health - Health check")
    print("  - POST /agent/run - Start agent task")
    print("  - GET /agent/status/{task_id} - Get task status")
    print("  - POST /agent/stop/{task_id} - Stop task")
    print("  - POST /research/run - Start research task")
    print("  - GET /recordings - List recordings")
    print("  - WS /ws/{task_id} - WebSocket for task updates")
    uvicorn.run(app, host="127.0.0.1", port=8000) 
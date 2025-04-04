from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
import uuid
import base64
import logging
import time
from typing import Dict, Any, List
from io import BytesIO
from PIL import Image, ImageDraw

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Simple Browser API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store tasks and connections
tasks = {}
websocket_connections = {}

def generate_mock_screenshot(step=0):
    """Generate a visually different mock screenshot for each step"""
    try:
        # Define colors for different steps
        colors = ["#336699", "#669933", "#993366", "#996633", "#339966"]
        color = colors[step % len(colors)]
        
        # Create image
        width, height = 1280, 800
        img = Image.new('RGB', (width, height), color=color)
        draw = ImageDraw.Draw(img)
        
        # Add text
        draw.text((width//2 - 150, height//2 - 50), f"Task Step {step+1}", fill="white")
        draw.text((width//2 - 180, height//2), "Mock Browser View", fill="white")
        draw.text((width//2 - 100, height//2 + 50), f"Timestamp: {time.time()}", fill="white")
        
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
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        logger.info(f"Generated mock screenshot for step {step}")
        return encoded
    except Exception as e:
        logger.error(f"Error generating screenshot: {e}")
        return None

async def broadcast_status(task_id: str, status: Dict[str, Any]):
    """Send updates to all connected WebSockets for a task"""
    if task_id in websocket_connections:
        disconnected = []
        for ws in websocket_connections[task_id]:
            try:
                await ws.send_text(json.dumps({
                    "type": "update",
                    "data": status
                }))
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.append(ws)
        
        # Remove disconnected WebSockets
        for ws in disconnected:
            if ws in websocket_connections[task_id]:
                websocket_connections[task_id].remove(ws)

async def process_task(task_id: str, prompt: str):
    """Run a task with the given prompt"""
    try:
        # Define steps
        steps = [
            "Initializing browser",
            "Loading page",
            "Analyzing content",
            "Executing actions",
            "Gathering results"
        ]
        
        # Update initial state
        tasks[task_id].update({
            "status": "running",
            "model_thoughts": "Starting task execution...",
            "model_actions": "Initializing browser"
        })
        
        # Initial update
        await broadcast_status(task_id, tasks[task_id])
        
        # Process steps
        for i, step in enumerate(steps):
            # Check if task was stopped
            if tasks[task_id]["status"] == "stopped":
                logger.info(f"Task {task_id} was stopped")
                return
            
            # Update progress
            progress = (i + 1) / len(steps)
            screenshot = generate_mock_screenshot(i)
            
            # Update task state
            tasks[task_id].update({
                "progress": progress,
                "screenshot": screenshot,
                "model_thoughts": f"Step {i+1}/{len(steps)}: {step}\nProcessing '{prompt}'",
                "model_actions": f"Executing: {step}"
            })
            
            # Send update
            await broadcast_status(task_id, tasks[task_id])
            
            # Wait between steps
            await asyncio.sleep(2)
        
        # Task completed
        final_screenshot = generate_mock_screenshot(len(steps))
        
        tasks[task_id].update({
            "status": "completed",
            "progress": 1.0,
            "screenshot": final_screenshot,
            "final_result": f"Task completed successfully.\nPrompt: {prompt}\n\nActions performed:\n- Browsed to target website\n- Analyzed content\n- Completed requested actions",
            "model_thoughts": "Task completed. Final results provided."
        })
        
        # Final update
        await broadcast_status(task_id, tasks[task_id])
        
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {e}")
        tasks[task_id].update({
            "status": "failed",
            "errors": str(e)
        })
        await broadcast_status(task_id, tasks[task_id])

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Simple Browser API is running"}

@app.post("/agent/run")
async def run_agent(prompt: dict, background_tasks: BackgroundTasks):
    """Start a new browser task"""
    task_id = str(uuid.uuid4())
    
    # Initialize task
    tasks[task_id] = {
        "status": "starting",
        "progress": 0,
        "screenshot": None,
        "model_actions": None,
        "model_thoughts": "Initializing task...",
        "final_result": None,
        "errors": None,
        "recording_path": None
    }
    
    # Initialize connections list
    websocket_connections[task_id] = []
    
    # Start background task
    background_tasks.add_task(process_task, task_id, prompt.get("prompt", ""))
    
    return {"task_id": task_id, "status": "starting"}

@app.get("/agent/status/{task_id}")
async def get_agent_status(task_id: str):
    """Get the status of a task"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks[task_id]

@app.post("/agent/stop/{task_id}")
async def stop_agent(task_id: str):
    """Stop a running task"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update task status
    tasks[task_id]["status"] = "stopped"
    await broadcast_status(task_id, tasks[task_id])
    
    return {"message": f"Task {task_id} stopped", "status": "stopped"}

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for real-time updates"""
    logger.info(f"WebSocket connection request for task {task_id}")
    
    # Accept the connection with optional headers
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for task {task_id}")
    
    if task_id not in tasks:
        logger.warning(f"Task {task_id} not found for WebSocket connection")
        await websocket.send_text(json.dumps({
            "type": "error",
            "data": "Task not found"
        }))
        await websocket.close()
        return
    
    # Add websocket to connections
    if task_id not in websocket_connections:
        websocket_connections[task_id] = []
    websocket_connections[task_id].append(websocket)
    logger.info(f"WebSocket added to connections for task {task_id}")
    
    # Send current status
    await websocket.send_text(json.dumps({
        "type": "update",
        "data": tasks[task_id]
    }))
    logger.info(f"Initial status sent for task {task_id}")
    
    try:
        # Keep connection open
        while True:
            data = await websocket.receive_text()
            # Handle ping
            logger.debug(f"WebSocket message received: {data}")
            message = json.loads(data)
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                logger.debug("Sent pong response")
    except WebSocketDisconnect:
        # Remove connection on disconnect
        logger.info(f"WebSocket disconnected for task {task_id}")
        if task_id in websocket_connections and websocket in websocket_connections[task_id]:
            websocket_connections[task_id].remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {e}")
        if task_id in websocket_connections and websocket in websocket_connections[task_id]:
            websocket_connections[task_id].remove(websocket)

if __name__ == "__main__":
    print("Starting Simple Browser API Server...")
    print("API will be available at http://127.0.0.1:8000")
    
    print("\nEndpoints:")
    print("  - POST /agent/run - Start agent task")
    print("  - GET /agent/status/{task_id} - Get task status")
    print("  - POST /agent/stop/{task_id} - Stop task")
    print("  - WS /ws/{task_id} - WebSocket for task updates")
    
    uvicorn.run(app, host="127.0.0.1", port=8000) 
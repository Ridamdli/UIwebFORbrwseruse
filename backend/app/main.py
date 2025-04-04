from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv

from app.api.router import api_router
from app.api.websocket import websocket_router

# Load environment variables
load_dotenv()

# Get CORS settings from environment variables
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
allowed_origins = [origin.strip() for origin in CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

# Create FastAPI app
app = FastAPI(
    title="Browser-Use Web UI API",
    description="API for browser automation with AI agents",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# Include API routers
app.include_router(api_router)
app.include_router(websocket_router)

# Mount static files
@app.on_event("startup")
async def startup_event():
    # Create necessary directories
    os.makedirs("./tmp/record_videos", exist_ok=True)
    os.makedirs("./tmp/traces", exist_ok=True)
    os.makedirs("./tmp/agent_history", exist_ok=True)
    os.makedirs("./tmp/webui_settings", exist_ok=True)

# Mount static files for recordings
app.mount("/recordings", StaticFiles(directory="./tmp/record_videos"), name="recordings")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 
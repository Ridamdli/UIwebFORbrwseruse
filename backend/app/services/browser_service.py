import os
import glob
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.models.responses import RecordingInfo

class BrowserService:
    """Service for handling browser functionality"""
    def __init__(self):
        # Create the necessary directories
        os.makedirs("./tmp/record_videos", exist_ok=True)
        os.makedirs("./tmp/traces", exist_ok=True)
        os.makedirs("./tmp/agent_history", exist_ok=True)
    
    def get_recordings(self) -> List[RecordingInfo]:
        """Get a list of all recordings"""
        recordings = []
        
        # Check if the recordings directory exists
        if not os.path.exists("./tmp/record_videos"):
            return recordings
        
        # Find all video files
        video_files = (
            glob.glob("./tmp/record_videos/*.[mM][pP]4") +
            glob.glob("./tmp/record_videos/*.[wW][eE][bB][mM]")
        )
        
        # Create RecordingInfo objects for each file
        for file_path in video_files:
            filename = os.path.basename(file_path)
            size = os.path.getsize(file_path)
            created_at = datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
            url = f"/recordings/{filename}"
            
            recording_info = RecordingInfo(
                filename=filename,
                url=url,
                size=size,
                created_at=created_at
            )
            
            recordings.append(recording_info)
        
        # Sort by creation time (newest first)
        recordings.sort(key=lambda r: r.created_at, reverse=True)
        
        return recordings 
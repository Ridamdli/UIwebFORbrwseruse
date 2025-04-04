#!/usr/bin/env python
"""
Run script for the backend application
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment variables or use defaults
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    # Run the application
    uvicorn.run(
        "app.main:app", 
        host=host, 
        port=port, 
        reload=os.getenv("ENVIRONMENT", "development") == "development"
    ) 
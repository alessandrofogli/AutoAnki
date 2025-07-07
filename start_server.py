#!/usr/bin/env python3
"""
Startup script for AutoAnki FastAPI server.
Checks prerequisites and starts the server with proper error handling.
"""

import subprocess
import sys
import os
import time
import requests
from config import MODEL_NAME, get_logger

# Set up logging for this module
logger = get_logger(__name__)


def check_ollama():
    """Check if Ollama is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def check_model(model_name=MODEL_NAME):
    """Check if the specified model is available."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return any(model["name"] == model_name for model in models)
        return False
    except requests.exceptions.RequestException:
        return False


def main():
    """Main startup function."""
    logger.info("🚀 AutoAnki Server Startup")
    logger.info("=" * 40)
    
    # Check if Ollama is running
    logger.info("🔍 Checking Ollama...")
    if not check_ollama():
        logger.error("❌ Ollama is not running!")
        logger.error("Please start Ollama with: ollama serve")
        logger.error("Then run this script again.")
        sys.exit(1)
    logger.info("✅ Ollama is running")
    
    # Check if the configured model is available
    logger.info(f"🔍 Checking for {MODEL_NAME} model...")
    if not check_model():
        logger.warning(f"⚠️  {MODEL_NAME} model not found!")
        logger.info(f"Pulling {MODEL_NAME} model...")
        try:
            subprocess.run(["ollama", "pull", MODEL_NAME], check=True)
            logger.info(f"✅ {MODEL_NAME} model downloaded successfully")
        except subprocess.CalledProcessError:
            logger.error(f"❌ Failed to download {MODEL_NAME} model")
            logger.error(f"You can try manually: ollama pull {MODEL_NAME}")
            sys.exit(1)
    else:
        logger.info(f"✅ {MODEL_NAME} model is available")
    
    logger.info("")
    logger.info("🎯 Starting FastAPI server...")
    logger.info("📖 API documentation will be available at: http://localhost:8000/docs")
    logger.info("🔍 Health check: http://localhost:8000/health")
    logger.info("⏹️  Press Ctrl+C to stop the server")
    logger.info("")
    
    # Start the FastAPI server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        logger.info("\n👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
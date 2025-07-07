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
from config import MODEL_NAME


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
    print("🚀 AutoAnki Server Startup")
    print("=" * 40)
    
    # Check if Ollama is running
    print("🔍 Checking Ollama...")
    if not check_ollama():
        print("❌ Ollama is not running!")
        print("Please start Ollama with: ollama serve")
        print("Then run this script again.")
        sys.exit(1)
    print("✅ Ollama is running")
    
    # Check if the configured model is available
    print(f"🔍 Checking for {MODEL_NAME} model...")
    if not check_model():
        print(f"⚠️  {MODEL_NAME} model not found!")
        print(f"Pulling {MODEL_NAME} model...")
        try:
            subprocess.run(["ollama", "pull", MODEL_NAME], check=True)
            print(f"✅ {MODEL_NAME} model downloaded successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to download {MODEL_NAME} model")
            print(f"You can try manually: ollama pull {MODEL_NAME}")
            sys.exit(1)
    else:
        print(f"✅ {MODEL_NAME} model is available")
    
    print()
    print("🎯 Starting FastAPI server...")
    print("📖 API documentation will be available at: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
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
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
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


def check_ollama():
    """Check if Ollama is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def check_model(model_name="deepseek-r1:8b"):
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
    
    # Check if deepseek-r1:8b model is available
    print("🔍 Checking for deepseek-r1:8b model...")
    if not check_model("deepseek-r1:8b"):
        print("⚠️  deepseek-r1:8b model not found!")
        print("Pulling deepseek-r1:8b model...")
        try:
            subprocess.run(["ollama", "pull", "deepseek-r1:8b"], check=True)
            print("✅ deepseek-r1:8b model downloaded successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to download deepseek-r1:8b model")
            print("You can try manually: ollama pull deepseek-r1:8b")
            sys.exit(1)
    else:
        print("✅ deepseek-r1:8b model is available")
    
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
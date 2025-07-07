from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import sys
import os
from config import MODEL_NAME

# Add the parent directory to the path so we can import from agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.langgraph_orchestrator import create_orchestrator

app = FastAPI(title="AutoAnki API", description="LLM-powered flashcard generation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the orchestrator
orchestrator = None

class FlashcardRequest(BaseModel):
    instruction: str
    model_name: str = MODEL_NAME

class FlashcardResponse(BaseModel):
    instruction: str
    mini_lesson: str
    flashcards: List[Dict[str, str]]
    status: str
    workflow_info: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    """Initialize the orchestrator on startup."""
    global orchestrator
    try:
        orchestrator = create_orchestrator(MODEL_NAME)
        print("✅ AutoAnki orchestrator initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        print("Make sure Ollama is running and the model is available")

@app.get("/")
def read_root():
    return {"message": "AutoAnki backend is running.", "status": "ready"}

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "orchestrator_ready": orchestrator is not None
    }

@app.post("/generate-flashcards", response_model=FlashcardResponse)
async def generate_flashcards(request: FlashcardRequest):
    """
    Generate flashcards from a natural language instruction.
    
    Example request:
    {
        "instruction": "Generate flashcards about the French Revolution",
        "model_name": "deepseek-r1:8b"
    }
    """
    if orchestrator is None:
        raise HTTPException(
            status_code=503, 
            detail="Orchestrator not initialized. Make sure Ollama is running."
        )
    
    try:
        # Generate flashcards using the orchestrator
        result = orchestrator.generate_flashcards(request.instruction)
        
        # Extract the relevant data for the response
        response_data = {
            "instruction": result["instruction"],
            "mini_lesson": result["mini_lesson"],
            "flashcards": result["flashcards"],
            "status": result["status"],
            "workflow_info": {
                "agent": result["agent"],
                "timestamp": result["timestamp"]
            }
        }
        
        return FlashcardResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate flashcards: {str(e)}"
        )

@app.get("/models")
def list_available_models():
    """List available Ollama models (placeholder for future implementation)."""
    return {
        "available_models": [MODEL_NAME, "mistral", "llama2"],
        "current_model": MODEL_NAME,
        "note": "This endpoint will be enhanced to actually check available models"
    }

# TODO: Add MCP endpoints, Anki integration, agent endpoints

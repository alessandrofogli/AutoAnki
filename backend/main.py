from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import sys
import os
from config import MODEL_NAME, get_logger, MODEL_PROVIDER, get_model_config

# Set up logging for this module
logger = get_logger(__name__)

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
        config = get_model_config()
        logger.info(f"🚀 Initializing orchestrator with {config['provider'].upper()} provider")
        logger.info(f"📝 Model: {config['model_name']}")
        
        orchestrator = create_orchestrator()
        logger.info("✅ AutoAnki orchestrator initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize orchestrator: {e}")
        if MODEL_PROVIDER == "ollama":
            logger.error("Make sure Ollama is running and the model is available")
        elif MODEL_PROVIDER == "huggingface":
            logger.error("Make sure your Hugging Face API key is valid and the model is accessible")

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
    """Get current model configuration."""
    config = get_model_config()
    return {
        "current_provider": config["provider"],
        "current_model": config["model_name"],
        "provider_info": {
            "ollama": {
                "description": "Local Ollama instance",
                "base_url": config.get("base_url") if config["provider"] == "ollama" else None
            },
            "huggingface": {
                "description": "Hugging Face Inference API",
                "has_api_key": bool(config.get("api_key")) if config["provider"] == "huggingface" else None
            }
        },
        "note": f"Currently using {config['provider'].upper()} provider"
    }

# TODO: Add MCP endpoints, Anki integration, agent endpoints

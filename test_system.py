#!/usr/bin/env python3
"""
Test script for AutoAnki system.
This script tests the agent workflow directly without the FastAPI server.
"""

import sys
import os
import json
from config import MODEL_NAME, get_logger

# Set up logging for this module
logger = get_logger(__name__)

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.langgraph_orchestrator import create_orchestrator


def test_flashcard_generation():
    """Test the flashcard generation workflow."""
    
    logger.info("🚀 Testing AutoAnki Flashcard Generation System")
    logger.info("=" * 50)
    
    # Test instruction
    instruction = "Generate flashcards about the French Revolution"
    logger.info(f"📝 Instruction: {instruction}")
    logger.info("")
    
    try:
        # Create orchestrator
        logger.info("🔧 Initializing orchestrator...")
        orchestrator = create_orchestrator(MODEL_NAME)
        logger.info("✅ Orchestrator initialized successfully")
        logger.info("")
        
        # Generate flashcards
        logger.info("🔄 Running flashcard generation workflow...")
        result = orchestrator.generate_flashcards(instruction)
        logger.info("✅ Workflow completed successfully")
        logger.info("")
        
        # Display results
        logger.info("📊 Results:")
        logger.info("-" * 30)
        logger.info(f"Status: {result['status']}")
        logger.info(f"Agent: {result['agent']}")
        logger.info("")
        
        logger.info("📚 Mini Lesson:")
        logger.info("-" * 30)
        logger.info(result['mini_lesson'])
        logger.info("")
        
        logger.info("🃏 Generated Flashcards:")
        logger.info("-" * 30)
        for i, card in enumerate(result['flashcards'], 1):
            logger.info(f"Card {i}:")
            logger.info(f"  Question: {card['question']}")
            logger.info(f"  Answer: {card['answer']}")
            logger.info(f"  Category: {card['category']}")
            logger.info("")
        
        # Save results to file for inspection
        with open("test_results.json", "w") as f:
            json.dump(result, f, indent=2)
        logger.info("💾 Results saved to test_results.json")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.error("\n🔧 Troubleshooting:")
        logger.error("1. Make sure Ollama is running: ollama serve")
        logger.error(F"2. Make sure the model is available: ollama pull {MODEL_NAME}")
        logger.error("3. Check that all dependencies are installed: poetry install")
        return False


if __name__ == "__main__":
    success = test_flashcard_generation()
    sys.exit(0 if success else 1) 
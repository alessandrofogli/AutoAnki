#!/usr/bin/env python3
"""
Example script demonstrating how to use the AutoAnki API.
This script shows how to interact with the FastAPI endpoints programmatically.
"""

import requests
import json
import time
from config import get_logger

# Set up logging for this module
logger = get_logger(__name__)


def test_health_check():
    """Test the health check endpoint."""
    logger.info("🔍 Testing health check...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Health check passed: {data}")
            return True
        else:
            logger.error(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Health check error: {e}")
        return False


def test_flashcard_generation(instruction):
    """Test the flashcard generation endpoint."""
    logger.info(f"🃏 Testing flashcard generation for: '{instruction}'")
    
    payload = {
        "instruction": instruction,
        "model_name": "deepseek-r1:8b"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/generate-flashcards",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ Flashcard generation successful!")
            logger.info("")
            
            # Display results
            logger.info("📚 Mini Lesson:")
            logger.info("-" * 40)
            logger.info(data["mini_lesson"])
            logger.info("")
            
            logger.info("🃏 Generated Flashcards:")
            logger.info("-" * 40)
            for i, card in enumerate(data["flashcards"], 1):
                logger.info(f"Card {i}:")
                logger.info(f"  Question: {card['question']}")
                logger.info(f"  Answer: {card['answer']}")
                logger.info(f"  Category: {card['category']}")
                logger.info("")
            
            # Save to file
            with open(f"api_results_{int(time.time())}.json", "w") as f:
                json.dump(data, f, indent=2)
            logger.info("💾 Results saved to file")
            
            return True
        else:
            logger.error(f"❌ Flashcard generation failed: {response.status_code}")
            logger.error(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Flashcard generation error: {e}")
        return False


def test_models_endpoint():
    """Test the models endpoint."""
    logger.info("📋 Testing models endpoint...")
    try:
        response = requests.get("http://localhost:8000/models")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Models endpoint: {data}")
            return True
        else:
            logger.error(f"❌ Models endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Models endpoint error: {e}")
        return False


def main():
    """Main function to run all API tests."""
    logger.info("🚀 AutoAnki API Usage Examples")
    logger.info("=" * 50)
    logger.info("")
    
    # Test health check
    if not test_health_check():
        logger.error("❌ Server is not running or not healthy")
        logger.error("Please start the server with: python start_server.py")
        return
    
    logger.info("")
    
    # Test models endpoint
    test_models_endpoint()
    logger.info("")
    
    # Test flashcard generation with different topics
    test_topics = [
        "Generate flashcards about the French Revolution",
        "Create flashcards about photosynthesis",
        "Make flashcards about Python programming basics"
    ]
    
    for topic in test_topics:
        logger.info("=" * 60)
        success = test_flashcard_generation(topic)
        if not success:
            logger.error("❌ Stopping tests due to failure")
            break
        logger.info("")
        time.sleep(2)  # Brief pause between requests
    
    logger.info("🎉 API testing completed!")


if __name__ == "__main__":
    main() 
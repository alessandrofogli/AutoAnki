#!/usr/bin/env python3
"""
Example script demonstrating how to use the AutoAnki API.
This script shows how to interact with the FastAPI endpoints programmatically.
"""

import requests
import json
import time


def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False


def test_flashcard_generation(instruction):
    """Test the flashcard generation endpoint."""
    print(f"🃏 Testing flashcard generation for: '{instruction}'")
    
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
            print("✅ Flashcard generation successful!")
            print()
            
            # Display results
            print("📚 Mini Lesson:")
            print("-" * 40)
            print(data["mini_lesson"])
            print()
            
            print("🃏 Generated Flashcards:")
            print("-" * 40)
            for i, card in enumerate(data["flashcards"], 1):
                print(f"Card {i}:")
                print(f"  Question: {card['question']}")
                print(f"  Answer: {card['answer']}")
                print(f"  Category: {card['category']}")
                print()
            
            # Save to file
            with open(f"api_results_{int(time.time())}.json", "w") as f:
                json.dump(data, f, indent=2)
            print("💾 Results saved to file")
            
            return True
        else:
            print(f"❌ Flashcard generation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Flashcard generation error: {e}")
        return False


def test_models_endpoint():
    """Test the models endpoint."""
    print("📋 Testing models endpoint...")
    try:
        response = requests.get("http://localhost:8000/models")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Models endpoint: {data}")
            return True
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Models endpoint error: {e}")
        return False


def main():
    """Main function to run all API tests."""
    print("🚀 AutoAnki API Usage Examples")
    print("=" * 50)
    print()
    
    # Test health check
    if not test_health_check():
        print("❌ Server is not running or not healthy")
        print("Please start the server with: python start_server.py")
        return
    
    print()
    
    # Test models endpoint
    test_models_endpoint()
    print()
    
    # Test flashcard generation with different topics
    test_topics = [
        "Generate flashcards about the French Revolution",
        "Create flashcards about photosynthesis",
        "Make flashcards about Python programming basics"
    ]
    
    for topic in test_topics:
        print("=" * 60)
        success = test_flashcard_generation(topic)
        if not success:
            print("❌ Stopping tests due to failure")
            break
        print()
        time.sleep(2)  # Brief pause between requests
    
    print("🎉 API testing completed!")


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Test script for AutoAnki system.
This script tests the agent workflow directly without the FastAPI server.
"""

import sys
import os
import json

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.langgraph_orchestrator import create_orchestrator


def test_flashcard_generation():
    """Test the flashcard generation workflow."""
    
    print("🚀 Testing AutoAnki Flashcard Generation System")
    print("=" * 50)
    
    # Test instruction
    instruction = "Generate flashcards about the French Revolution"
    print(f"📝 Instruction: {instruction}")
    print()
    
    try:
        # Create orchestrator
        print("🔧 Initializing orchestrator...")
        orchestrator = create_orchestrator("deepseek-r1:8b")
        print("✅ Orchestrator initialized successfully")
        print()
        
        # Generate flashcards
        print("🔄 Running flashcard generation workflow...")
        result = orchestrator.generate_flashcards(instruction)
        print("✅ Workflow completed successfully")
        print()
        
        # Display results
        print("📊 Results:")
        print("-" * 30)
        print(f"Status: {result['status']}")
        print(f"Agent: {result['agent']}")
        print()
        
        print("📚 Mini Lesson:")
        print("-" * 30)
        print(result['mini_lesson'])
        print()
        
        print("🃏 Generated Flashcards:")
        print("-" * 30)
        for i, card in enumerate(result['flashcards'], 1):
            print(f"Card {i}:")
            print(f"  Question: {card['question']}")
            print(f"  Answer: {card['answer']}")
            print(f"  Category: {card['category']}")
            print()
        
        # Save results to file for inspection
        with open("test_results.json", "w") as f:
            json.dump(result, f, indent=2)
        print("💾 Results saved to test_results.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Make sure the model is available: ollama pull deepseek-r1:8b")
        print("3. Check that all dependencies are installed: poetry install")
        return False


if __name__ == "__main__":
    success = test_flashcard_generation()
    sys.exit(0 if success else 1) 
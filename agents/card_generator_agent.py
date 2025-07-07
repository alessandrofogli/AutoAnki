from typing import Dict, Any, List
from langchain_core.runnables import RunnableLambda
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
import json
from config import get_logger

logger = get_logger(__name__)


class CardGeneratorAgent:
    """Agent that generates flashcards from a mini lesson."""
    
    def __init__(self, llm: Ollama):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["mini_lesson"],
            template="""
You are an expert flashcard creator. Based on the following mini lesson, create 3-5 high-quality flashcards.

Each flashcard should:
- Have a clear, specific question
- Have a concise, accurate answer
- Cover different aspects of the topic
- Be suitable for spaced repetition learning

Format your response as a valid JSON array with this exact structure:
[
    {{
        "question": "What is the question?",
        "answer": "What is the answer?",
        "category": "concept/definition/fact/example"
    }}
]

Mini Lesson:
{mini_lesson}

Flashcards (JSON format only):
"""
        )
        
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate flashcards from the mini lesson.
        
        Args:
            state: Dictionary containing the mini lesson from topic research
            
        Returns:
            Dictionary containing the flashcards and metadata
        """
        mini_lesson = state["mini_lesson"]
        logger.info("🃏 Card Generator Agent: Starting flashcard generation")
        
        # Generate flashcards using the LLM
        prompt = self.prompt.format(mini_lesson=mini_lesson)
        logger.debug("🔧 Card Generator Agent: Generated prompt, invoking LLM...")
        response = self.llm.invoke(prompt)
        
        # Parse the JSON response
        try:
            # Extract JSON from the response (in case LLM adds extra text)
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            json_str = response[json_start:json_end]
            
            flashcards = json.loads(json_str)
            logger.debug(f"📋 Card Generator Agent: Successfully parsed {len(flashcards)} raw flashcards from LLM")
            
            # Validate flashcard structure
            validated_flashcards = []
            for card in flashcards:
                if isinstance(card, dict) and 'question' in card and 'answer' in card:
                    validated_flashcards.append({
                        "question": card["question"],
                        "answer": card["answer"],
                        "category": card.get("category", "general")
                    })
            
            logger.info(f"✅ Card Generator Agent: Successfully validated {len(validated_flashcards)} flashcards")
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"⚠️ Card Generator Agent: JSON parsing failed, using fallback: {e}")
            # Fallback: create simple flashcards if JSON parsing fails
            validated_flashcards = [
                {
                    "question": "What was the main topic covered?",
                    "answer": mini_lesson[:100] + "..." if len(mini_lesson) > 100 else mini_lesson,
                    "category": "general"
                }
            ]
        
        result = {
            **state,
            "flashcards": validated_flashcards,
            "status": "card_generation_complete",
            "agent": "card_generator"
        }
        
        logger.info("🏁 Card Generator Agent: Flashcard generation workflow completed")
        return result


def create_card_generator_agent(llm: Ollama) -> RunnableLambda:
    """Factory function to create a runnable card generator agent."""
    agent = CardGeneratorAgent(llm)
    return RunnableLambda(agent.run) 
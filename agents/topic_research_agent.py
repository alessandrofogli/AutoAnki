from typing import Dict, Any
from langchain_core.runnables import RunnableLambda
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate


class TopicResearchAgent:
    """Agent that researches and creates a mini lesson on a given topic."""
    
    def __init__(self, llm: Ollama):
        self.llm = llm
        self.prompt = PromptTemplate(
            input_variables=["instruction"],
            template="""
You are an expert educator. Create a comprehensive but concise mini lesson on the following topic: {instruction}

Your response should include:
1. A brief introduction to the topic
2. Key concepts and definitions
3. Important facts and details
4. Historical context if relevant
5. Examples or case studies if applicable

Keep the lesson focused and educational, suitable for creating flashcards. Aim for 3-5 paragraphs total.

Topic: {instruction}

Mini Lesson:
"""
        )
        
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a mini lesson on the given topic.
        
        Args:
            state: Dictionary containing the instruction from supervisor
            
        Returns:
            Dictionary containing the mini lesson and metadata
        """
        instruction = state["instruction"]
        
        # Generate the mini lesson using the LLM
        prompt = self.prompt.format(instruction=instruction)
        mini_lesson = self.llm.invoke(prompt)
        
        return {
            **state,
            "mini_lesson": mini_lesson,
            "status": "topic_research_complete",
            "agent": "topic_research"
        }


def create_topic_research_agent(llm: Ollama) -> RunnableLambda:
    """Factory function to create a runnable topic research agent."""
    agent = TopicResearchAgent(llm)
    return RunnableLambda(agent.run) 
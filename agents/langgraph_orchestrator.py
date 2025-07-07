# agents/langgraph_orchestrator.py

"""
This module will contain LangGraph orchestration logic for AutoAnki agents.
"""

from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from langchain_ollama import OllamaLLM
from .supervisor_agent import create_supervisor_agent
from .topic_research_agent import create_topic_research_agent
from .card_generator_agent import create_card_generator_agent
from config import MODEL_NAME


class AgentState(TypedDict):
    """State that flows through the agent workflow."""
    instruction: str
    mini_lesson: str | None
    flashcards: list | None
    status: str
    agent: str
    timestamp: str


class LangGraphOrchestrator:
    """Orchestrates the flashcard generation workflow using LangGraph."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize the orchestrator with a specific model.
        
        Args:
            model_name: Name of the Ollama model to use
        """
        if model_name is None:
            model_name = MODEL_NAME
        self.llm = OllamaLLM(model=model_name)
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("supervisor", create_supervisor_agent(self.llm))
        workflow.add_node("topic_research", create_topic_research_agent(self.llm))
        workflow.add_node("card_generator", create_card_generator_agent(self.llm))
        
        # Define the flow: supervisor → topic_research → card_generator → end
        workflow.set_entry_point("supervisor")
        workflow.add_edge("supervisor", "topic_research")
        workflow.add_edge("topic_research", "card_generator")
        workflow.add_edge("card_generator", END)
        
        return workflow.compile()
    
    def generate_flashcards(self, instruction: str) -> Dict[str, Any]:
        """
        Generate flashcards from a natural language instruction.
        
        Args:
            instruction: Natural language instruction (e.g., "Generate flashcards about the French Revolution")
            
        Returns:
            Dictionary containing the complete workflow result with flashcards
        """
        # Initialize the state
        initial_state = {
            "instruction": instruction,
            "mini_lesson": None,
            "flashcards": None,
            "status": "started",
            "agent": "initial",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Run the workflow
        result = self.graph.invoke(initial_state)
        
        return result


def create_orchestrator(model_name: str = None) -> LangGraphOrchestrator:
    """Factory function to create a LangGraph orchestrator."""
    return LangGraphOrchestrator(model_name)

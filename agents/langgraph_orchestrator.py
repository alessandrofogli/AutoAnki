# agents/langgraph_orchestrator.py

"""
This module will contain LangGraph orchestration logic for AutoAnki agents.
"""

from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from .supervisor_agent import create_supervisor_agent
from .topic_research_agent import create_topic_research_agent
from .card_generator_agent import create_card_generator_agent
from config import MODEL_NAME, get_logger, create_llm_instance, MODEL_PROVIDER

logger = get_logger(__name__)


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
    
    def __init__(self, model_name: str = None, llm_instance = None):
        """
        Initialize the orchestrator with a specific model.
        
        Args:
            model_name: Name of the model to use (for backward compatibility)
            llm_instance: Pre-configured LLM instance (takes precedence)
        """
        if llm_instance is not None:
            self.llm = llm_instance
            logger.info(f"🔧 Orchestrator: Using provided LLM instance ({type(llm_instance).__name__})")
        else:
            # Use the configured provider
            self.llm = create_llm_instance()
            logger.info(f"🔧 Orchestrator: Created LLM instance using {MODEL_PROVIDER.upper()} provider")
        
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
        logger.info(f"🚀 Orchestrator: Starting flashcard generation workflow for: '{instruction}'")
        
        # Initialize the state
        initial_state = {
            "instruction": instruction,
            "mini_lesson": None,
            "flashcards": None,
            "status": "started",
            "agent": "initial",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        logger.info("🔄 Orchestrator: Executing LangGraph workflow...")
        
        # Run the workflow
        result = self.graph.invoke(initial_state)
        
        logger.info(f"🎉 Orchestrator: Workflow completed successfully! Generated {len(result.get('flashcards', []))} flashcards")
        
        return result


def create_orchestrator(model_name: str = None, llm_instance = None) -> LangGraphOrchestrator:
    """
    Factory function to create a LangGraph orchestrator.
    
    Args:
        model_name: Name of the model (for backward compatibility)
        llm_instance: Pre-configured LLM instance (takes precedence)
        
    Returns:
        Configured LangGraph orchestrator
    """
    return LangGraphOrchestrator(model_name=model_name, llm_instance=llm_instance)

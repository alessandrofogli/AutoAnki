from typing import Dict, Any
from langchain_core.runnables import RunnableLambda
from langchain_core.language_models.llms import LLM
from config import get_logger

logger = get_logger(__name__)


class SupervisorAgent:
    """Supervisor agent that coordinates the flashcard generation workflow."""
    
    def __init__(self, llm: LLM):
        self.llm = llm
        
    def run(self, instruction: str) -> Dict[str, Any]:
        """
        Main entry point for the supervisor agent.
        
        Args:
            instruction: Natural language instruction from user
            
        Returns:
            Dictionary containing the instruction and metadata
        """
        logger.info(f"🎯 Supervisor Agent: Processing instruction - '{instruction}'")
        
        result = {
            "instruction": instruction,
            "status": "supervisor_complete",
            "timestamp": "2024-01-01T00:00:00Z",  # In production, use actual timestamp
            "agent": "supervisor"
        }
        
        logger.info("✅ Supervisor Agent: Completed processing, handing off to topic research")
        return result


def create_supervisor_agent(llm: LLM) -> RunnableLambda:
    """Factory function to create a runnable supervisor agent."""
    agent = SupervisorAgent(llm)
    return RunnableLambda(agent.run) 
from typing import Dict, Any
from langchain_core.runnables import RunnableLambda
from langchain_ollama import OllamaLLM


class SupervisorAgent:
    """Supervisor agent that coordinates the flashcard generation workflow."""
    
    def __init__(self, llm: OllamaLLM):
        self.llm = llm
        
    def run(self, instruction: str) -> Dict[str, Any]:
        """
        Main entry point for the supervisor agent.
        
        Args:
            instruction: Natural language instruction from user
            
        Returns:
            Dictionary containing the instruction and metadata
        """
        return {
            "instruction": instruction,
            "status": "supervisor_complete",
            "timestamp": "2024-01-01T00:00:00Z",  # In production, use actual timestamp
            "agent": "supervisor"
        }


def create_supervisor_agent(llm: OllamaLLM) -> RunnableLambda:
    """Factory function to create a runnable supervisor agent."""
    agent = SupervisorAgent(llm)
    return RunnableLambda(agent.run) 
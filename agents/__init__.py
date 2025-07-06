# agents/__init__.py

# This package will contain LLM agent logic, LangGraph orchestration, and agent utilities.

"""
AutoAnki Agents Module

This module contains the agent implementations for the AutoAnki system:
- SupervisorAgent: Coordinates the workflow
- TopicResearchAgent: Generates mini lessons
- CardGeneratorAgent: Creates flashcards
- LangGraphOrchestrator: Orchestrates the entire workflow
"""

from .supervisor_agent import SupervisorAgent, create_supervisor_agent
from .topic_research_agent import TopicResearchAgent, create_topic_research_agent
from .card_generator_agent import CardGeneratorAgent, create_card_generator_agent
from .langgraph_orchestrator import LangGraphOrchestrator, create_orchestrator

__all__ = [
    "SupervisorAgent",
    "create_supervisor_agent",
    "TopicResearchAgent", 
    "create_topic_research_agent",
    "CardGeneratorAgent",
    "create_card_generator_agent",
    "LangGraphOrchestrator",
    "create_orchestrator"
]

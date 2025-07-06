#!/usr/bin/env python3
"""
Script to plot and save the LangGraph workflow structure for AutoAnki.
"""

from agents.langgraph_orchestrator import (
    create_supervisor_agent,
    create_topic_research_agent,
    create_card_generator_agent,
    AgentState,
)
from langgraph.graph import StateGraph, END
from langchain_community.llms import Ollama

def main():
    llm = Ollama(model="llama3")
    workflow = StateGraph(AgentState)
    workflow.add_node("supervisor", create_supervisor_agent(llm))
    workflow.add_node("topic_research", create_topic_research_agent(llm))
    workflow.add_node("card_generator", create_card_generator_agent(llm))
    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", "topic_research")
    workflow.add_edge("topic_research", "card_generator")
    workflow.add_edge("card_generator", END)

    # DO NOT CALL .compile() HERE!
    dot = workflow.plot()
    print(dot.source)
    dot.render("langgraph_workflow", format="png", cleanup=True)
    print("Graph saved as langgraph_workflow.png")

if __name__ == "__main__":
    main()
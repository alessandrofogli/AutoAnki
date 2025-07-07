# plot_graph_structure.py
# This script is used to plot the graph structure of the workflow.
# It is used to visualize the workflow and the flow of data through the workflow.
# It is also used to debug the workflow.

from agents.langgraph_orchestrator import LangGraphOrchestrator
from langchain_core.runnables.graph import MermaidDrawMethod
from IPython.display import display, Image

# Instantiate your orchestrator (optionally pass a model name)
orchestrator = LangGraphOrchestrator()

# Get the compiled graph object
app = orchestrator.graph

# Display the graph as a PNG
display(
    Image(
        app.get_graph().draw_mermaid_png(
            draw_method=MermaidDrawMethod.API,
        )
    )
)

# Save the PNG to a file
png_bytes = app.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
with open("graph_structure.png", "wb") as f:
    f.write(png_bytes)
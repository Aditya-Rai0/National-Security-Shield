"""
Workflow Definition for the National Security Guardian AI.

This module defines the Directed Acyclic Graph (DAG) that orchestrates the
video security audit process. It connects the nodes (functional units)
using the StateGraph primitive from LangGraph.

Architecture:
    [START] -> [index_video_node] -> [audit_content_node] -> [END]
"""

from langgraph.graph import StateGraph, END

# Import the UPDATED State Schema (Security focused)
from backend.src.graph.state import VideoSecurityState

# Import the Functional Nodes (The workers we just built)
from backend.src.graph.nodes import (
    index_video_node,
    audit_content_node
)

def create_graph():
    """
    Constructs and compiles the LangGraph workflow.

    Returns:
        CompiledGraph: A runnable graph object ready for execution.
    """
    # 1. Initialize the Graph with the State Schema
    workflow = StateGraph(VideoSecurityState)

    # 2. Add Nodes (The Workers)
    workflow.add_node("indexer", index_video_node)
    workflow.add_node("auditor", audit_content_node)

    # 3. Define Edges (The Logic Flow)
    workflow.set_entry_point("indexer")

    # Connect 'indexer' -> 'auditor'
    # Kya aur Kyu: Jaise hi Azure Video Indexer video se transcript nikaal le, us text ko 
    # check karne ke liye 'auditor' (LLM) ke paas bhej do.
    workflow.add_edge("indexer", "auditor")

    # Connect 'auditor' -> END
    # Kya aur Kyu: Jab LLM check karke JSON flag bana de, toh process ko END kar do.
    workflow.add_edge("auditor", END)

    # 4. Compile the Graph
    # Ye poore flow ko lock karke ek executable app bana deta hai jise hum API se call kar sakte hain.
    app = workflow.compile()

    return app

# Expose the runnable app for import by the API or CLI (FastAPI me yahi import hoga)
app = create_graph()
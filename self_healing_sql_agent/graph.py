from langgraph.graph import StateGraph, END
from state import AgentState
from nodes import (
    retrieve_schema_node,
    generate_sql_node,
    execute_sql_node,
    critique_and_fix_node,
    narrate_results_node
)

def route_execution(state: AgentState) -> str:
    """
    Conditional routing logic:
    - If error exists AND retries < 3 -> route to 'critique'
    - If error exists AND retries >= 3 -> route to 'narrate' (reporting failure)
    - If no error -> route to 'narrate'
    """
    if state.get("execution_error") is not None:
        if state["retry_count"] < 3:
            return "critique"
        else:
            return "narrate"
    return "narrate"

# Build StateGraph
workflow = StateGraph(AgentState)

# Register Nodes
workflow.add_node("retrieve_schema", retrieve_schema_node)
workflow.add_node("generate_sql", generate_sql_node)
workflow.add_node("execute_sql", execute_sql_node)
workflow.add_node("critique_and_fix", critique_and_fix_node)
workflow.add_node("narrate_results", narrate_results_node)

# Define Linear Edges
workflow.set_entry_point("retrieve_schema")
workflow.add_edge("retrieve_schema", "generate_sql")
workflow.add_edge("generate_sql", "execute_sql")

# Define Conditional Edges for Self-Healing Loop
workflow.add_conditional_edges(
    "execute_sql",
    route_execution,
    {
        "critique": "critique_and_fix",
        "narrate": "narrate_results"
    }
)

# Loop back from critique to execution sandbox
workflow.add_edge("critique_and_fix", "execute_sql")
workflow.add_edge("narrate_results", END)

# Compile Graph
app = workflow.compile()
# -------------------------------
# GRAPH CREATION
# -------------------------------
from langgraph.constants import END
from langgraph.graph import StateGraph

from src.entity.finance_state import State
from src.helpers.desicions import should_continue
from src.nodes.financial_instrument_picker import llm_investment_executor_node, investment_tools_node
from src.nodes.portfolio_allocator import llm_portfolio_node, portfolio_tools_node
from src.nodes.transaction_analyzer import llm_transaction_analyzer_node, transaction_analyzer_tools_node


def create_agent():
    graph = StateGraph(State)

    # --- Add nodes ---
    graph.add_node("llm_analyzer", llm_transaction_analyzer_node)
    graph.add_node("transaction_analyzer_tools", transaction_analyzer_tools_node)
    graph.add_node("portfolio_llm", llm_portfolio_node)
    graph.add_node("portfolio_tools", portfolio_tools_node)
    graph.add_node("llm_investment_executor", llm_investment_executor_node)
    graph.add_node("investment_tools", investment_tools_node)

    # --- Entry Point ---
    graph.set_entry_point("llm_analyzer")

    # --- Add Edges ---
    # graph.add_conditional_edges("llm_analyzer", should_continue, {"transaction_analyzer_tools": "transaction_analyzer_tools", END: "portfolio_llm"})
    # graph.add_edge("transaction_analyzer_tools", "llm_analyzer")  # back from tools
    # graph.add_edge("portfolio_llm", "portfolio_tools")
    # graph.add_edge("portfolio_tools", "llm_investment_executor")
    # graph.add_edge("llm_investment_executor", "investment_tools")
    # graph.add_edge("investment_tools", END)

    # --- Add Edges ---
    graph.add_conditional_edges("llm_analyzer", should_continue,{"transaction_analyzer_tools": "transaction_analyzer_tools",END: "transaction_analyzer_tools"})
    graph.add_edge("transaction_analyzer_tools", "portfolio_llm")
    graph.add_edge("portfolio_llm", "portfolio_tools")
    graph.add_edge("portfolio_tools", "llm_investment_executor")
    graph.add_edge("llm_investment_executor", "investment_tools")
    graph.add_edge("investment_tools", END)

    return graph.compile()


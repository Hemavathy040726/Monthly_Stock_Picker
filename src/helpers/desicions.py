# -------------------------------
# DECISION LOGIC
# -------------------------------
from langgraph.constants import END
from src.entity.finance_state import State


def should_continue(state: State):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "transaction_analyzer_tools"
    return END
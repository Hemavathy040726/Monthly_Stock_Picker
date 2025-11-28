# src/nodes/transaction_analyzer.py
from langchain_core.messages import ToolMessage, AIMessage
from src.config import llm_client
from src.entity.finance_state import State
from src.helpers.currency_formatter import format_currency_inr
from src.tools.pdf_reader import pdf_reader_tool
from src.tools.tools_registry import create_tool_registry
from src.utils import retry, safe_float, prune_messages
from src.logger import log
from src.helpers.pretty_print import section, success, money, result_box, info
import re


@log.time_node("transaction_analyzer")
def llm_transaction_analyzer_node(state: State) -> dict:
    log.info("Agent 1: Transaction Analyzer Started")
    section("Agent 1 : Transaction Analyzer Agent Started")
    info("Start Analyzing Transactions")
    messages = prune_messages(state["messages"])

    try:
        tools = [pdf_reader_tool]
        llm_with_tools = llm_client.bind_tools(tools, tool_choice="auto")

        response = llm_with_tools.invoke(messages)
        state["messages"].append(response)

        if hasattr(response, "tool_calls") and response.tool_calls:
            log.info("Tool call detected", {"tool_calls": [tc["name"] for tc in response.tool_calls]})
            return {"messages": state["messages"]}  # go to tools node

        # Parse savings from final response
        total_savings = _extract_savings_from_response(response.content)
        state["total_savings"] = total_savings
        state["formatted_savings"] = format_currency_inr(total_savings)
        if state.get("total_savings", 0) > 0:
            print(f"-------Final Result of Agent 1--------")
            print(f"Total savings in Current Month: {money(state['total_savings'])}")
        log.info("Savings extracted", {"total_savings": total_savings})

    except Exception as e:
        log.error("Transaction analyzer failed", {"error": str(e)})
        state["total_savings"] = 0.0
        state["formatted_savings"] = format_currency_inr(0.0)

    return state


def _extract_savings_from_response(content: str) -> float:
    """Extract and compute savings by parsing incomes and expenses."""
    log.debug("Extracting savings from response", {"content": content[:200]})

    # Patterns for amounts (e.g., Rs.50000, ₹50000, or 50000)
    amount_pattern = r"(?:Rs\.?|₹)?\s*([\d,]+)(?:\.\d+)?\b"

    # Find all amounts with their context
    amounts = []
    for line in content.splitlines():
        match = re.search(amount_pattern, line, re.I)
        if match:
            amount = safe_float(match.group(1).replace(",", ""))
            context = line.lower()
            amounts.append((amount, context))

    # Categorize as income (received) or expense (sent/spent)
    income = sum(a for a, ctx in amounts if "received" in ctx or "salary" in ctx)
    expenses = sum(a for a, ctx in amounts if "sent" in ctx or "spent" in ctx)

    # Compute savings
    savings = income - expenses
    log.debug("Computed savings", {"income": income, "expenses": expenses, "savings": savings})

    # Fallback: look for explicit savings mention
    if savings <= 0:
        savings_patterns = [
            r"savings[:\s]*₹?([\d,]+\.?\d*)",
            r"remaining[:\s]*₹?([\d,]+\.?\d*)",
            r"(\d{4,})"
        ]
        for pattern in savings_patterns:
            match = re.search(pattern, content.replace(",", ""), re.I)
            if match:
                savings = safe_float(match.group(1))
                log.debug("Used fallback savings pattern", {"savings": savings})
                break

    return max(0.0, savings)


@log.time_node("transaction_analyzer_tools")
@retry(max_attempts=3)
def transaction_analyzer_tools_node(state: State):
    registry = create_tool_registry()
    tool_messages = []
    last = state["messages"][-1]

    for call in getattr(last, "tool_calls", []):
        try:
            tool_fn = registry[call["name"]]
            result = tool_fn.invoke(call["args"])
            # After PDF is read, re-invoke LLM to process the content
            tool_messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
            log.debug("Tool executed", {"tool": call["name"], "success": True})

            # Add the PDF content as a new message for LLM to analyze
            state["messages"].append(AIMessage(content=f"PDF Content: {result}"))
            llm_with_tools = llm_client.bind_tools([], tool_choice="none")  # No more tools needed
            response = llm_with_tools.invoke(state["messages"])
            state["messages"].append(response)

            # Parse savings from the LLM's final response
            total_savings = _extract_savings_from_response(response.content)
            state["total_savings"] = total_savings
            state["formatted_savings"] = format_currency_inr(total_savings)
            log.info("Final savings extracted", {"total_savings": total_savings})

        except Exception as e:
            error_msg = f"Tool {call['name']} failed: {str(e)}"
            tool_messages.append(ToolMessage(content=error_msg, tool_call_id=call["id"]))
            log.error("Tool execution failed", {"tool": call["name"], "error": str(e)})
            state["total_savings"] = 0.0
            state["formatted_savings"] = format_currency_inr(0.0)

    return {
        "messages": tool_messages,
        "total_savings": state.get("total_savings", 0.0),
        "formatted_savings": state.get("formatted_savings", format_currency_inr(0.0))
    }
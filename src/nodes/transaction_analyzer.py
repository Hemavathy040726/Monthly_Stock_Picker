from langchain_core.messages import ToolMessage, AIMessage

from src.config import llm_client
from src.entity.finance_state import State
from src.helpers.currency_formatter import format_currency_inr
from src.tools.pdf_reader import pdf_reader_tool
from src.tools.tools_registry import create_tool_registry
import re

def llm_transaction_analyzer_node(state: State):
    """LLM node to extract savings from PDF."""
    global final_response
    print("--------------------------------------------")
    print("Agent 1 : Transaction Analyzer Agent Started")
    print("--------------------------------------------")

    tools = [pdf_reader_tool]
    llm_with_tools = llm_client.bind_tools(tools)
    messages = state["messages"]
    print("Start Analyzing Transactions")
    response = llm_with_tools.invoke(messages)

    if hasattr(response, "tool_calls") and response.tool_calls:
        # Tool was called, now run the tool
        for call in response.tool_calls:
            result = pdf_reader_tool.invoke(call["args"])


            # Feed the result back into the conversation
            messages.append(response)
            messages.append(AIMessage(content=f"Tool {call['name']} output: {result}"))

            # Re-invoke LLM with the new context
            final_response = llm_with_tools.invoke(messages)

    # Append LLM response to state
    state["messages"].append(final_response)

    # Parse total savings from LLM output
    try:
        match = re.search(r"[-+]?\d*\.\d+|\d+", final_response.content)
        if match:
            state["total_savings"] = float(match.group())
            state["formatted_savings"] = format_currency_inr(state["total_savings"])
            print("-------Final Result of Agent 1--------")
            print(f"💰 Total savings in Current Month: {state['formatted_savings']}")
        else:
            state["total_savings"] = 0.0
            state["formatted_savings"] = format_currency_inr(0.0)
    except Exception as e:
        state["total_savings"] = 0.0
        state["formatted_savings"] = format_currency_inr(0.0)
        print(f"Error parsing savings: {e}")

    return {
        "messages": state["messages"],
        "total_savings": state["total_savings"],
        "formatted_savings": state["formatted_savings"]
    }





def transaction_analyzer_tools_node(state: State):
    tool_registry = create_tool_registry()
    last_message = state["messages"][-1]
    tool_messages = []

    for tool_call in getattr(last_message, "tool_calls", []):
        tool_name = tool_call["name"]
        if tool_name in tool_registry:
            result = tool_registry[tool_name].invoke(tool_call["args"])
            tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
    return {"messages": tool_messages}





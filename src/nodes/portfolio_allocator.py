from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from src.config import llm_client
from src.entity.finance_state import State
from src.helpers.load_prompt import load_prompt
from src.tools.portfolio_builder import portfolio_builder_tool
from src.tools.tools_registry import create_tool_registry


def llm_portfolio_node(state: State):
    """LLM generates portfolio plan."""
    print("\n")
    print("--------------------------------------------")
    print("Agent 2 : Portfolio Generator Agent Started")
    print("--------------------------------------------")

    # Load system prompt from external file
    system_prompt = load_prompt("system_prompt_portfolio_builder.txt")
    user_prompt = load_prompt("user_prompt_portfolio_builder.txt")
    human_prompt = user_prompt.format(
        total_savings=state["total_savings"],
        user_age=state["user_age"],
        insured=state["insured"],
    )

    tools = [portfolio_builder_tool]
    llm_with_tools = llm_client.bind_tools(tools)
    messages = state["messages"] + [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)

    ]
    print("Building an investment portfolio using the '100 - age' rule, for the Following details")
    print("Total Savings: ", state["total_savings"])
    print("Age: ", state["user_age"])
    print("Insured Status: ", state["insured"])
    response = llm_with_tools.invoke(messages)
    state["messages"].append(response)
    return state

def portfolio_tools_node(state: State):
    """Execute portfolio tool calls."""
    registry = create_tool_registry()
    last = state["messages"][-1]
    for call in getattr(last, "tool_calls", []):
        tool_fn = registry[call["name"]]
        result = tool_fn.invoke(call["args"])
        state["portfolio"] = result
        print("-------Final Result of Agent 2--------")
        print(f"📊 Portfolio Allocated: {state['portfolio']}")
        state["messages"].append(ToolMessage(content=str(result), tool_call_id=call["id"]))
    return state



import re
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from src.helpers.load_prompt import load_prompt
from src.tools.tools_registry import create_tool_registry
from src.config import llm_client
from src.entity.finance_state import State
from src.tools.search_tool import web_search_tool


def llm_investment_executor_node(state: dict):
    """Agent 3: Executes a real trade (Equity only) via Zerodha after human confirmation."""
    print("\n")
    print("--------------------------------------------")
    print("Agent 3 : Instrument Picker Agent Started")
    print("--------------------------------------------")


    tools = [web_search_tool]
    llm_with_tools = llm_client.bind_tools(tools)

    print("As of now, Picking instruments for Equities alone")

    # --- Extract equity amount safely ---
    equity_amount_str = state["portfolio"].get("Equity (Stocks)", "₹0")

    # Remove ₹, commas, and convert to float
    equity_amount = float(re.sub(r"[₹,]", "", equity_amount_str))

    system_prompt_from_file = load_prompt("system_prompt_inst_picker.txt")
    user_prompt = load_prompt("user_prompt_inst_picker.txt")
    human_prompt = user_prompt.format(equity_amount=equity_amount)

    if not equity_amount:
        print("⚠️ No equity amount found. Skipping trade execution.")
        return state

    system_prompt = SystemMessage(content=system_prompt_from_file)

    messages = state["messages"] + [system_prompt]

    # --- Step 1: LLM picks top stocks ---
    search_prompt = HumanMessage(content=human_prompt)
    messages.append(search_prompt)

    search_result = web_search_tool.invoke({"query": "top Indian stocks to buy now"})
    print("🔎 Finding best stocks...")

    # --- Step 2: LLM suggests one stock ---
    decision_prompt = HumanMessage(content=(
        f"From the following stock list, suggest one stock to buy within ₹{equity_amount}.\n"
        f"Then ask for human confirmation before buying.\n\n"
        f"Search Results:\n{search_result}"
    ))

    response = llm_client.invoke(messages + [decision_prompt])
    suggestion = response.content
    print("-------Final Result of Agent 3--------")
    print("💡 LLM Suggestion:", suggestion)

    # --- Step 3: Human confirmation for Buying ---
    confirmation = input("\n🤔 Do you want to confirm this purchase? (yes/no): ").strip().lower()
    if confirmation.lower() != "yes":
        print("❌ Purchase cancelled by user.")
        state["investment_execution"] = "Cancelled by user"
        return state

    # --- Step 4: Execute trade via Zerodha ---
    print("Will connect to zerodha API in next module")
    return state



def investment_tools_node(state: State):
    registry = create_tool_registry()
    last = state["messages"][-1]
    for call in getattr(last, "tool_calls", []):
        # Map any unexpected names
        tool_name = call["name"]
        if tool_name == "get_search_tool":
            tool_name = "web_search_tool"

        tool_fn = registry[tool_name]
        result = tool_fn.invoke(call["args"])
        state["investment_instruments"] = result
        print(f"📈 Instruments stored in state: {state['investment_instruments']}")
        state["messages"].append(ToolMessage(content=str(result), tool_call_id=call["id"]))
    return state

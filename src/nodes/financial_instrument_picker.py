# src/nodes/financial_instrument_picker.py
import json
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from src.helpers.load_prompt import load_prompt
from src.config import llm_client
from src.entity.finance_state import State
from src.utils import safe_float, prune_messages
from src.logger import log
from src.helpers.pretty_print import banner, stock_recommendation, success, warning, section


@log.time_node("llm_investment_executor")
def llm_investment_executor_node(state: State) -> dict:
    """
    Final Agent: Picks ONE stock, shows price & quantity, asks for human confirmation.
    Uses external prompt file: prompts/user_prompt_inst_picker_final.txt
    """
    log.info("Agent 3: Investment Instrument Picker Started")
    section("Agent 3 : Instrument Picker Agent Started")
    # === 1. Extract Equity Amount ===
    portfolio = state.get("portfolio") or {}
    equity_str = portfolio.get("Equity (Stocks)", "₹0")
    equity_amount = safe_float(equity_str.replace("₹", "").replace(",", ""))

    if equity_amount < 5000:
        log.warning("Equity allocation too low", {"amount": equity_amount})
        print("Equity allocation below ₹5,000. Skipping stock picking.")
        warning(f"Equity too low: {equity_str} → Skipping stock picking")
        state["investment_instruments"] = ["Skipped: Low equity"]
        state["investment_instruments"] = ["Skipped: Low equity amount"]
        return state

    try:
        # === 2. Find search results from previous tool call ===
        search_content = "No recent search results available."
        for msg in reversed(state["messages"]):
            if isinstance(msg, ToolMessage) and len(str(msg.content)) > 100:
                search_content = str(msg.content)
                break

        # === 3. Load external final prompt ===
        prompt_template = load_prompt("user_prompt_inst_picker.txt")
        final_prompt_text = prompt_template.format(
            equity_amount=equity_amount,
            search_content=search_content[:12000]  # Limit context
        )

        # === 4. Build message history ===
        messages = prune_messages(state["messages"], max_messages=20) + [
            SystemMessage(content=load_prompt("system_prompt_inst_picker.txt")),
            HumanMessage(content=final_prompt_text)
        ]

        # === 5. Show header ===
        #banner("BEST STOCK RECOMMENDATION FOR YOU", "✨", 70)


        # === 6. Get final suggestion from LLM (no tool calling) ===
        response = llm_client.invoke(messages)
        suggestion = response.content.strip()

        stock_recommendation(suggestion)

        # === 7. Human confirmation ===
        confirm = input("\nDo you want to confirm this purchase? (yes/no): ").strip().lower()

        if confirm in ["yes", "y"]:
            success("Purchase confirmed! Proceeding to Zerodha API in next phase...")
            state["investment_instruments"] = [suggestion]
            state["investment_execution"] = "confirmed_by_user"
        else:
            warning("Purchase cancelled by user.")
            state["investment_instruments"] = ["Cancelled by user"]
            state["investment_execution"] = "cancelled"

        print("Thank you")
        log.info("Stock picking completed", {"confirmed": confirm in ["yes", "y"]})
        print("\nThank you for using Monthly Stock Picker!")
        print("Made with ❤️ for smart investors\n")

    except Exception as e:
        error_msg = f"Stock picker failed: {str(e)}"
        log.error("Investment executor error", {"error": str(e)})
        print(error_msg)
        state["investment_instruments"] = [error_msg]

    return state


# This node is kept only for compatibility — it will rarely run
@log.time_node("investment_tools")
def investment_tools_node(state: State) -> dict:
    log.info("Investment tools node executed (usually skipped in final flow)")
    # No action needed — final decision already made in executor node
    return state
# nodes/portfolio_allocator.py
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from src.config import llm_client
from src.entity.finance_state import State
from src.helpers.load_prompt import load_prompt
from src.tools.portfolio_builder import portfolio_builder_tool
from src.tools.tools_registry import create_tool_registry
from src.utils import retry, prune_messages, safe_float
from src.helpers.pretty_print import section, result_box, info, money
from src.logger import log

import json
import re


@log.time_node("portfolio_llm")
def llm_portfolio_node(state: State) -> dict:
    """LLM generates portfolio allocation plan with full resilience."""
    log.info("Agent 2: Portfolio Generator Agent Started", {
        "total_savings": state.get("total_savings"),
        "user_age": state.get("user_age"),
        "insured": state.get("insured")
    })
    section("Agent 2 : Portfolio Generator Agent Started")
    info("Building an investment portfolio using the '100 - age' rule")
    print(f"Total Savings : {money(state['total_savings'])}")
    print(f"Age           : {state['user_age']}")
    print(f"Insured       : {state['insured']}\n")

    messages = prune_messages(state["messages"], max_messages=15)

    try:
        system_prompt = load_prompt("system_prompt_portfolio_builder.txt")
        user_prompt_template = load_prompt("user_prompt_portfolio_builder.txt")

        # Safely format prompt
        total_savings = state.get("total_savings") or 0.0
        user_age = state.get("user_age") or 35
        insured = state.get("insured", False)

        human_prompt = user_prompt_template.format(
            total_savings=total_savings,
            user_age=user_age,
            insured=insured
        )

        tools = [portfolio_builder_tool]
        llm_with_tools = llm_client.bind_tools(
            tools,
            tool_choice={"type": "function", "function": {"name": "portfolio_builder_tool"}}
        )

        full_messages = messages + [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]

        log.debug("Invoking LLM for portfolio allocation")
        response = llm_with_tools.invoke(full_messages)

        if not response:
            raise ValueError("LLM returned empty response")

        state["messages"].append(response)
        log.info("Portfolio LLM responded", {"has_tool_calls": bool(getattr(response, "tool_calls", None))})

    except Exception as e:
        log.error("Portfolio LLM node failed", {
            "error": str(e),
            "total_savings": state.get("total_savings"),
            "fallback_used": True
        })
        # Fallback: use rule-based allocation
        state["portfolio"] = _fallback_portfolio_allocation(
            total_savings=state.get("total_savings", 0.0),
            user_age=state.get("user_age", 35),
            insured=state.get("insured", False)
        )
        state["messages"].append(
            AIMessage(content="[FALLBACK] Used rule-based portfolio allocation due to LLM failure."))

    return state


@log.time_node("portfolio_tools")
@retry(max_attempts=3, delay=1.5)
def portfolio_tools_node(state: State) -> dict:
    """Execute portfolio_builder_tool with full resilience."""
    registry = create_tool_registry()
    last_message = state["messages"][-1]
    tool_messages = []

    tool_calls = getattr(last_message, "tool_calls", [])
    if not tool_calls:
        log.warning("No tool calls found in portfolio LLM response")
        # Use fallback if tool wasn't called
        state["portfolio"] = _fallback_portfolio_allocation(
            total_savings=state.get("total_savings", 0.0),
            user_age=state.get("user_age", 35),
            insured=state.get("insured", False)
        )
        log.info("Fallback portfolio applied (no tool call)", {"portfolio": state["portfolio"]})
        return state

    for call in tool_calls:
        tool_name = call["name"]
        args = call["args"]

        try:
            log.debug("Executing portfolio tool", {"tool": tool_name, "args": args})

            # Fix common LLM argument type issues
            args = {
                "total_savings": float(args.get("total_savings", 0)),
                "user_age": int(args.get("user_age", 35)),
                "insured": args.get("insured") in (True, "true", "True")
            }

            tool_fn = registry[tool_name]
            result = tool_fn.invoke(args)

            if isinstance(result, dict) and "error" in result:
                raise ValueError(result["error"])

            state["portfolio"] = result
            tool_messages.append(ToolMessage(content=json.dumps(result), tool_call_id=call["id"]))
            if state.get("portfolio"):
                result_box("FINAL PORTFOLIO ALLOCATION", state["portfolio"])
            log.info("Portfolio successfully built", {"portfolio": result})

        except Exception as e:
            log.error("Portfolio tool execution failed", {
                "tool": tool_name,
                "args": args,
                "error": str(e),
                "fallback_used": True
            })
            fallback = _fallback_portfolio_allocation(
                total_savings=state.get("total_savings", 0.0),
                user_age=state.get("user_age", 35),
                insured=state.get("insured", False)
            )
            state["portfolio"] = fallback
            error_content = f"[ERROR] Portfolio tool failed: {str(e)}. Using fallback allocation."
            tool_messages.append(ToolMessage(content=error_content, tool_call_id=call["id"]))

    state["messages"].extend(tool_messages)
    return state


def _fallback_portfolio_allocation(total_savings: float, user_age: int, insured: bool) -> dict:
    """Pure Python fallback using 100 - age rule."""
    if total_savings <= 0:
        return {"Emergency Fund": "₹0.00", "Note": "No savings to invest"}

    equity_pct = max(10, min(90, 100 - user_age))
    bond_pct = 80 - equity_pct + 20
    emergency_pct = 10
    insurance_pct = 10 if not insured else 0

    total_pct = equity_pct + bond_pct + emergency_pct + insurance_pct
    equity_pct = equity_pct / total_pct * 90
    bond_pct = bond_pct / total_pct * 90
    emergency_pct = 10

    amount = lambda pct: total_savings * pct / 100

    return {
        "Equity (Stocks)": f"₹{amount(equity_pct):,.2f}",
        "Bond Securities": f"₹{amount(bond_pct):,.2f}",
        "Emergency Fund": f"₹{amount(emergency_pct):,.2f}",
        "Insurance (Recommended)": f"₹{amount(insurance_pct):,.2f}" if not insured else None
    }
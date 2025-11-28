# -------------------------------
# RUN
# -------------------------------
import uuid

from langchain_core.messages import SystemMessage, HumanMessage

from src.helpers.pretty_print import banner
from src.logger import log

from src.graph.graph_creation import create_agent
from src.helpers.load_prompt import load_prompt




if __name__ == "__main__":
    print("LLM initialized with model: llama-3.3-70b-versatile")
    print("Running integrated agent...\n")

    banner("MONTHLY STOCK PICKER v1.0", "=", 70)
    agent = create_agent()

    system_prompt = load_prompt("system_prompt_transaction_analyzer.txt")
    user_prompt = load_prompt("user_prompt_transaction_analyzer.txt")
    human_prompt = user_prompt.format(test_pdf = "data/transactions_november.pdf")
    initial_state = {
        "messages": [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ],
        "total_savings": None,
        "user_age": 35,
        "insured": False,
        "portfolio": None,
        "investment_instruments": None
    }

    print("🤖 Running integrated agent...\n")
    result = agent.invoke(initial_state)
    print("------Thank you------")
    print("Agent finished. Have a great investing month!".center(70))
    print("Thank you".center(70, " "))


#
# if __name__ == "__main__":
#     run_id = str(uuid.uuid4())[:8]
#     log.info("Agent run started", {"run_id": run_id})
#
#     agent = create_agent()
#     initial_state = {"messages": [
#         SystemMessage(content=system_prompt),
#         HumanMessage(content=human_prompt)
#     ], "total_savings": None, "user_age": 35, "insured": False, "portfolio": None, "investment_instruments": None,
#         "metadata": {"run_id": run_id}}
#
#     try:
#         result = agent.invoke(initial_state)
#         log.info("Agent completed successfully", {"run_id": run_id})
#     except Exception as e:
#         log.error("Agent crashed", {"run_id": run_id, "error": str(e)})
#
#     print("Agent finished. Check logs/agent.log for details.")
# -------------------------------
# RUN
# -------------------------------
from langchain_core.messages import SystemMessage, HumanMessage

from src.graph.graph_creation import create_agent
from src.helpers.load_prompt import load_prompt




if __name__ == "__main__":
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

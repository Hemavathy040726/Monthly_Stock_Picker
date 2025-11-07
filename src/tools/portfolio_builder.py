# -------------------------------
# Portfolio Builder
# -------------------------------
from langchain_core.tools import tool

@tool
def portfolio_builder_tool(total_savings: float, user_age: int, insured: bool) -> dict:
    """Build an investment portfolio using the '100 - age' rule and adjust for insurance."""
    if total_savings <= 0:
        return {"error": "No savings to invest."}

    # Apply the 100 - age rule for equity allocation
    equity_ratio = max(0, min(100 - user_age, 100)) / 100
    bond_ratio = 1 - equity_ratio

    # Set aside emergency fund (e.g., 10%)
    emergency_fund_ratio = 0.1
    investable_ratio = 1 - emergency_fund_ratio

    equity_ratio *= investable_ratio
    bond_ratio *= investable_ratio

    portfolio = {
        "Equity (Stocks)": equity_ratio,
        "Bond Securities": bond_ratio,
        "Emergency Fund": emergency_fund_ratio
    }

    if not insured:
        portfolio["Insurance"] = 0.1
        # Rebalance to make sure total = 1.0
        total = sum(portfolio.values())
        portfolio = {k: v / total for k, v in portfolio.items()}

    formatted = {k: f"₹{(v * total_savings):,.2f}" for k, v in portfolio.items()}
    return formatted
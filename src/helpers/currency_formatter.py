def format_currency_inr(amount: float) -> str:
    try:
        formatted = f"₹{amount:,.2f}"
        return formatted
    except Exception:
        return "₹0.00"
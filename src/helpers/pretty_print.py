# src/helpers/pretty_print.py
from datetime import datetime

def banner(text: str, char="=", length=70):
    print(f"\n{char * length}")
    print(f"{text.center(length)}")
    print(f"{char * length}\n")

def section(title: str):
    print(f"\n{'─' * 25} {title} {'─' * 25}")

def success(msg: str):
    print(f"✅ {msg}")

def info(msg: str):
    print(f"ℹ️  {msg}")

def warning(msg: str):
    print(f"⚠️  {msg}")

def money(amount: float):
    return f"₹{amount:,.2f}"

def result_box(title: str, data: dict):
    print(f"\n{'='*60}")
    print(f" {title} ".center(60, "█"))
    print(f"{'='*60}")
    for k, v in data.items():
        print(f"   {k:<20}: {v}")
    print(f"{'='*60}\n")

def stock_recommendation(stock_data: str):
    lines = stock_data.strip().splitlines()
    print(f"\n{'✨'*30}")
    print("    BEST STOCK RECOMMENDATION FOR YOU    ".center(60))
    print(f"{'✨'*30}\n")
    for line in lines:
        if "Stock:" in line or "Ticker:" in line:
            print(f"   {line}")
        elif "Price:" in line or "Shares:" in line or "Cost:" in line:
            print(f"   {line}")
        elif "Do you want to confirm" in line:
            print(f"\n{line}")
    print()
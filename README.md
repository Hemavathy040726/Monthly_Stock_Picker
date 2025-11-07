* * * * *

💼 Monthly Stock Picker --- AI Financial Planning System
======================================================

### 🧠 Powered by LLM + LangGraph + Tool-Integrated Agents

* * * * *

📘 Overview
-----------

**Monthly Stock Picker** is an **agentic AI system** that analyzes your monthly transaction data (from PDF statements), identifies potential savings, builds an investment portfolio using the **"100 - Age"** rule, and picks suitable stock instruments for investment.

This project demonstrates **multi-agent collaboration** using **LangGraph** and **LLM tool integration**, where each intelligent agent is responsible for a specific part of the financial decision-making process.

* * * * *

🏗️ Architecture
----------------

### ⚙️ Core Layers

| Layer | Folder | Description |
| --- | --- | --- |
| **Entities** | `src/entity` | Contains global state definitions shared across agents (`FinanceState`). |
| **Graph** | `src/graph` | Defines the agentic workflow using LangGraph. |
| **Nodes** | `src/nodes` | Each node represents an intelligent agent (Analyzer, Allocator, Picker). |
| **Tools** | `src/tools` | Tool layer providing LLM-accessible functions like PDF reading and portfolio building. |
| **Helpers** | `src/helpers` | Utility modules for formatting and decision-making logic. |
| **Prompts** | `src/prompts` | Contain all system and user prompts. |
| **Main** | `src/main.py` | Entry point initializing the LLM, registering tools, and running the multi-agent graph. |

* * * * *

🧩 Agents Overview
------------------

### 1️⃣ Transaction Analyzer Agent

**File:** `src/nodes/transaction_analyzer.py`

-   Reads and parses a monthly transaction PDF (`transactions_november.pdf`).

-   Uses the `pdf_reader_tool` to extract and summarize income, expenses, and savings.

-   Calculates the total amount available for investment.

**Tool Used:** `pdf_reader_tool`

* * * * *

### 2️⃣ Portfolio Allocator Agent

**File:** `src/nodes/portfolio_allocator.py`

-   Builds an investment portfolio using the **"100 - Age"** principle:

    -   Equity Allocation = 100 - Age (%)

    -   Remaining funds go into Bonds, Emergency Fund, and optionally Insurance.

-   Converts all values into formatted currency strings.

**Tool Used:** `portfolio_builder_tool`

* * * * *

### 3️⃣ Financial Instrument Picker Agent

**File:** `src/nodes/financial_instrument_picker.py`

-   Picks the best stock instruments for the **Equity** portion of the portfolio.

-   Currently uses a placeholder logic that recommends a stock and its buy/target range.

-   Future extension: integrates with **Zerodha Kite API** to execute real orders.

**Tool Used:** `search_tool` (LLM-based query placeholder)

* * * * *

🧠 Tool Registry
----------------

**File:** `src/tools/tools_registry.py`

Centralized registry that exposes all tools to the LLM.

| Tool | Description |
| --- | --- |
| `pdf_reader_tool` | Reads and summarizes a PDF of transactions. |
| `portfolio_builder_tool` | Allocates savings based on the "100 - Age" rule. |
| `search_tool` | (Planned) Searches stock instruments via financial APIs. |

* * * * *

🧱 State Definition
-------------------

**File:** `src/entity/finance_state.py`

Defines the `FinanceState` shared across all agents:

```
class State(TypedDict):
    messages: Annotated[list, add_messages]
    total_savings: Annotated[Union[float, None], update_savings]
    formatted_savings: Annotated[Optional[str], update_formatted_savings]
    user_age: Annotated[Union[int, None], keep_first]
    insured: Annotated[Union[bool, None], keep_first]
    portfolio: Annotated[Union[dict, None], keep_first]
    investment_instruments: Annotated[Union[list, None], keep_first]

```

* * * * *

🔁 Graph Workflow
-----------------

**File:** `src/graph/graph_creation.py`

Defines the agent flow:

```
Transaction Analyzer ➜ Portfolio Allocator ➜ Stock Picker ➜ (Zerodha Execution Future)

```

Each node updates the shared state and passes it along the graph.

* * * * *

🚀 Run the Project
------------------

### 1️⃣ Create Virtual Environment

```
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows

```

### 2️⃣ Install Dependencies

```
pip install -r requirements.txt

```

### 3️⃣ Place Your PDF

Add your monthly statement under:

```
data/transactions_november.pdf

```

### 4️⃣ Run the Agents

```
python src/main.py

```

### 🧾 Example Output

```

✅ LLM initialized with model: llama-3.3-70b-versatile
🤖 Running integrated agent...

--------------------------------------------
Agent 1 : Transaction Analyzer Agent Started
--------------------------------------------
Start Analyzing Transactions
Reading data/transactions_november.pdf
✅ Extracted PDF content from: data/transactions_november.pdf
-------Final Result of Agent 1--------
💰 Total savings in Current Month: ₹47,800.00


--------------------------------------------
Agent 2 : Portfolio Generator Agent Started
--------------------------------------------
Building an investment portfolio using the '100 - age' rule, for the Following details
Total Savings:  47800.0
Age:  35
Insured Status:  False
-------Final Result of Agent 2--------
📊 Portfolio Allocated: {'Equity (Stocks)': '₹25,420.91', 'Bond Securities': '₹13,688.18', 'Emergency Fund': '₹4,345.45', 'Insurance': '₹4,345.45'}


--------------------------------------------
Agent 3 : Instrument Picker Agent Started
--------------------------------------------
As of now, Picking instruments for Equities alone
🔎 Finding best stocks...
-------Final Result of Agent 3--------
💡 LLM Suggestion: Based on the search results, I suggest buying 434 shares of Bank of Maha at ₹58.16 per share, which would cost approximately ₹25231.44, within your budget of ₹25420.91.

Do you want to confirm buying 434 shares of Bank of Maha at ₹58.16 per share?

🤔 Do you want to confirm this purchase? (yes/no): yes
Will connect to zerodha API in next module
------Thank you------

```

* * * * *

🧠 Future Enhancements
----------------------

| Feature | Description |
| --- | --- |
| 🔗 **Zerodha Kite Integration** | Automate order placement for stock picks. |
| 💰 **Expense Categorization** | NLP-based classification of expenses. |
| 📈 **Goal Planning** | Track goals and suggest monthly investments. |
| 💬 **Interactive Chat** | Query your portfolio and performance conversationally. |
| 🪄 **Visualization Dashboard** | Show charts and analytics (Streamlit/Flutter). |

* * * * *

🧰 Tech Stack
-------------

| Component | Technology |
| --- | --- |
| **Language Model** | Llama-3.3-70B (via Groq / local inference) |
| **Framework** | LangGraph |
| **Orchestration** | Python-based Graph Flow |
| **Tools Integration** | LangChain-style `@tool` decorators |
| **PDF Processing** | PyPDF / LangGraph Tool Interface |
| **State Management** | TypedDict (`FinanceState`) |

* * * * *

📁 Project Structure
--------------------

```
MonthlyStockPicker/
│
├── src/
│   ├── main.py
│   ├── config.py
│   ├── entity/
│   │   └── finance_state.py
│   ├── graph/
│   │   └── graph_creation.py
│   ├── helpers/
│   │   ├── currency_formatter.py
│   │   └── desicions.py
│   ├── nodes/
│   │   ├── transaction_analyzer.py
│   │   ├── portfolio_allocator.py
│   │   └── financial_instrument_picker.py
│   |── tools/
│   |   ├── pdf_reader.py
│   |   ├── portfolio_builder.py
│   |   ├── search_tool.py
│   |   └── tools_registry.py
|   |___ prompts/
|        |_  system_prompt_inst_picker.txt
|        |_  system_prompt_portfolio_builder.txt
|        |_  system_prompt_transaction_analyzer.txt
|        |_  user_prompt_portfolio_builder.txt
|        |_  user_prompt_inst_picker.txt
|        |_  user_prompt_transaction_analyzer.txt
│  
├── requirements.txt
└── data/
    └── transactions_november.pdf

```

* * * * *

🧑‍💻 Author
------------

**Hemavathy .M**\
Agentic AI | LLM-Orchestrated Systems | Financial Reasoning\
✨ *"Building a legacy-grade intelligent financial ecosystem."*

* * * * *

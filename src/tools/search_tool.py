# -------------------------------
# Search Tool
# -------------------------------
# import tavily
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import os
from langchain.tools import tool
from langchain_tavily import TavilySearch
import os
load_dotenv()

# web_search_tool = TavilySearch(
#     name="web_search_tool",
#     max_results=3,
#     search_depth="advanced",
#     tavily_api_key=os.getenv("TAVILY_API_KEY")
# )



tavily = TavilySearch(
    max_results=5,
    search_depth="advanced",
    tavily_api_key=os.getenv("TAVILY_API_KEY")
)

@tool
def web_search_tool(query: str):
    """Search the web using Tavily."""
    return tavily.run(query)
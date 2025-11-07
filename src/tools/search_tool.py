# -------------------------------
# Search Tool
# -------------------------------

from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import os
load_dotenv()

web_search_tool = TavilySearch(
    name="web_search_tool",
    max_results=3,
    search_depth="advanced",
    tavily_api_key=os.getenv("TAVILY_API_KEY")
)
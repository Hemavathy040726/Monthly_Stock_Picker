# -------------------------------
# TOOL REGISTRY
# -------------------------------
from src.tools.pdf_reader import pdf_reader_tool
from src.tools.portfolio_builder import portfolio_builder_tool
from src.tools.search_tool import web_search_tool


def get_all_tools():
    return [pdf_reader_tool, portfolio_builder_tool, web_search_tool]

def create_tool_registry():
    tools = get_all_tools()
    return {tool.name: tool for tool in tools}
# -------------------------------
# PDF Reader
# -------------------------------
import os

from langchain_core.tools import tool
from typing import Union
import PyPDF2

@tool
def pdf_reader_tool(pdf_path: str) -> Union[str, bool]:
    """Read a PDF file and return its extracted text."""
    print(f"Reading {pdf_path}")
    if not os.path.exists(pdf_path):
        print(f"❌ File does not exist: {pdf_path}")
        return False
    try:
        text = ""
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        print(f"✅ Extracted PDF content from: {pdf_path}")
        return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {str(e)}")
        return False

import os

def load_prompt(file_name: str) -> str:
    """Loads a text prompt from the src/prompts directory."""
    base_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
    file_path = os.path.join(base_dir, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

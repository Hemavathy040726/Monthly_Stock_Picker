# src/utils.py
import time
from functools import wraps
from typing import Callable, Any
from src.logger import log

def retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        log.error(f"Failed after {max_attempts} attempts", {"error": str(e)})
                        raise
                    log.warning(f"Retry {attempt}/{max_attempts}", {"error": str(e)})
                    time.sleep(delay * (2 ** (attempt - 1)))  # Exponential backoff
            return None
        return wrapper
    return decorator

def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return float(''.join(c for c in value if c in '0123456789.'))
        return default
    except:
        return default

def prune_messages(messages: list, max_messages: int = 20):
    """Keep only system + last N messages"""
    if len(messages) <= max_messages:
        return messages
    system_msg = next((m for m in messages if m.type == "system"), None)
    recent = messages[-max_messages+1:]
    return [system_msg] + recent if system_msg else recent
# src/logger.py
import logging
import time
import json
from typing import Any, Dict, Optional
from pathlib import Path


class AgentLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger("FinanceAgent")
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)

        # File handler (detailed)
        fh = logging.FileHandler(log_dir / "agent.log", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        self.logger.handlers.clear()
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)

        self._initialized = True
        self.logger.info("AgentLogger initialized")

    def info(self, msg: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.INFO, msg, extra)

    def error(self, msg: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.ERROR, msg, extra)

    def warning(self, msg: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.WARNING, msg, extra)

    def debug(self, msg: str, extra: Optional[Dict[str, Any]] = None):
        self._log(logging.DEBUG, msg, extra)

    def _log(self, level: int, msg: str, extra: Optional[Dict[str, Any]]):
        extra = extra or {}
        extra_str = " | " + json.dumps(extra, ensure_ascii=False) if extra else ""
        self.logger.log(level, msg + extra_str)

    def time_node(self, node_name: str):
        """Decorator for timing node execution"""

        def decorator(func):
            def wrapper(state, *args, **kwargs):
                start = time.perf_counter()
                node_id = extra.get("run_id", "unknown") if (extra := state.get("metadata", {})) else "unknown"
                try:
                    result = func(state, *args, **kwargs)
                    duration = time.perf_counter() - start
                    self.info("Node completed", {
                        "node": node_name,
                        "duration_ms": round(duration * 1000, 2),
                        "run_id": node_id
                    })
                    return result
                except Exception as e:
                    duration = time.perf_counter() - start
                    self.error("Node failed", {
                        "node": node_name,
                        "duration_ms": round(duration * 1000, 2),
                        "error": str(e),
                        "run_id": node_id
                    })
                    raise

            return wrapper

        return decorator


log = AgentLogger()
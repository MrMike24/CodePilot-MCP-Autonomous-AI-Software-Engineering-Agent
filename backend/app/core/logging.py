import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any
from backend.app.core.config import settings

SENSITIVE_KEYS = {"api_key", "secret", "token", "password", "authorization", "llm_api_key", "github_token"}


def sanitize_log_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Sanitize dictionary to avoid logging sensitive fields."""
    cleaned = {}
    for key, value in data.items():
        if any(sens in key.lower() for sens in SENSITIVE_KEYS):
            cleaned[key] = "***REDACTED***"
        elif isinstance(value, dict):
            cleaned[key] = sanitize_log_dict(value)
        else:
            cleaned[key] = value
    return cleaned


class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter for telemetry and audit compliance."""

    def format(self, record: logging.LogRecord) -> str:
        log_object: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Include extra context attributes if provided
        if hasattr(record, "task_id"):
            log_object["task_id"] = getattr(record, "task_id")
        if hasattr(record, "agent"):
            log_object["agent"] = getattr(record, "agent")
        if hasattr(record, "tool"):
            log_object["tool"] = getattr(record, "tool")
        if hasattr(record, "run_id"):
            log_object["run_id"] = getattr(record, "run_id")

        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)

        return json.dumps(sanitize_log_dict(log_object))


def setup_logging() -> logging.Logger:
    """Configure system-wide structured logger."""
    root_logger = logging.getLogger("codepilot")
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Clear existing handlers
    if root_logger.handlers:
        root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)

    # Disable noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return root_logger


logger = setup_logging()

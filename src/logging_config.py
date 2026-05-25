import logging
import json
import sys
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Include extra fields if present
        extra_keys = [
            k
            for k in record.__dict__.keys()
            if k
            not in (
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
            )
        ]
        for k in extra_keys:
            try:
                payload[k] = record.__dict__[k]
            except Exception:
                payload[k] = str(record.__dict__[k])

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging(level: int = logging.INFO, log_file: str | None = None) -> None:
    """Configure root logging to emit structured JSON to stdout and optional file.

    This is intentionally lightweight and has no third-party dependencies.
    """
    root = logging.getLogger()
    root.setLevel(level)

    # Clear existing handlers to avoid duplicate logs during tests
    for h in list(root.handlers):
        root.removeHandler(h)

    formatter = JsonFormatter()

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    sh.setLevel(level)
    root.addHandler(sh)

    if log_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(formatter)
        fh.setLevel(level)
        root.addHandler(fh)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

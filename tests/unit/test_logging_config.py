import json
import logging
from pathlib import Path

from src.logging_config import JsonFormatter, configure_logging, get_logger


def test_json_formatter_outputs_valid_json():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="hello world",
        args=(),
        exc_info=None,
    )
    record.extra_field = "extra"

    formatted = formatter.format(record)
    parsed = json.loads(formatted)

    assert parsed["message"] == "hello world"
    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "test_logger"
    assert parsed["extra_field"] == "extra"
    assert "timestamp" in parsed


def test_json_formatter_includes_exc_info():
    formatter = JsonFormatter()
    try:
        raise ValueError("boom")
    except ValueError:
        import sys

        record = logging.LogRecord(
            name="t",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="failed",
            args=(),
            exc_info=sys.exc_info(),
        )
    payload = json.loads(formatter.format(record))
    assert "ValueError: boom" in payload["exc_info"]


def test_configure_logging_replaces_existing_handlers():
    root = logging.getLogger()
    sentinel = logging.NullHandler()
    root.addHandler(sentinel)

    configure_logging(level=logging.DEBUG)

    assert sentinel not in root.handlers
    assert root.level == logging.DEBUG
    assert len(root.handlers) == 1


def test_configure_logging_writes_to_file(tmp_path: Path):
    log_path = tmp_path / "bot.log"
    configure_logging(level=logging.INFO, log_file=str(log_path))

    logger = get_logger("file_test")
    logger.info("written to disk", extra={"trace_id": "abc"})
    for h in logging.getLogger().handlers:
        h.flush()

    contents = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert contents, "log file should have at least one line"
    parsed = json.loads(contents[-1])
    assert parsed["message"] == "written to disk"
    assert parsed["trace_id"] == "abc"


def test_get_logger_returns_namespaced_logger():
    assert get_logger("a.b.c").name == "a.b.c"

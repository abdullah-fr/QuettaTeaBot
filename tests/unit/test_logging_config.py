import json
import logging

from src.logging_config import JsonFormatter


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

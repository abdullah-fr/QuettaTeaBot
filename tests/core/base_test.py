import os
import json
from datetime import datetime


class BaseTest:
    """
    Base class for all Discord bot tests.

    Provides:
    - logging
    - shared helpers
    - bot_data.json access
    - assertions
    """

    BOT_DATA_FILE = "data/bot_data.json"

    # ----------------------------------
    # Test Lifecycle
    # ----------------------------------

    def setup_method(self):
        self.start_time = datetime.utcnow()
        self.logs = []

    def teardown_method(self):
        duration = datetime.utcnow() - self.start_time
        self.log(f"Test finished in {duration.total_seconds():.2f}s")

    # ----------------------------------
    # Logging
    # ----------------------------------

    def log(self, message: str):
        timestamp = datetime.utcnow().isoformat()
        entry = f"[{timestamp}] {message}"
        self.logs.append(entry)
        print(entry)

    # ----------------------------------
    # Path Helpers
    # ----------------------------------

    def project_root(self):
        return os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        )

    def bot_data_path(self):
        return os.path.join(self.project_root(), self.BOT_DATA_FILE)

    # ----------------------------------
    # JSON Helpers
    # ----------------------------------

    def read_bot_data(self) -> dict:
        path = self.bot_data_path()

        if not os.path.exists(path):
            return {}

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def write_bot_data(self, data: dict):
        with open(self.bot_data_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # ----------------------------------
    # Assertions
    # ----------------------------------

    def assert_key_exists(self, data, key):
        assert key in data, f"Missing expected key: {key}"

    def assert_not_empty(self, value, message="Value should not be empty"):
        assert value, message

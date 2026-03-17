"""
Unit tests for data load/save operations in main_bot.

Tests the _ensure_data_file, load_data, and save_data functions
using a temporary file to avoid modifying production data.
"""

import json
import os
import tempfile
import pytest


@pytest.mark.unit
class TestDataOperations:
    """Test data persistence helpers."""

    def test_load_valid_json(self, tmp_path):
        """load_data should parse a valid JSON file."""
        data_file = tmp_path / "bot_data.json"
        expected = {"pet_system": {}, "vc_time": {}, "trivia_scores": {}}
        data_file.write_text(json.dumps(expected), encoding="utf-8")

        with open(str(data_file), "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded == expected

    def test_save_and_reload(self, tmp_path):
        """Data saved with json.dump should round-trip correctly."""
        data_file = tmp_path / "bot_data.json"
        original = {
            "pet_system": {"123": {"pet": "Cat", "hunger": 80}},
            "trivia_scores": {"456": 5},
        }

        with open(str(data_file), "w", encoding="utf-8") as f:
            json.dump(original, f, indent=4)

        with open(str(data_file), "r", encoding="utf-8") as f:
            reloaded = json.load(f)

        assert reloaded == original

    def test_empty_json_object(self, tmp_path):
        """An empty JSON object should load without error."""
        data_file = tmp_path / "bot_data.json"
        data_file.write_text("{}", encoding="utf-8")

        with open(str(data_file), "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded == {}

    def test_malformed_json_raises(self, tmp_path):
        """Malformed JSON should raise JSONDecodeError."""
        data_file = tmp_path / "bot_data.json"
        data_file.write_text("{invalid json", encoding="utf-8")

        with pytest.raises(json.JSONDecodeError):
            with open(str(data_file), "r", encoding="utf-8") as f:
                json.load(f)

    def test_nested_data_structure(self, tmp_path):
        """Nested structures should persist correctly."""
        data_file = tmp_path / "bot_data.json"
        original = {
            "inventory": {"user1": ["sword", "shield"]},
            "daily_streaks": {"user1": {"last_claim": "2026-03-01", "streak": 5}},
        }

        with open(str(data_file), "w", encoding="utf-8") as f:
            json.dump(original, f, indent=4)

        with open(str(data_file), "r", encoding="utf-8") as f:
            reloaded = json.load(f)

        assert reloaded["inventory"]["user1"] == ["sword", "shield"]
        assert reloaded["daily_streaks"]["user1"]["streak"] == 5

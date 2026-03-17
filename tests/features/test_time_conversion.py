"""
Unit tests for the convert_to_12hr helper in RamadanBot.

Covers standard conversions, edge cases (midnight, noon), and boundaries.
"""

import pytest
from src.ramadan_features import RamadanBot


class FakeSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class FakeRandom:
    def randint(self, a, b):
        return a

    def choice(self, items):
        return items[0]


def _bot():
    return RamadanBot(
        bot=None,
        http_session_factory=lambda: FakeSession(),
        random_provider=FakeRandom(),
    )


@pytest.mark.unit
class TestConvertTo12Hr:
    """Test convert_to_12hr with various time inputs."""

    def test_midnight(self):
        """00:00 should be 12:00 AM."""
        assert _bot().convert_to_12hr("00:00") == "12:00 AM"

    def test_midnight_thirty(self):
        """00:30 should be 12:30 AM."""
        assert _bot().convert_to_12hr("00:30") == "12:30 AM"

    def test_early_morning(self):
        """05:15 should be 5:15 AM."""
        assert _bot().convert_to_12hr("05:15") == "5:15 AM"

    def test_noon(self):
        """12:00 should be 12:00 PM."""
        assert _bot().convert_to_12hr("12:00") == "12:00 PM"

    def test_afternoon(self):
        """13:45 should be 1:45 PM."""
        assert _bot().convert_to_12hr("13:45") == "1:45 PM"

    def test_evening(self):
        """18:30 should be 6:30 PM."""
        assert _bot().convert_to_12hr("18:30") == "6:30 PM"

    def test_before_midnight(self):
        """23:59 should be 11:59 PM."""
        assert _bot().convert_to_12hr("23:59") == "11:59 PM"

    def test_one_am(self):
        """01:00 should be 1:00 AM."""
        assert _bot().convert_to_12hr("01:00") == "1:00 AM"

    def test_eleven_am(self):
        """11:00 should be 11:00 AM."""
        assert _bot().convert_to_12hr("11:00") == "11:00 AM"

    def test_twelve_thirty_pm(self):
        """12:30 should be 12:30 PM."""
        assert _bot().convert_to_12hr("12:30") == "12:30 PM"

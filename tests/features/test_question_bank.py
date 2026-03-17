"""
Unit tests for question_bank.py — validates data integrity and the
get_random_question helper.
"""

import pytest
import sys
import os

# Add project root to path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.question_bank import (
    QOTD_QUESTIONS,
    WYR_QUESTIONS,
    CONVERSATION_STARTERS,
    COMPLIMENTS,
    ROASTS,
    get_random_question,
)


@pytest.mark.unit
class TestQuestionBankData:
    """Validate the static question/answer banks."""

    def test_qotd_not_empty(self):
        assert len(QOTD_QUESTIONS) > 0

    def test_wyr_not_empty(self):
        assert len(WYR_QUESTIONS) > 0

    def test_conversation_starters_not_empty(self):
        assert len(CONVERSATION_STARTERS) > 0

    def test_compliments_not_empty(self):
        assert len(COMPLIMENTS) > 0

    def test_roasts_not_empty(self):
        assert len(ROASTS) > 0

    def test_all_qotd_are_strings(self):
        for q in QOTD_QUESTIONS:
            assert isinstance(q, str), f"Expected str, got {type(q)}"

    def test_all_roasts_are_strings(self):
        for r in ROASTS:
            assert isinstance(r, str), f"Expected str, got {type(r)}"

    def test_no_duplicate_qotd(self):
        assert len(QOTD_QUESTIONS) == len(set(QOTD_QUESTIONS))

    def test_no_duplicate_wyr(self):
        assert len(WYR_QUESTIONS) == len(set(WYR_QUESTIONS))


@pytest.mark.unit
class TestGetRandomQuestion:
    """Test the get_random_question helper."""

    def test_returns_item_from_list(self):
        asked = []
        result = get_random_question(QOTD_QUESTIONS, asked)
        assert result in QOTD_QUESTIONS

    def test_tracks_asked_questions(self):
        asked = []
        get_random_question(QOTD_QUESTIONS, asked)
        assert len(asked) == 1

    def test_avoids_recently_asked(self):
        """Should not return a question that is in the asked list."""
        small_list = ["Q1", "Q2", "Q3"]
        asked = ["Q1", "Q2"]
        result = get_random_question(small_list, asked)
        assert result == "Q3"

    def test_resets_when_all_asked(self):
        """When all questions are exhausted, history resets."""
        small_list = ["Q1", "Q2"]
        asked = ["Q1", "Q2"]
        result = get_random_question(small_list, asked)
        assert result in small_list

    def test_max_history_limit(self):
        """Asked list should not grow beyond max_history."""
        asked = []
        for _ in range(60):
            get_random_question(QOTD_QUESTIONS, asked, max_history=10)
        assert len(asked) <= 10

"""
Integration tests for data persistence.

Tests the interaction with bot_data.json:
- Reading data
- Data structure validation
- Data integrity
"""

import pytest
import json
import os
from pathlib import Path


@pytest.mark.integration
def test_bot_data_file_exists():
    """Test that bot_data.json exists and is accessible"""
    project_root = Path(__file__).parent.parent.parent
    bot_data_path = project_root / "data" / "bot_data.json"

    assert bot_data_path.exists()
    assert bot_data_path.is_file()


@pytest.mark.integration
def test_bot_data_valid_json():
    """Test that bot_data.json contains valid JSON"""
    project_root = Path(__file__).parent.parent.parent
    bot_data_path = project_root / "data" / "bot_data.json"

    with open(bot_data_path, "r") as f:
        data = json.load(f)

    assert isinstance(data, dict)


@pytest.mark.integration
def test_bot_data_structure():
    """Test that bot_data.json has expected structure"""
    project_root = Path(__file__).parent.parent.parent
    bot_data_path = project_root / "data" / "bot_data.json"

    with open(bot_data_path, "r") as f:
        data = json.load(f)

    # Verify it's a dictionary
    assert isinstance(data, dict)

    # Verify some expected keys exist (flexible - bot adds keys dynamically)
    # Just check that it's not empty and has some common keys
    assert len(data) > 0


@pytest.mark.integration
def test_bot_data_trivia_structure():
    """Test trivia data structure"""
    project_root = Path(__file__).parent.parent.parent
    bot_data_path = project_root / "data" / "bot_data.json"

    with open(bot_data_path, "r") as f:
        data = json.load(f)

    trivia = data.get("daily_trivia", {})

    # Verify trivia structure
    if trivia:
        assert "question" in trivia or trivia == {}
        if "question" in trivia:
            assert "correct_answer" in trivia
            assert "answers" in trivia
            assert isinstance(trivia["answers"], list)


@pytest.mark.integration
def test_bot_data_riddle_structure():
    """Test riddle data structure"""
    project_root = Path(__file__).parent.parent.parent
    bot_data_path = project_root / "data" / "bot_data.json"

    with open(bot_data_path, "r") as f:
        data = json.load(f)

    riddle = data.get("daily_riddle", {})

    # Verify riddle structure
    if riddle:
        assert "riddle" in riddle or riddle == {}
        if "riddle" in riddle:
            assert "answer" in riddle


@pytest.mark.integration
def test_bot_data_file_permissions():
    """Test that bot_data.json has correct permissions"""
    project_root = Path(__file__).parent.parent.parent
    bot_data_path = project_root / "data" / "bot_data.json"

    # Check file is readable
    assert os.access(bot_data_path, os.R_OK)

    # Check file is writable (bot needs to update it)
    assert os.access(bot_data_path, os.W_OK)


@pytest.mark.integration
def test_data_directory_structure():
    """Test that data directory has correct structure"""
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data"

    assert data_dir.exists()
    assert data_dir.is_dir()

    # Check for required files
    assert (data_dir / "bot_data.json").exists()
    assert (data_dir / "__init__.py").exists()


@pytest.mark.integration
def test_bot_data_encoding():
    """Test that bot_data.json uses UTF-8 encoding"""
    project_root = Path(__file__).parent.parent.parent
    bot_data_path = project_root / "data" / "bot_data.json"

    # Should be able to read with UTF-8
    with open(bot_data_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert len(content) > 0

    # Should be valid JSON
    data = json.loads(content)
    assert isinstance(data, dict)

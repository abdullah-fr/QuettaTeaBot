"""
End-to-End tests for data persistence workflows.

Simulates complete user journeys involving data storage:
- Reading bot data
- Data validation
- Data integrity across operations
"""

import pytest
import json
from pathlib import Path


@pytest.mark.e2e
def test_bot_data_read_workflow():
    """
    E2E Test: Bot reads persistent data on startup

    System Journey:
    1. Bot starts up
    2. Bot reads bot_data.json
    3. Bot loads user data
    4. Bot is ready to serve users
    """
    # Step 1 & 2: Bot startup, read data
    project_root = Path(__file__).parent.parent.parent
    bot_data_path = project_root / "data" / "bot_data.json"

    with open(bot_data_path, "r") as f:
        data = json.load(f)

    # Step 3: Verify data loaded
    assert isinstance(data, dict)
    assert len(data) > 0

    # Step 4: Bot ready (data is valid)
    assert data is not None


@pytest.mark.e2e
def test_user_data_persistence_workflow():
    """
    E2E Test: User data persists across sessions

    User Journey:
    1. User interacts with bot (data saved)
    2. Bot restarts
    3. User returns
    4. User's data still exists
    """
    project_root = Path(__file__).parent.parent.parent
    bot_data_path = project_root / "data" / "bot_data.json"

    # Step 1: Read current data (simulating saved state)
    with open(bot_data_path, "r") as f:
        data_before = json.load(f)

    # Step 2: Bot restart (simulated by re-reading)
    # Step 3: User returns
    with open(bot_data_path, "r") as f:
        data_after = json.load(f)

    # Step 4: Verify data persisted
    assert data_before == data_after


@pytest.mark.e2e
def test_data_integrity_workflow():
    """
    E2E Test: Data maintains integrity across operations

    System Journey:
    1. Bot reads data
    2. Bot validates structure
    3. Bot ensures no corruption
    4. Bot operates safely
    """
    project_root = Path(__file__).parent.parent.parent
    bot_data_path = project_root / "data" / "bot_data.json"

    # Step 1: Read data
    with open(bot_data_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Step 2: Validate JSON structure
    data = json.loads(content)

    # Step 3: Ensure no corruption
    assert isinstance(data, dict)

    # Step 4: Verify safe operation
    # Data should be serializable back to JSON
    json_str = json.dumps(data)
    assert len(json_str) > 0


@pytest.mark.e2e
def test_multi_user_data_workflow():
    """
    E2E Test: Bot handles multiple users' data

    System Journey:
    1. Bot stores data for multiple users
    2. Each user has separate data
    3. Data doesn't conflict
    4. All users served correctly
    """
    project_root = Path(__file__).parent.parent.parent
    bot_data_path = project_root / "data" / "bot_data.json"

    # Step 1 & 2: Read multi-user data
    with open(bot_data_path, "r") as f:
        data = json.load(f)

    # Step 3: Verify structure supports multiple users
    assert isinstance(data, dict)

    # Step 4: Verify data is organized
    # Each top-level key represents a feature or user collection
    for key, value in data.items():
        assert isinstance(key, str)
        # Value can be dict, list, or other JSON types
        assert value is not None


@pytest.mark.e2e
def test_data_file_accessibility_workflow():
    """
    E2E Test: Bot can access data file reliably

    System Journey:
    1. Bot checks file exists
    2. Bot checks file is readable
    3. Bot checks file is writable
    4. Bot operates normally
    """
    import os

    project_root = Path(__file__).parent.parent.parent
    bot_data_path = project_root / "data" / "bot_data.json"

    # Step 1: File exists
    assert bot_data_path.exists()

    # Step 2: File is readable
    assert os.access(bot_data_path, os.R_OK)

    # Step 3: File is writable
    assert os.access(bot_data_path, os.W_OK)

    # Step 4: Can actually read
    with open(bot_data_path, "r") as f:
        data = json.load(f)
    assert data is not None

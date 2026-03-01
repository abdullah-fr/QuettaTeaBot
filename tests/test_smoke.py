"""
Smoke tests to verify basic project setup.

These tests ensure the project structure and imports work correctly.
"""

import os
import pytest
from tests.core.base_test import BaseTest


class TestProjectSetup(BaseTest):
    """Basic smoke tests for project setup."""

    def test_project_structure_exists(self):
        """Verify critical directories exist."""
        self.log("Testing project structure...")

        project_root = self.project_root()

        # Check critical directories
        assert os.path.exists(os.path.join(project_root, "src"))
        assert os.path.exists(os.path.join(project_root, "tests"))
        assert os.path.exists(os.path.join(project_root, "data"))
        assert os.path.exists(os.path.join(project_root, "docs"))

        self.log("✅ All critical directories exist")

    def test_source_files_exist(self):
        """Verify critical source files exist."""
        self.log("Testing source files...")

        project_root = self.project_root()
        src_dir = os.path.join(project_root, "src")

        # Check critical files
        assert os.path.exists(os.path.join(src_dir, "main_bot.py"))
        assert os.path.exists(os.path.join(src_dir, "ramadan_features.py"))
        assert os.path.exists(os.path.join(src_dir, "api_helpers.py"))
        assert os.path.exists(os.path.join(src_dir, "question_bank.py"))

        self.log("✅ All source files exist")

    def test_bot_data_json_exists(self):
        """Verify bot_data.json exists and is valid JSON."""
        self.log("Testing bot_data.json...")

        bot_data_path = self.bot_data_path()

        # Check file exists
        assert os.path.exists(bot_data_path), "bot_data.json should exist"

        # Check it's valid JSON
        data = self.read_bot_data()
        assert isinstance(data, dict), "bot_data.json should contain a dictionary"

        self.log(f"✅ bot_data.json is valid with {len(data)} top-level keys")

    def test_requirements_file_exists(self):
        """Verify requirements.txt exists and contains dependencies."""
        self.log("Testing requirements.txt...")

        project_root = self.project_root()
        req_file = os.path.join(project_root, "requirements.txt")

        assert os.path.exists(req_file), "requirements.txt should exist"

        with open(req_file, "r") as f:
            content = f.read()

        # Check for critical dependencies
        assert "discord.py" in content
        assert "pytest" in content
        assert "pytest-asyncio" in content

        self.log("✅ requirements.txt contains critical dependencies")

    def test_config_files_exist(self):
        """Verify configuration files exist."""
        self.log("Testing configuration files...")

        project_root = self.project_root()

        assert os.path.exists(os.path.join(project_root, "Procfile"))
        assert os.path.exists(os.path.join(project_root, "nixpacks.toml"))

        self.log("✅ Configuration files exist")

    def test_pytest_configuration(self):
        """Verify pytest.ini exists and is configured."""
        self.log("Testing pytest configuration...")

        project_root = self.project_root()
        pytest_ini = os.path.join(project_root, "pytest.ini")

        assert os.path.exists(pytest_ini), "pytest.ini should exist"

        with open(pytest_ini, "r") as f:
            content = f.read()

        # Check for key configurations
        assert "testpaths" in content
        assert "markers" in content

        self.log("✅ pytest.ini is configured")


class TestBaseTestClass:
    """Test the BaseTest class functionality."""

    def test_base_test_instantiation(self):
        """Test that BaseTest can be instantiated."""
        test_instance = BaseTest()
        assert test_instance is not None

    def test_base_test_logging(self):
        """Test logging functionality."""
        test_instance = BaseTest()
        test_instance.setup_method()

        test_instance.log("Test message")

        assert len(test_instance.logs) == 1
        assert "Test message" in test_instance.logs[0]

    def test_base_test_project_root(self):
        """Test project root detection."""
        test_instance = BaseTest()

        root = test_instance.project_root()

        assert root is not None
        assert os.path.exists(root)
        assert os.path.isdir(root)

    def test_base_test_assertions(self):
        """Test custom assertion methods."""
        test_instance = BaseTest()

        # Test assert_key_exists
        data = {"key1": "value1"}
        test_instance.assert_key_exists(data, "key1")

        # Test assert_not_empty
        test_instance.assert_not_empty("not empty")
        test_instance.assert_not_empty([1, 2, 3])
        test_instance.assert_not_empty({"key": "value"})


@pytest.mark.unit
def test_imports_work():
    """Verify that critical imports work without errors."""
    # This test just needs to run without import errors
    from tests.core.base_test import BaseTest

    assert BaseTest is not None

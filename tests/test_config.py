import importlib
import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parent.parent / "src"


def import_config_module():
    sys.path.insert(0, str(SRC_ROOT))
    try:
        if "config" in sys.modules:
            del sys.modules["config"]
        import config as config_module

        importlib.reload(config_module)
        return config_module
    finally:
        sys.path.pop(0)


def test_settings_loads_env(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "fake-discord-token")
    monkeypatch.setenv("API_NINJAS_KEY", "fake-api-key")
    monkeypatch.setenv("GROQ_API_KEY", "fake-groq-key")

    config_module = import_config_module()

    assert (
        config_module.settings.discord_token.get_secret_value() == "fake-discord-token"
    )
    assert config_module.settings.api_ninjas_key.get_secret_value() == "fake-api-key"
    assert config_module.settings.groq_api_key.get_secret_value() == "fake-groq-key"


def test_missing_discord_token_raises(monkeypatch):
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)

    config_module = import_config_module()
    settings = config_module.Settings(discord_token=None)
    with pytest.raises(ValueError, match="DISCORD_TOKEN is required"):
        settings.get_discord_token()


def test_log_level_normalization():
    config_module = import_config_module()
    settings = config_module.Settings(log_level="debug")

    assert settings.log_level == "DEBUG"


def test_secret_fields_are_wrapped_and_retrievable():
    config_module = import_config_module()
    settings = config_module.Settings(
        discord_token="secret-token",
        api_ninjas_key="api-key",
        groq_api_key="groq-key",
    )

    assert settings.discord_token.get_secret_value() == "secret-token"
    assert settings.api_ninjas_key.get_secret_value() == "api-key"
    assert settings.groq_api_key.get_secret_value() == "groq-key"


def test_default_paths_are_resolved_correctly():
    config_module = import_config_module()
    settings = config_module.Settings()

    assert settings.env_file.name == ".env"
    assert settings.bot_data_file.name == "bot_data.json"

from __future__ import annotations
from pathlib import Path
from typing import Optional

from pydantic import Field, SecretStr, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    discord_token: Optional[SecretStr] = None
    bot_data_file: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent
        / "data"
        / "bot_data.json"
    )
    api_ninjas_key: Optional[SecretStr] = None
    gemini_api_key_1: Optional[SecretStr] = None
    gemini_api_key_2: Optional[SecretStr] = None
    gemini_api_key_3: Optional[SecretStr] = None
    gemini_api_key_4: Optional[SecretStr] = None
    yt_dlp_cookies_file: Optional[str] = None
    yt_dlp_cookies_browser: Optional[str] = None
    yt_dlp_js_runtime: str = "node"
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    env_file: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent / ".env"
    )

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    def get_discord_token(self) -> str:
        if self.discord_token is None:
            raise ValueError("DISCORD_TOKEN is required")
        return self.discord_token.get_secret_value()

    @validator("log_level", pre=True)
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()


settings = Settings()

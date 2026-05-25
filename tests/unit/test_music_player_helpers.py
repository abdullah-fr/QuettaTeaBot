import os

import pytest

pytest.importorskip("discord")

from src.music_player import (
    MusicError,
    _base_ytdlp_options,
    _cookie_options_from_env,
    _first_entry,
    _js_runtime_options_from_env,
    _normalize_webpage_url,
    _parse_browser_cookie_spec,
    format_duration,
    is_probably_url,
    truncate_text,
)
from src import music_player


def test_format_duration_values():
    assert format_duration(None) == "Unknown"
    assert format_duration(0) == "Live"
    assert format_duration(30) == "0:30"
    assert format_duration(3601) == "1:00:01"


def test_is_probably_url_detects_valid_and_invalid_urls():
    assert is_probably_url("https://example.com/path") is True
    assert is_probably_url("http://example.com") is True
    assert is_probably_url("ftp://example.com") is False
    assert is_probably_url("not a url") is False


def test_truncate_text_short_string():
    assert truncate_text("Hello", 10) == "Hello"
    assert truncate_text("Hello world", 8) == "Hello..."


def test_parse_browser_cookie_spec_variants():
    assert _parse_browser_cookie_spec("brave") == ("brave", None, None, None)
    assert _parse_browser_cookie_spec("chrome:Default") == (
        "chrome",
        "Default",
        None,
        None,
    )
    assert _parse_browser_cookie_spec("firefox+keyring:Profile::container") == (
        "firefox",
        "Profile",
        "KEYRING",
        "container",
    )


def test_parse_browser_cookie_spec_raises_on_empty_browser():
    with pytest.raises(MusicError):
        _parse_browser_cookie_spec(":")


def test_cookie_options_from_env_falls_back_to_settings(monkeypatch):
    monkeypatch.setenv("YTDLP_COOKIES_FILE", "/tmp/env_cookies.txt")
    monkeypatch.setenv("YTDLP_COOKIES_BROWSER", "brave::")
    monkeypatch.setattr(music_player.settings, "yt_dlp_cookies_file", "./cookie.txt")
    monkeypatch.setattr(music_player.settings, "yt_dlp_cookies_browser", None)

    options = _cookie_options_from_env()

    assert options["cookiefile"].endswith("cookie.txt")
    assert options["cookiesfrombrowser"][0] == "brave"


def test_js_runtime_options_from_env_uses_env_when_settings_empty(monkeypatch):
    monkeypatch.delenv("YTDLP_JS_RUNTIME", raising=False)
    monkeypatch.delenv("YOUTUBE_JS_RUNTIME", raising=False)
    monkeypatch.setattr(music_player.settings, "yt_dlp_js_runtime", "node,coffee")

    options = _js_runtime_options_from_env()

    assert "js_runtimes" in options
    assert "node" in options["js_runtimes"]
    assert "coffee" in options["js_runtimes"]


def test_normalize_webpage_url_uses_fallback_fields():
    assert _normalize_webpage_url({"webpage_url": "https://x.com"}) == "https://x.com"
    assert _normalize_webpage_url({"original_url": "https://y.com"}) == "https://y.com"
    assert _normalize_webpage_url({"url": "https://z.com"}) == "https://z.com"
    assert _normalize_webpage_url({"id": "dQw4w9WgXcQ"}) == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_first_entry_returns_first_valid_entry():
    info = {"entries": [None, {"title": "x"}]}
    assert _first_entry(info) == {"title": "x"}


def test_first_entry_raises_when_all_entries_are_none():
    with pytest.raises(MusicError):
        _first_entry({"entries": [None, None]})


def test_first_entry_returns_info_when_entries_empty():
    info = {"title": "no-playlist", "entries": []}
    assert _first_entry(info) is info


def test_base_ytdlp_options_includes_defaults():
    options = _base_ytdlp_options()
    assert options["format"] == "bestaudio/best"
    assert options["noplaylist"] is True
    assert options["source_address"] == "0.0.0.0"

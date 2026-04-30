"""
Unit tests for the music player helpers.
"""

import pytest

from src.music_player import (
    GuildMusicState,
    MAX_QUEUE_SIZE,
    MusicError,
    Track,
    _cookie_options_from_env,
    _js_runtime_options_from_env,
    _parse_browser_cookie_spec,
    format_duration,
    is_probably_url,
    truncate_text,
)


@pytest.mark.unit
def test_format_duration_for_song_lengths():
    assert format_duration(None) == "Unknown"
    assert format_duration(0) == "Live"
    assert format_duration(65) == "1:05"
    assert format_duration(3661) == "1:01:01"


@pytest.mark.unit
def test_is_probably_url_accepts_only_http_links():
    assert is_probably_url("https://www.youtube.com/watch?v=test")
    assert is_probably_url("http://youtu.be/test")
    assert not is_probably_url("never gonna give you up")
    assert not is_probably_url("ftp://example.com/song")


@pytest.mark.unit
def test_truncate_text_preserves_short_strings():
    assert truncate_text("short title", 20) == "short title"
    assert truncate_text("this is a very long title", 12) == "this is a..."


@pytest.mark.unit
def test_music_state_enqueue_and_clear():
    state = GuildMusicState()
    track = Track(title="Song", webpage_url="https://youtu.be/test")

    position = state.enqueue(track)

    assert position == 1
    assert state.queue == [track]

    state.current = track
    state.clear()

    assert state.queue == []
    assert state.current is None


@pytest.mark.unit
def test_music_state_rejects_full_queue():
    state = GuildMusicState(
        queue=[
            Track(title=f"Song {index}", webpage_url=f"https://youtu.be/{index}")
            for index in range(MAX_QUEUE_SIZE)
        ]
    )

    with pytest.raises(MusicError):
        state.enqueue(Track(title="Extra", webpage_url="https://youtu.be/extra"))


@pytest.mark.unit
def test_parse_browser_cookie_spec():
    assert _parse_browser_cookie_spec("brave") == ("brave", None, None, None)
    assert _parse_browser_cookie_spec("chrome:Default") == (
        "chrome",
        "Default",
        None,
        None,
    )
    assert _parse_browser_cookie_spec("firefox:Profile::none") == (
        "firefox",
        "Profile",
        None,
        "none",
    )


@pytest.mark.unit
def test_cookie_options_from_env(monkeypatch):
    monkeypatch.setenv("YTDLP_COOKIES_BROWSER", "brave")
    monkeypatch.setenv("YTDLP_COOKIES_FILE", "~/cookies.txt")

    options = _cookie_options_from_env()

    assert options["cookiesfrombrowser"] == ("brave", None, None, None)
    assert options["cookiefile"].endswith("cookies.txt")


@pytest.mark.unit
def test_js_runtime_options_default_to_node(monkeypatch):
    monkeypatch.delenv("YTDLP_JS_RUNTIME", raising=False)
    monkeypatch.delenv("YOUTUBE_JS_RUNTIME", raising=False)

    assert _js_runtime_options_from_env() == {"js_runtimes": {"node": {}}}

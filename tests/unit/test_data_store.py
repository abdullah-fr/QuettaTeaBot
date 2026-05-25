import asyncio
import json
from pathlib import Path

import pytest

from src.data_store import JsonDataStore


def test_load_sync_creates_default_file(tmp_path: Path):
    target = tmp_path / "nested" / "bot_data.json"
    store = JsonDataStore(target)

    data = store.load_sync()

    assert target.exists()
    assert data == {"pet_system": {}, "vc_time": {}, "trivia_scores": {}}


def test_load_sync_recovers_from_corrupt_json(tmp_path: Path):
    target = tmp_path / "bot_data.json"
    target.write_text("not valid json {{{", encoding="utf-8")

    data = JsonDataStore(target).load_sync()

    assert data == {"pet_system": {}, "vc_time": {}, "trivia_scores": {}}


async def test_async_save_round_trips(tmp_path: Path):
    store = JsonDataStore(tmp_path / "bot_data.json")
    store.load_sync()

    payload = {
        "pet_system": {"123": {"name": "Mochi", "happiness": 50}},
        "vc_time": {"123": 600},
        "trivia_scores": {"123": 4},
    }
    await store.save(payload)

    on_disk = await store.load()
    assert on_disk == payload


async def test_concurrent_saves_are_serialized(tmp_path: Path):
    store = JsonDataStore(tmp_path / "bot_data.json")
    store.load_sync()

    async def writer(value: int):
        await store.save({"trivia_scores": {"u": value}})

    # Fire 10 writes concurrently; lock should serialize them and the file
    # should end in a valid (parseable) state regardless of interleaving.
    await asyncio.gather(*(writer(i) for i in range(10)))

    final = await store.load()
    assert final["trivia_scores"]["u"] in range(10)
    # File parses cleanly = atomic write worked.
    parsed = json.loads((tmp_path / "bot_data.json").read_text(encoding="utf-8"))
    assert "trivia_scores" in parsed


async def test_save_does_not_leave_tempfile(tmp_path: Path):
    store = JsonDataStore(tmp_path / "bot_data.json")
    await store.save({"trivia_scores": {"u": 1}})

    leftover_tmps = list(tmp_path.glob("bot_data.json.*.tmp"))
    assert leftover_tmps == []


def test_path_property_returns_path(tmp_path: Path):
    target = tmp_path / "bot_data.json"
    store = JsonDataStore(str(target))

    assert isinstance(store.path, Path)
    assert store.path == target


async def test_save_then_load_after_external_mutation(tmp_path: Path):
    target = tmp_path / "bot_data.json"
    store = JsonDataStore(target)
    await store.save({"pet_system": {}, "vc_time": {}, "trivia_scores": {"u": 7}})

    # External edit (simulating a manual change between bot operations).
    target.write_text(
        json.dumps({"pet_system": {}, "vc_time": {}, "trivia_scores": {"u": 99}}),
        encoding="utf-8",
    )

    fresh = await store.load()
    assert fresh["trivia_scores"]["u"] == 99


@pytest.mark.parametrize("payload", [{}, {"only": "one"}, {"a": [1, 2, 3], "b": None}])
async def test_save_accepts_arbitrary_json_compatible_payload(
    tmp_path: Path, payload: dict
):
    store = JsonDataStore(tmp_path / "bot_data.json")
    await store.save(payload)
    assert await store.load() == payload

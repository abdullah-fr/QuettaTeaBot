"""Async-safe JSON data store with atomic writes.

Wraps the bot's JSON persistence to:
- Serialize concurrent writes with an asyncio.Lock so overlapping event
  handlers can't interleave mid-write.
- Write to a temp file and os.replace into place so a crash during write
  cannot leave a half-written JSON file.
- Run file IO in a thread executor so the event loop isn't blocked.
"""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Any

_DEFAULT_PAYLOAD: dict[str, dict] = {
    "pet_system": {},
    "vc_time": {},
    "trivia_scores": {},
}


class JsonDataStore:
    def __init__(self, path: str | Path, default: dict | None = None):
        self._path = Path(path)
        self._lock = asyncio.Lock()
        self._default = default if default is not None else dict(_DEFAULT_PAYLOAD)

    @property
    def path(self) -> Path:
        return self._path

    def _ensure_file_sync(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text(
                json.dumps(self._default, indent=4) + "\n",
                encoding="utf-8",
            )

    def _read_sync(self) -> dict[str, Any]:
        self._ensure_file_sync()
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            self._path.write_text(
                json.dumps(self._default, indent=4) + "\n",
                encoding="utf-8",
            )
            return json.loads(self._path.read_text(encoding="utf-8"))

    def _write_sync(self, data: dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        # Atomic write: temp file in same dir, then os.replace.
        fd, tmp_path = tempfile.mkstemp(
            prefix=self._path.name + ".",
            suffix=".tmp",
            dir=str(self._path.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self._path)
        except Exception:
            # Best-effort cleanup of the temp file if replace failed.
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def load_sync(self) -> dict[str, Any]:
        """Synchronous load. Use at startup before the event loop runs."""
        return self._read_sync()

    async def load(self) -> dict[str, Any]:
        async with self._lock:
            return await asyncio.to_thread(self._read_sync)

    async def save(self, data: dict[str, Any]) -> None:
        async with self._lock:
            await asyncio.to_thread(self._write_sync, data)

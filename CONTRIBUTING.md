# Contributing to QuettaTeaBot

Thanks for helping out. This file covers how to set up a dev environment, run the test suite, lint your changes, and open a PR that passes CI on the first try.

## Development setup

You need Python 3.11+. (CI tests against 3.10, 3.11, and 3.12.)

```bash
git clone https://github.com/abdullah-fr/QuettaTeaBot.git
cd QuettaTeaBot
python -m venv .venv
```

Activate the venv:

| OS | Command |
| --- | --- |
| macOS / Linux | `source .venv/bin/activate` |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (cmd) | `.venv\Scripts\activate.bat` |

Install runtime and dev dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Copy `.env.example` to `.env` and fill in at least `DISCORD_TOKEN`. The bot will fail fast with a clear message if `DISCORD_TOKEN` is missing.

## Running the bot

```bash
# With music (needs ~1 GB RAM, ffmpeg installed)
python src/main_bot.py

# Without music (low-memory hosts)
python src/main_bot_no_music.py
```

## Running tests

```bash
# Fast: unit + smoke + features + integration (~1 min)
pytest tests/ --ignore=tests/performance -q

# Full suite including performance/load tests (slow)
pytest tests/ -q

# Just the new unit tests
pytest tests/unit/ -q

# With coverage on the typed modules
pytest tests/unit/ tests/test_config.py \
  --cov=src.config --cov=src.retry_utils --cov=src.logging_config \
  --cov=src.api_helpers --cov=src.data_store --cov-report=term-missing
```

On Windows you may see a `UnicodeEncodeError` from `tests/conftest.py` when the post-session report writes emoji to a `cp1252` stdout. Set `PYTHONIOENCODING=utf-8` for the session and it goes away. CI runs on Ubuntu so this only affects local Windows runs.

## Linting and formatting

CI gates on **black**, **flake8**, and **mypy** (mypy is scoped to the typed helper modules — `config`, `retry_utils`, `logging_config`, `api_helpers`, `data_store`).

```bash
black .                 # format
black --check .         # verify formatted (what CI runs)
flake8 src/ tests/      # lint
mypy --ignore-missing-imports src/config.py src/retry_utils.py \
     src/logging_config.py src/api_helpers.py src/data_store.py
```

Style rules in this repo:
- Black with default settings (line length 88).
- No bare `except:` — catch `Exception` (or the specific class) so `KeyboardInterrupt` and `SystemExit` still propagate.
- No unused imports or `f"..."` strings without placeholders — flake8 will fail.
- The `main_bot*.py` files use `from question_bank import *`; this is grandfathered for now and will go away when those files are split into cogs. Don't add new star imports.

## Project layout

```
src/
  api_helpers.py      # External API calls (Groq, OpenTDB, etc.) — routed through retry_async
  config.py           # pydantic-settings — single source of truth for env config
  data_store.py       # Async-safe JSON store with atomic writes (asyncio.Lock + os.replace)
  logging_config.py   # Structured JSON logging
  main_bot.py         # Entry point with music
  main_bot_no_music.py# Entry point without music (low-memory hosts)
  music_player.py     # yt-dlp + voice client wiring
  question_bank.py    # Static curated content (trivia/wyr/etc.)
  retry_utils.py      # retry_async helper with exponential backoff
tests/
  unit/               # Fast, isolated tests for individual modules
  features/           # Per-feature test files
  integration/        # Cross-module tests
  e2e/                # End-to-end workflow tests
  performance/        # Slow load/stress tests (skipped in fast CI runs)
```

## Commit messages

Use conventional-commit prefixes so the history is greppable:
- `feat:` — user-visible new functionality
- `fix:` — bug fix
- `refactor:` — code change with no behavior change
- `perf:` — performance improvement
- `test:` — adding or fixing tests
- `docs:` — docs only
- `style:` — formatting only (no logic changes)
- `chore:` — tooling, deps, CI

Keep the subject under ~70 chars; put detail in the body explaining *why* the change is needed, not what the diff already shows.

## Pull requests

1. Branch off `main`.
2. Make sure `pytest tests/ --ignore=tests/performance`, `black --check .`, `flake8 src/ tests/`, and the scoped `mypy` invocation above all pass locally.
3. Open the PR. The `PR Checks` workflow runs the same gates plus a coverage report on Python 3.11.
4. If a CI step you didn't touch fails, check the workflow logs — `tests/conftest.py` produces an HTML report at `reports/test_report.html` that's uploaded as a CI artifact.

## Quick reference

| Task | Command |
| --- | --- |
| Install dev deps | `pip install -r requirements-dev.txt` |
| Run fast tests | `pytest tests/ --ignore=tests/performance -q` |
| Format | `black .` |
| Lint | `flake8 src/ tests/` |
| Type-check | `mypy --ignore-missing-imports src/config.py src/retry_utils.py src/logging_config.py src/api_helpers.py src/data_store.py` |
| Run bot (no music) | `python src/main_bot_no_music.py` |

# QuettaTeaBot — Claude Reference Sheet

> Load this file at the start of any session to skip full codebase exploration.
> Last synced: 2026-05-26

---

## Project Identity

- **Name**: QuettaTeaBot
- **Purpose**: Feature-rich Discord bot for the "Quetta Tea Corner" community — a Pakistani/South Asian Discord server
- **Repo**: `github.com/abdullah-fr/QuettaTeaBot`
- **Language**: Python 3.11+ (async, discord.py 2.7.1)
- **Deployment**: Railway (auto-deploy from `main`), also supports Pterodactyl/FeatherPanel

---

## File Map (src/)

| File | Role |
|------|------|
| `src/main_bot.py` | **Main entry** — all slash commands, event handlers, AI chat, role system (~1844 lines) |
| `src/main_bot_no_music.py` | Lightweight variant — same as main but no music (for <100MB RAM hosts) |
| `src/config.py` | Pydantic `Settings` — reads `.env`, exposes `settings` singleton |
| `src/data_store.py` | `JsonDataStore` — async-safe, atomic writes, single JSON file persistence |
| `src/api_helpers.py` | All external HTTP — Groq AI, Open Trivia DB, API Ninjas, etc. with retry logic |
| `src/music_player.py` | `MusicController` + `Track`/`GuildMusicState` — yt-dlp + ffmpeg queue system |
| `src/retry_utils.py` | `retry_async()` — exponential backoff with jitter, `HttpStatusError`/`RetryError` |
| `src/logging_config.py` | `configure_logging()` + `get_logger()` — structured JSON output to stdout |
| `src/question_bank.py` | Static fallback lists: `COMPLIMENTS`, `ROASTS`, `QOTD_QUESTIONS`, `WYR_QUESTIONS`, `URDU_POETRY`, `PETS` |

---

## Architecture Patterns

- **Config**: `settings = Settings()` from `src/config.py` (pydantic-settings, reads `.env`)
- **Data persistence**: Single file `data/bot_data.json` with keys `pet_system`, `vc_time`, `trivia_scores`
  - Always call `await data_store.save(bot_data)` after mutating `bot_data`
- **API calls**: All go through `_fetch_json()` / `_fetch_text()` in `api_helpers.py` (2 retries, exponential backoff)
- **AI (Groq)**: `fetch_ai_chat_reply()` and `fetch_ai_summary()` — model `llama-3.1-8b-instant`
- **Music**: `yt-dlp` runs in `asyncio.to_thread()` to avoid blocking the event loop. `MusicController.get_state(guild_id)` gives per-guild state
- **Logging**: `get_logger(__name__)` everywhere, JSON structured, extra fields via `extra={}`
- **Import guard**: Every `src/` file has `try: from config import ... except ImportError: from .config import ...` for both direct run and package import

---

## Bot Commands (Slash)

### Music (`src/music_player.py`)
`/play`, `/search`, `/queue`, `/skip`, `/pause`, `/resume`, `/stop`, `/disconnect`, `/leave`, `/connect`

### Entertainment (`src/main_bot.py`)
`/trivia`, `/triviascores`, `/wyr`, `/riddle`, `/roast`, `/qotd`, `/compliment`, `/rekhta`, `/pomodoro`, `/adopt`

### Utilities
`/stats`, `/vctime`, `/tldr` (AI channel summary — uses Groq), `/purge` (bulk delete with filters)

### Admin/Debug
`/checkroles`, `/checkintents`, `/checkaudit`, `/welcome`, `/setuphobbies`

### Role Panels
`ColorRoleView` (37 colors, split across 3 Views of 25 each), `NotificationView` (VC/Chat/Game/Event pings), `HobbyRoleView` (Gaming/Art/Music/Reading)

---

## Key Discord Channel Names (hardcoded)

| Channel | Bot behavior |
|---------|-------------|
| `#intro` | Sticky welcome embed + auto-thread per intro |
| `#freedom-of-speech` | Auto-thread per confession (bot posts) |
| `#art-n-clicks` | Images only — deletes text, auto-threads images |
| `#foodie` | Food images only — deletes text, auto-threads |
| `#tollplaza` | Join/leave log embeds |
| `#general` | Verified-role welcome message, milestone announcements |
| `#self-roles` | Referenced in welcome messages |
| `#logs` | Message delete log + verified-member-left warning |

---

## Key Role Names (hardcoded)

- `"✔️Verified"` — triggers auto-welcome to #general
- `"Unverified"` — auto-assigned on join
- `"VC Ping"`, `"Chat Ping"`, `"Game Ping"`, `"Event Ping"` — notification toggles
- `"Gaming"`, `"Art"`, `"Music"`, `"Reading"` — hobby roles
- 37 color roles (see `COLOR_ROLES` dict in main_bot.py:57-94)

---

## AI Chat System (`maybe_send_ai_chat_reply` in main_bot.py:1289)

**Trigger conditions** (all must pass):
- Not a bot, has guild, in `TextChannel | VoiceChannel | Thread`
- Message > 3 chars, doesn't start with `/`
- Not a low-signal message (short, emoji-only, test words)
- Not containing serious keywords (death, hospital, suicide, etc.)
- Channel cooldown: 45s, user cooldown: 75s
- Not replying to same user twice in a row per channel
- Probability: 10% base (funny = 22%), doubled if 3+ messages of context

**Anti-repetition**: `_recent_bot_replies` deque (6 per channel) + `_is_too_similar_to_recent()`

**Persona**: Pakistani/South Asian Discord member, roman urdu + english mix, 3-8 words, lowercase, casual

---

## Environment Variables

| Var | Required | Notes |
|-----|----------|-------|
| `DISCORD_TOKEN` | Yes | Bot fails fast without it |
| `GROQ_API_KEY` | No | Enables AI chat + /tldr |
| `API_NINJAS_KEY` | No | Enables riddle API |
| `YTDLP_COOKIES_BROWSER` | No | e.g. `brave`, for YouTube auth |
| `YTDLP_COOKIES_FILE` | No | Path to cookies.txt |
| `YTDLP_JS_RUNTIME` | No | Default `node` |
| `BOT_DATA_FILE` | No | Default `data/bot_data.json` |

---

## Git Branches & Contributors

| Branch | Status | Author | Summary |
|--------|--------|--------|---------|
| `main` | Production | merged | Current live state |
| `origin/refactor/cleanup` | Merged (PR #12) | Abdullah Ali (`aali274297@gmail.com`) | Config centralization, pydantic settings, retry utils, async data store, structured logging, heartbeat, AI persona overhaul, unit test expansion, flake8/black formatting |
| `origin/dependabot/pip/*` | Open (3 PRs) | Dependabot | pynacl ≥1.6.2, pytz ≥2026.2, yt-dlp ≥2026.3.17 |

**Primary author**: Abdullah Shabbir (`abdullah.shabbir.1211@gmail.com`) — original bot, all core features  
**Infrastructure contributor**: Abdullah Ali (`aali274297@gmail.com`) — refactor/cleanup branch

---

## Testing

```bash
# Run all non-perf tests
pytest tests/ --ignore=tests/performance -q

# Lint
black --check .
flake8 src/ tests/

# Type-check (if using mypy)
mypy src/
```

**Test structure**:
- `tests/unit/` — isolated unit tests (api_helpers, data_store, logging, music, retry)
- `tests/integration/` — API + data integration
- `tests/e2e/` — end-to-end workflow tests
- `tests/features/` — feature-level tests (iftar, sehri, trivia, scheduler)
- `tests/performance/` — load/stress tests (excluded from normal CI run)
- `tests/conftest.py` — shared fixtures

---

## Deployment

- **Railway**: Auto-deploys from `main` push (CI tests run first via `deploy.yml`)
- **Pterodactyl/FeatherPanel**: Use `main_bot_no_music.py`, no ffmpeg needed
- `nixpacks.toml` for Railway build config
- `Procfile` for process management
- `runtime.txt` pins Python version

---

## Common Tasks & Where to Look

| Task | File(s) |
|------|---------|
| Add a new slash command | `src/main_bot.py` (follow existing pattern) |
| Add music command | `src/music_player.py` → `setup_music_commands()` |
| Change AI persona/behavior | `src/api_helpers.py` → `fetch_ai_chat_reply()` system prompt |
| Change persona reply behavior | `src/api_helpers.py` → `fetch_ai_persona_reply()` system prompt |
| Change AI trigger probability | `src/main_bot.py` → `maybe_send_ai_chat_reply()` |
| Tune persona activation threshold | `src/main_bot.py` → `_PROFILE_MIN_MESSAGES` (currently 50) |
| Tune profile save frequency | `src/main_bot.py` → `_PROFILE_SAVE_INTERVAL` (currently 70 msgs) |
| Add channel rule | `src/main_bot.py` → `on_message()` handler |
| Add a new API | `src/api_helpers.py` (use `_fetch_json()` helper) |
| Change bot settings | `src/config.py` → `Settings` class |
| View persistent data schema | `src/data_store.py` → `_DEFAULT_PAYLOAD` |
| View user profiles | `data/user_profiles.json` (auto-created, keyed by Discord user ID) |
| Add static content (jokes/roasts) | `src/question_bank.py` |

---

## Recommended VS Code Extensions

These reduce the need to re-explore the codebase in Claude context:

| Extension | ID | Why |
|-----------|-----|-----|
| **Pylance** | `ms-python.vscode-pylance` | Type inference, go-to-definition, inline errors — huge for navigating main_bot.py |
| **GitLens** | `eamodio.gitlens` | Inline blame, branch compare, commit history without needing Claude for git context |
| **Error Lens** | `usernamehw.errorlens` | Inline error display — diagnose issues without asking Claude |
| **Python** | `ms-python.python` | Core Python support |
| **Python Graph** (call graph) | `ededejr.call-graph` | Visualize call chains — see which functions call which without reading files |
| **Outline Map** | `saber2pr.outline-map` | Persistent file outline in sidebar — navigate 1844-line main_bot.py instantly |
| **Todo Tree** | `Gruntfuggly.todo-tree` | Scan all TODOs/FIXMEs across codebase in one view |
| **Coverage Gutters** | `ryanluker.vscode-coverage-gutters` | See test coverage inline — know what's tested without reading test files |
| **REST Client** | `humao.rest-client` | Test Groq/API Ninjas endpoints directly from VS Code |

**For call/dependency graphs** (the "graph extension" you mentioned):
- `ededejr.call-graph` — shows Python call hierarchy from any function
- Alternative: run `pyreverse -o png src/` (from pylint) to get UML class/dependency diagrams

---

## Commit Rules

- Never add `Co-Authored-By: Claude` to any commit message
- One-liner description: `type(scope): what changed — how it affects the bot`

---

## Key Invariants (don't break these)

1. `data_store.save(bot_data)` must be awaited after every mutation — it's the only persistence
2. Music commands use `asyncio.to_thread()` for yt-dlp — never call yt-dlp directly in async context
3. The `on_message` handler must always call `await bot.process_commands(message)` at the end
4. Persistent views (`ColorRoleView`, `NotificationView`, `HobbyRoleView`, `MusicPlayerView`) must be registered in `on_ready()` with `bot.add_view()` — otherwise buttons break on restart
5. The `try/except ImportError` import guard in every src file must be preserved
6. Never hardcode API keys — always read from `settings.*` (pydantic-settings)
7. AI chat: serious keyword list must stay — bot should never engage with grief/crisis topics
8. `_user_profiles_store` uses `default={}` — do not change to `_DEFAULT_PAYLOAD` or it will corrupt user_profiles.json
9. Profile saves are batched every 70 messages per user (`_PROFILE_SAVE_INTERVAL`) — don't call `_user_profiles_store.save()` on every message
10. Persona reply always falls back to generic reply if Groq returns empty — never skip the fallback

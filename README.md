# QuettaTeaBot 🍵

A feature-rich Discord bot built for the **Quetta Tea Corner ☕** community server. Handles moderation utilities, entertainment, channel automation, AI-powered chat replies, and city/role management.

> **Deployed bot name:** PingAtYourOwnRisk
> **Hosting:** Pterodactyl/FeatherPanel (no-music version)
> **AI:** Google Gemini 3.1 Flash-Lite with 4-key rotation

---

## Features

### 🤖 AI Chat Replies
- Randomly replies to conversations using **Gemini 3.1 Flash-Lite**
- Context-aware — reads up to 15 recent messages before replying
- Per-user persona profiles — learns each user's chat style over time
- Proactive dead chat revival — drops a casual message when chat goes quiet
- Serious topic detection — never replies during grief/condolence conversations
- Uses server custom emojis naturally
- **4-key Gemini rotation** — auto-switches keys on 429 rate limit
- Output safety guard — blocks threats, self-harm phrases, and protected-class slurs
- Bot self-mention stripping — cleans up `@BotName` from context before sending to AI

### 🛡️ Moderation
- `/purge` — bulk delete up to 100 messages with filters (all, text, images, voice, links) and message link anchor
- Auto-deletes non-image messages in `#art-n-clicks` and `#foodie` channels
- Notifies users with an auto-disappearing message when rules are broken

### 📋 Channel Automation
- **Auto threads** — creates discussion threads on every confession in `#freedom-of-speech`
- **Auto threads** — creates welcome threads on every intro in `#intro`
- **Auto threads** — creates discussion threads on every image post in `#art-n-clicks` and `#foodie`
- **Sticky intro message** — keeps the intro format pinned at the bottom of `#intro`

### 👋 Join/Leave Logs (`#tollplaza`)
- Compact embed on member join with: username, invited by, account age, member count
- Compact embed on member leave with: username, join date, roles, member count
- Tracks invite usage to show who invited each member

### 🎮 Entertainment
- `/trivia` — trivia questions with 2-minute timer and leaderboard
- `/riddle` — riddles with 5-minute timer
- `/wyr` — Would You Rather questions
- `/qotd` — Question of the Day
- `/roast` — friendly roasts
- `/compliment` — compliments
- `/rekhta` — random Urdu poetry
- `/pomodoro` — study timer (up to 60 minutes)

### 🎨 Role Management
- **37 color roles** via button panel (3 pages of 25)
- **Notification roles** — VC Ping, Chat Ping, Game Ping, Event Ping
- **Hobby roles** — Gaming, Art, Music, Reading
- **17 city roles** — Karachite, Lahori, Faisalabadi, Peshawari, Multani, Islamabadi/Pindi, Quettaite, Gujranwala, Hyderabadi, Sialkoti, Bahawalpuri, Sukkuri, Abbottabadi, Gujrati, Jhelumi, Elsewhere 🇵🇰, International

### 📊 Utilities
- `/stats` — server statistics
- `/vctime` — voice chat time tracker per user per server
- `/tldr` — AI-powered channel summary (last 50–500 messages)
- `/adopt` — virtual pet system

---

## Two Bot Versions

| Version | File | Use Case |
|---|---|---|
| Full (with music) | `src/main_bot.py` | Local / high-RAM hosting |
| No music | `src/main_bot_no_music.py` | Pterodactyl / low-RAM hosting |

> Music requires ffmpeg, libopus, and ~1GB RAM. The no-music version runs under 100MB.

---

## Setup

### Requirements
- Python 3.11+
- ffmpeg (only for music version)

### Installation

```bash
git clone https://github.com/abdullah-fr/QuettaTeaBot.git
cd QuettaTeaBot
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
DISCORD_TOKEN=your_bot_token

# Gemini AI — get free keys at aistudio.google.com
# Use keys from different Google accounts for higher rate limits
GEMINI_API_KEY_1=your_key_1
GEMINI_API_KEY_2=your_key_2
GEMINI_API_KEY_3=your_key_3
GEMINI_API_KEY_4=your_key_4

API_NINJAS_KEY=your_key   # optional, for riddles
```

### Running

```bash
# Without music (recommended for hosted deployments)
python src/main_bot_no_music.py

# With music (needs ffmpeg + ~1GB RAM)
python src/main_bot.py
```

---

## Deployment (Pterodactyl / FeatherPanel)

Set the startup command to:

```bash
if [[ -d .git ]] && [[ "${AUTO_UPDATE}" == "1" ]]; then git pull; fi; pip install -U -r requirements.txt --user; python src/main_bot_no_music.py
```

Set these environment variables in the panel:
- `DISCORD_TOKEN`
- `GEMINI_API_KEY_1` through `GEMINI_API_KEY_4`
- `API_NINJAS_KEY` (optional)

---

## Development

```bash
pip install -r requirements-dev.txt
pytest tests/ --ignore=tests/performance -q
black --check .
flake8 src/ tests/
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

## Bot Permissions Required

- Read/Send Messages
- Manage Messages
- Manage Threads
- Manage Roles
- Add Reactions
- Embed Links
- Connect & Speak (music version only)
- View Audit Log (invite tracking)
- Manage Server (invite tracking)

---

## License

MIT

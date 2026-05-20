# Quetta Tea Bot

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![Deploy](https://github.com/abdullah-fr/QuettaTeaBot/workflows/Deploy%20to%20Production/badge.svg)
![License](https://img.shields.io/badge/license-Private-red)

A feature-rich Discord bot built for community engagement — games, music, Ramadan tools, role management, and more.

</div>

---

## Features

### 🎮 Games & Entertainment
- **Trivia** — unlimited questions pulled from an API, with a global leaderboard (`/trivia`, `/triviascores`)
- **Riddles** — 5-minute timer, first correct answer wins (`/riddle`)
- **Would You Rather** — reaction-based polls with fresh questions every time (`/wyr`)
- **Question of the Day** — daily conversation prompt (`/qotd`)
- **Roast & Compliment** — friendly roasts and compliments, optionally targeting a member (`/roast`, `/compliment`)
- **Urdu Poetry** — random Urdu/Rekhta poetry (`/rekhta`)

### 🎵 Music
Stream audio from YouTube directly into voice channels.

| Command | Description |
|---------|-------------|
| `/play <song>` | Play by YouTube link or search text (with autocomplete) |
| `/search <song>` | Search YouTube and pick from a dropdown |
| `/queue` | View the current queue |
| `/skip` | Skip the current track |
| `/pause` / `/resume` | Pause or resume playback |
| `/stop` | Stop playback and clear the queue |
| `/connect` / `/disconnect` | Join or leave your voice channel |

The Now Playing message includes inline ⏸ Pause, ⏭ Skip, and ⏹ Stop buttons.

> **YouTube sign-in issues?** Add `YTDLP_COOKIES_BROWSER=brave` (or your browser) to `.env` for local use, or `YTDLP_COOKIES_FILE=/path/to/cookies.txt` for a hosted bot.

### 🌙 Ramadan Features
Prayer times and reminders for 8 Pakistani cities (Islamabad, Lahore, Karachi, Faisalabad, Rawalpindi, Multan, Peshawar, Quetta).

| Command | Description |
|---------|-------------|
| `/ramadan [city]` | Today's Sehri/Iftar times with live Iftar countdown |
| `/iftar` | Countdown to Iftar (Maghrib) |
| `/hadith` | Random hadith about Ramadan from Sahih Bukhari |
| `/ayat` | Random Ramadan-related Quranic verse |

**Automated reminders** (no command needed):
- Sehri reminder 15 minutes before Fajr
- Iftar announcement at Maghrib time with the Iftar dua
- Daily Hadith posted at 8:00 PM PKT
- Daily Ayat posted at 9:00 AM PKT

### 👥 Social & Engagement
- **Daily streaks and rewards** — track consecutive activity
- **Voice channel time tracking** — per-user, per-server (`/vctime`)
- **Pet system** — adopt and care for a virtual pet (`/adopt`)
- **Pomodoro timer** — study timer up to 60 minutes (`/pomodoro`)
- **AI channel summary** — summarize the last 50–500 messages with Gemini (`/tldr`)

### 🎨 Role Management
- **Color roles** — 36 color options via interactive buttons (`/setupcolors`)
- **Hobby roles** — Gaming, Art, Music, Reading via buttons (`/setuphobbies`)
- **Notification roles** — VC Pings, Chat Pings, Game Pings, Event Pings

### 🛠️ Utility & Admin
- **Server stats** — member count, online count, channel counts (`/stats`)
- **Purge** — bulk delete messages with filters (text, images, links, voice messages) and message-link anchor support (`/purge`)

---

## Setup

### Prerequisites

- Python 3.10, 3.11, or 3.12
- [FFmpeg](https://ffmpeg.org/download.html) — required for music playback
- A Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications)

### Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/abdullah-fr/QuettaTeaBot.git
   cd QuettaTeaBot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and fill in your values (see [Environment Variables](#environment-variables) below).

5. **Run the bot**
   ```bash
   cd src && python main_bot.py
   ```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_TOKEN` | ✅ Yes | Your bot token from the Discord Developer Portal |
| `GROQ_API_KEY` | Optional | Enables AI-powered `/tldr` summaries ([get a free key](https://console.groq.com/keys)) |
| `API_NINJAS_KEY` | Optional | Enables riddle questions from API Ninjas ([get a free key](https://api-ninjas.com/)) |
| `BOT_DATA_FILE` | Optional | Custom path for persistent data (defaults to `data/bot_data.json`) |
| `YTDLP_COOKIES_BROWSER` | Optional | Browser to pull YouTube cookies from (e.g. `brave`, `chrome`) |
| `YTDLP_COOKIES_FILE` | Optional | Path to a cookies.txt file for YouTube auth on hosted bots |
| `YTDLP_JS_RUNTIME` | Optional | JavaScript runtime for YouTube challenge solving (defaults to `node`) |

---

## Project Structure

```
QuettaTeaBot/
├── src/
│   ├── main_bot.py          # Bot entry point, commands, and event handlers
│   ├── music_player.py      # YouTube music streaming and queue management
│   ├── ramadan_features.py  # Prayer times, countdowns, and automated reminders
│   ├── api_helpers.py       # External API integrations (trivia, jokes, AI, etc.)
│   └── question_bank.py     # Static content (poetry, fallback questions, etc.)
├── data/
│   └── bot_data.json        # Persistent storage (scores, VC time, pets, etc.)
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
├── Procfile                 # Railway deployment config
└── nixpacks.toml            # Nixpacks build config
```

---

## Deployment

The bot is deployed on [Wispbyte](https://wispbyte.com) with automatic deploys triggered on pushes to `main`. The deploy pipeline runs the full test suite before deploying — a failing test blocks the deploy.

For Railway or similar platforms, the `Procfile` and `nixpacks.toml` are already configured.

---

## Contributing

1. Fork the repo and create a branch from `main`
2. Make your changes and run the tests: `pytest tests/ -v`
3. Open a pull request — the PR template will guide you through the checklist

---

## License

Private project maintained by [@abdullah-fr](https://github.com/abdullah-fr).

# QuettaTeaBot 🍵

A feature-rich Discord bot built for the **Quetta Tea Corner** community server. Handles moderation utilities, entertainment, music playback, channel automation, and AI-powered chat replies.

---

## Features

### 🎵 Music
- `/play` — play any song by name or YouTube link with autocomplete
- `/search` — search YouTube and pick from a dropdown
- `/queue` — view the current queue
- `/skip`, `/pause`, `/resume`, `/stop`, `/disconnect`
- Now Playing card with ⏸ Pause, ⏭ Skip, ⏹ Stop buttons

### 🤖 AI Chat Replies
- Randomly replies to conversations using Groq (llama-3.1-8b-instant)
- Context-aware — reads recent chat history before replying
- Vibe detection — higher chance during funny/chaotic moments
- Serious topic detection — never replies during sensitive conversations
- Per-channel and per-user cooldowns to avoid spam
- Uses server custom emojis naturally

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
- `/pomodoro` — study timer

### 🎨 Role Management
- 37 color roles via button panel
- Notification roles (VC Ping, Chat Ping, Game Ping, Event Ping)
- Hobby roles (Gaming, Art, Music, Reading)

### 📊 Utilities
- `/stats` — server statistics
- `/vctime` — voice chat time tracker per user per server
- `/tldr` — AI-powered channel summary (last 50–500 messages)
- `/adopt` — virtual pet system

---

## Setup

### Requirements
- Python 3.11+
- ffmpeg (for music)

### Installation

```bash
git clone https://github.com/abdullah-fr/QuettaTeaBot.git
cd QuettaTeaBot
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
DISCORD_TOKEN=your_bot_token
GROQ_API_KEY=your_groq_key        # free at console.groq.com
API_NINJAS_KEY=your_key           # optional, for riddles
```

### Running

```bash
# With music
.venv/bin/python src/main_bot.py

# Without music (for low-memory hosting)
.venv/bin/python src/main_bot_no_music.py
```

---

## Deployment

The bot includes a `nixpacks.toml` for platforms like Railway or Wispbyte.

For Pterodactyl/FeatherPanel, use the Python Generic egg with:
- **APP PY FILE**: `src/main_bot_no_music.py`
- **REQUIREMENTS FILE**: `requirements.txt`
- **USER UPLOADED FILES**: `1`

> Music requires at least 1GB RAM. The no-music version runs comfortably under 100MB.

---

## Bot Permissions Required

- Read/Send Messages
- Manage Messages
- Manage Threads
- Add Reactions
- Embed Links
- Connect & Speak (for music)
- View Audit Log (for invite tracking)
- Manage Server (for invite tracking)

---

## License

MIT

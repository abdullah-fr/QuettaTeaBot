# Quetta Tea Bot

Complete Discord bot with color roles, automated features, and games.

## Files:
- `main_bot.py` - Main bot file (run this)
- `question_bank.py` - Questions and content
- `api_helpers.py` - API integrations
- `.env` - Discord token (keep secret)
- `requirements.txt` - Dependencies
- `Procfile` - Railway deployment
- `nixpacks.toml` - Build configuration

## Features:
- 60 Color Roles with buttons
- Notification role toggles
- Sticky intro message
- Auto-assign Unverified role
- Daily Trivia (tracks answers, reveals after 2 min)
- Daily Would You Rather
- Daily Riddle (5 min timer, first correct wins)
- Daily QOTD
- Daily Compliment
- Auto conversation starter
- Guess the Song (Pakistani/Indian/English)
- Pet system
- Inventory system
- Daily streaks
- VC time tracking
- Message delete logs
- And more!

## Run Locally:
```bash
python main_bot.py
```

## Deploy to Railway:
1. Push to GitHub
2. Connect Railway to repo
3. Add DISCORD_TOKEN environment variable
4. Deploy automatically

## Environment Variables:
- `DISCORD_TOKEN` - Your Discord bot token

That's it! The bot handles everything automatically.

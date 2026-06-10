# Bot File Rules

## Active deployed bot
`src/main_bot.py` — this is the **no-music version**, deployed on Pterodactyl/FeatherPanel.

## Music version
`main_bot_with_music.py` — at the **project root** (not inside src/). Includes music player and TTS/voice features.

## Rules
- **All code changes go to `src/main_bot.py` only** unless the user explicitly says to update the music version.
- Do NOT automatically sync changes to `main_bot_with_music.py`.
- Only update `main_bot_with_music.py` when the user explicitly asks.
- The startup command on the panel is: `python src/main_bot.py`

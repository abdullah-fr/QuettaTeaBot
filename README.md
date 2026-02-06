# Quetta Tea Corner Bot

Discord bot for Quetta Tea Corner server.

## Features
- Color role selection
- Notification preferences
- Sticky intro message
- Auto-assign Unverified role

## Hosting on Railway

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select this repository
5. Railway will automatically detect and deploy the bot
6. Bot will run 24/7!

## Hosting on Render

1. Go to [render.com](https://render.com)
2. Sign up
3. Click "New" → "Background Worker"
4. Connect your GitHub repo
5. Set start command: `python main_bot.py`
6. Deploy!

## Local Testing

```bash
pip install -r requirements.txt
python main_bot.py
```

## Environment Variables

If you want to hide your token (recommended for GitHub):
- Create a `.env` file
- Add: `DISCORD_TOKEN=your_token_here`
- Update main_bot.py to use `os.getenv('DISCORD_TOKEN')`

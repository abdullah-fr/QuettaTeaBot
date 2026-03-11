# 🚀 LemonHost Deployment Guide with GitHub Auto-Deploy

This guide will help you deploy your Discord bot to LemonHost with automatic deployment from GitHub.

## 📋 Prerequisites

- GitHub account with your bot repository
- Discord bot token
- LemonHost account (free, no credit card required)

## 🔧 Step 1: Sign Up for LemonHost

1. Go to [https://lemonhost.me/](https://lemonhost.me/)
2. Click "Get Started Free"
3. Join their Discord server (usually required for account creation)
4. Follow their signup process

## 📦 Step 2: Create a New Bot Server on LemonHost

1. Log into your LemonHost dashboard
2. Click "Create Server" or "New Bot"
3. Select "Python" as your bot type
4. Choose "GitHub" as deployment method
5. Name your server (e.g., "QuettaTeaBot")

## 🔗 Step 3: Connect Your GitHub Repository

### Option A: Direct GitHub Integration (Recommended)

1. In LemonHost dashboard, select "GitHub Integration"
2. Authorize LemonHost to access your GitHub account
3. Select repository: `abdullah-fr/QuettaTeaBot`
4. Select branch: `main` (or your default branch)
5. Set auto-deploy: **Enabled** ✅

### Option B: Manual GitHub Webhook Setup

If LemonHost doesn't have direct GitHub integration:

1. **Get Webhook URL from LemonHost:**
   - In your bot's settings, find "Webhook URL" or "Deploy URL"
   - Copy this URL (e.g., `https://deploy.lemonhost.me/webhook/your-bot-id`)

2. **Add Webhook to GitHub:**
   - Go to your GitHub repo: https://github.com/abdullah-fr/QuettaTeaBot
   - Click "Settings" → "Webhooks" → "Add webhook"
   - **Payload URL:** Paste the LemonHost webhook URL
   - **Content type:** `application/json`
   - **Secret:** (if LemonHost provides one, enter it here)
   - **Which events:** Select "Just the push event"
   - **Active:** ✅ Check this box
   - Click "Add webhook"

## 🔐 Step 4: Configure Environment Variables

In LemonHost dashboard, add these environment variables:

```
DISCORD_TOKEN=your_discord_bot_token_here
```

**Important:** Never commit your `.env` file to GitHub! It's already in `.gitignore`.

## ⚙️ Step 5: Configure Startup Command

In LemonHost bot settings, set the startup command to one of these:

**Option 1 (using start.sh):**
```bash
bash start.sh
```

**Option 2 (using Procfile):**
```bash
cd src && python main_bot.py
```

**Option 3 (direct command):**
```bash
python src/main_bot.py
```

## 📁 Step 6: Verify Project Structure

Your project should have these files (already present):

```
QuettaTeaBot/
├── src/
│   ├── main_bot.py          # Main bot file
│   ├── ramadan_features.py
│   ├── api_helpers.py
│   └── question_bank.py
├── data/
│   └── bot_data.json        # Persistent data
├── requirements.txt         # Python dependencies
├── Procfile                 # Deployment config
├── runtime.txt              # Python version
├── start.sh                 # Startup script
├── .env                     # Local env (NOT in git)
└── .gitignore              # Excludes .env
```

## 🚀 Step 7: Deploy Your Bot

### First Deployment:

1. In LemonHost dashboard, click "Deploy" or "Start Bot"
2. LemonHost will:
   - Clone your GitHub repository
   - Install dependencies from `requirements.txt`
   - Set up environment variables
   - Start your bot using the startup command

3. Monitor the console logs for any errors
4. Check if bot comes online in Discord

### Automatic Deployments:

Once set up, every time you push to GitHub:

```bash
git add .
git commit -m "Update bot features"
git push origin main
```

LemonHost will automatically:
1. Detect the push via webhook
2. Pull the latest code
3. Restart the bot with new changes
4. Your bot updates in ~30 seconds! 🎉

## 🔍 Step 8: Verify Auto-Deploy is Working

Test the auto-deployment:

1. Make a small change to your bot (e.g., add a comment)
2. Commit and push:
   ```bash
   git add .
   git commit -m "Test auto-deploy"
   git push origin main
   ```
3. Watch LemonHost console logs
4. You should see: "Deployment triggered by GitHub webhook"
5. Bot should restart automatically

## 📊 Monitoring Your Bot

### LemonHost Dashboard:
- View real-time console logs
- Check CPU/RAM usage (1GB RAM available)
- Monitor uptime (99.9% guaranteed)
- Restart bot manually if needed

### Discord:
- Check if bot is online
- Test commands: `!help`, `!trivia`, `!daily`

## 🐛 Troubleshooting

### Bot Won't Start:

1. **Check logs in LemonHost console**
2. Common issues:
   - Missing `DISCORD_TOKEN` environment variable
   - Wrong startup command
   - Missing dependencies in `requirements.txt`

### Auto-Deploy Not Working:

1. **Verify webhook in GitHub:**
   - Go to Settings → Webhooks
   - Check "Recent Deliveries"
   - Should show successful deliveries (green checkmark)

2. **Check LemonHost webhook URL:**
   - Make sure it matches exactly
   - No extra spaces or characters

3. **Test webhook manually:**
   - In GitHub webhook settings, click "Redeliver"

### Bot Crashes:

1. Check console logs for error messages
2. Common fixes:
   - Ensure `data/bot_data.json` exists
   - Check API rate limits
   - Verify all imports are in `requirements.txt`

## 🔄 Making Updates

### To update your bot:

1. **Edit code locally**
2. **Test locally:**
   ```bash
   python src/main_bot.py
   ```
3. **Commit changes:**
   ```bash
   git add .
   git commit -m "Add new feature"
   ```
4. **Push to GitHub:**
   ```bash
   git push origin main
   ```
5. **LemonHost auto-deploys** (30 seconds)
6. **Done!** ✅

## 📝 Important Notes

### Data Persistence:
- `data/bot_data.json` stores user data
- LemonHost should persist this file between restarts
- Consider backing up important data periodically

### Free Tier Limits:
- 1GB RAM (plenty for Discord bots)
- 2GB Storage
- 3 bot servers per user
- 99.9% uptime
- No bandwidth limits

### Best Practices:
- Always test locally before pushing
- Use meaningful commit messages
- Monitor logs after deployment
- Keep dependencies updated
- Never commit `.env` file

## 🎉 Success Checklist

- ✅ LemonHost account created
- ✅ Bot server created on LemonHost
- ✅ GitHub repository connected
- ✅ Webhook configured (if needed)
- ✅ Environment variables set
- ✅ Bot deployed and online
- ✅ Auto-deploy tested and working
- ✅ Commands working in Discord

## 🆘 Need Help?

1. **LemonHost Support:**
   - Join their Discord server
   - Open a support ticket
   - 24/7 support available

2. **GitHub Issues:**
   - Check webhook delivery status
   - Verify repository permissions

3. **Bot Issues:**
   - Check console logs
   - Test commands in Discord
   - Review error messages

## 🔗 Useful Links

- LemonHost: https://lemonhost.me/
- Your GitHub Repo: https://github.com/abdullah-fr/QuettaTeaBot
- Discord Developer Portal: https://discord.com/developers/applications

---

**Deployment Status:** Ready to deploy! 🚀

Follow the steps above and your bot will be live with automatic GitHub deployments in minutes!

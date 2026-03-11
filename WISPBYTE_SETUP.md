# 🚀 Wispbyte Deployment Guide - Discord Bot

Complete guide to deploy your QuettaTeaBot on Wispbyte with GitHub auto-deploy.

## 📋 What is Wispbyte?

- Free Discord bot hosting
- 99.9% uptime guarantee
- High-performance infrastructure
- No credit card required
- Support for Python bots

## 🔧 Step 1: Create Wispbyte Account

1. Go to **https://wispbyte.com/**
2. Click "Sign Up" or "Get Started"
3. Fill in your details:
   - Email address
   - Username
   - Strong password
4. Verify your email address
5. Complete profile setup
6. **Enable two-factor authentication** (recommended)

## 🎮 Step 2: Create New Server

1. **Log into Client Area**
   - Go to https://wispbyte.com/client
   - Navigate to dashboard

2. **Click "Create New Server"**

3. **Choose Server Type:**
   - Select **"Discord Bots"**
   - Or select **"Python"** if Discord Bots isn't available

4. **Select Plan:**
   - Choose **Free Plan** (if available)
   - Check available resources

5. **Configure Server Settings:**
   ```
   Server Name: QuettaTeaBot
   Description: Custom Discord bot for server management
   Server Type: Python
   Python Version: 3.11 or 3.12
   ```

6. **Click "Create Server"**

## 📁 Step 3: Upload Your Bot Files

### Option A: GitHub Integration (Recommended)

If Wispbyte supports GitHub integration:

1. In server settings, look for **"GitHub"** or **"Git"** tab
2. Click "Connect GitHub"
3. Authorize Wispbyte
4. Select repository: `abdullah-fr/QuettaTeaBot`
5. Select branch: `main`
6. Enable **Auto-Deploy** ✅
7. Save settings

### Option B: Manual File Upload

If no GitHub integration:

1. **Download your repo as ZIP:**
   ```bash
   # On your local machine
   cd ~/Desktop/QuettaTeaBot
   git archive --format=zip --output=QuettaTeaBot.zip HEAD
   ```

2. **Upload via Wispbyte File Manager:**
   - Go to server dashboard
   - Click "File Manager"
   - Upload `QuettaTeaBot.zip`
   - Extract the ZIP file
   - Delete the ZIP after extraction

### Option C: Git Clone (If Terminal Access Available)

If Wispbyte provides terminal/console access:

```bash
git clone https://github.com/abdullah-fr/QuettaTeaBot.git
cd QuettaTeaBot
```

## 🔐 Step 4: Set Environment Variables

1. **Go to Server Settings**
2. **Find "Environment Variables" or "Configuration" tab**
3. **Add variable:**
   ```
   Name: DISCORD_TOKEN
   Value: your_actual_discord_bot_token_here
   ```
4. **Save changes**

## ⚙️ Step 5: Configure Startup Command

1. **Go to "Startup" or "Configuration" section**
2. **Set startup command:**
   ```bash
   cd src && python main_bot.py
   ```

   **Alternative commands if above doesn't work:**
   ```bash
   python src/main_bot.py
   ```
   or
   ```bash
   bash start.sh
   ```

3. **Save startup configuration**

## 📦 Step 6: Install Dependencies

Wispbyte should automatically install from `requirements.txt`, but if not:

1. **Access server console/terminal**
2. **Run:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Step 7: Start Your Bot

1. **Go to server dashboard**
2. **Click "Start" button**
3. **Monitor console logs** for any errors
4. **Check Discord** - your bot should come online!

## 🔄 Step 8: Set Up Auto-Deploy (If Not Done in Step 3)

### If Wispbyte Provides Webhook URL:

1. **Get webhook URL from Wispbyte:**
   - Look in server settings for "Deploy Webhook" or "Webhook URL"
   - Copy the URL (e.g., `https://deploy.wispbyte.com/webhook/your-server-id`)

2. **Add webhook to GitHub:**
   - Go to: https://github.com/abdullah-fr/QuettaTeaBot/settings/hooks
   - Click "Add webhook"
   - **Payload URL:** Paste Wispbyte webhook URL
   - **Content type:** `application/json`
   - **Secret:** (leave empty unless Wispbyte provides one)
   - **Events:** Select "Just the push event"
   - **Active:** ✅ Check this
   - Click "Add webhook"

3. **Test auto-deploy:**
   ```bash
   # Make a small change
   echo "# Test" >> README.md
   git add README.md
   git commit -m "Test auto-deploy"
   git push origin main

   # Watch Wispbyte console - should auto-restart!
   ```

## 📊 Step 9: Monitor Your Bot

### Wispbyte Dashboard:
- **Console Logs:** Real-time output
- **Resource Usage:** CPU, RAM, Disk
- **Uptime:** Check bot availability
- **Restart:** Manual restart if needed

### Discord:
- Check bot online status
- Test commands: `!help`, `!trivia`, `!daily`

## 🐛 Troubleshooting

### Bot Won't Start

**Check console logs for errors:**

1. **Missing DISCORD_TOKEN:**
   - Error: `discord.errors.LoginFailure`
   - Fix: Add `DISCORD_TOKEN` in environment variables

2. **Wrong startup command:**
   - Error: `No such file or directory`
   - Fix: Use `cd src && python main_bot.py`

3. **Missing dependencies:**
   - Error: `ModuleNotFoundError`
   - Fix: Run `pip install -r requirements.txt`

4. **File structure issues:**
   - Make sure all files uploaded correctly
   - Check that `src/main_bot.py` exists

### Auto-Deploy Not Working

1. **Check GitHub webhook:**
   - Go to Settings → Webhooks
   - Check "Recent Deliveries"
   - Should show green checkmarks

2. **Verify webhook URL:**
   - Make sure it matches Wispbyte's URL exactly
   - No extra spaces or characters

3. **Test manually:**
   - In GitHub webhook settings, click "Redeliver"
   - Check Wispbyte console for deployment trigger

### Bot Crashes

1. **Check console logs** for error messages
2. **Common issues:**
   - API rate limits (wait and retry)
   - Missing `data/bot_data.json` (should auto-create)
   - Network connectivity issues

## 🔄 Making Updates

Once auto-deploy is set up:

```bash
# 1. Edit your code locally
# 2. Test locally
python src/main_bot.py

# 3. Commit changes
git add .
git commit -m "Add new feature"

# 4. Push to GitHub
git push origin main

# 5. Wispbyte auto-deploys (30-60 seconds)
# 6. Done! ✅
```

## 📝 Important Notes

### Data Persistence
- `data/bot_data.json` stores user data
- Wispbyte should persist files between restarts
- Consider periodic backups

### Free Tier Limits
- Check Wispbyte's free tier specifications
- Monitor resource usage
- Upgrade if needed

### Best Practices
- Always test locally before pushing
- Use meaningful commit messages
- Monitor logs after deployment
- Keep dependencies updated
- Never commit `.env` file (already in `.gitignore`)

## ✅ Success Checklist

- ✅ Wispbyte account created
- ✅ Server created and configured
- ✅ Bot files uploaded (GitHub or manual)
- ✅ Environment variables set (`DISCORD_TOKEN`)
- ✅ Startup command configured
- ✅ Dependencies installed
- ✅ Bot started and online in Discord
- ✅ Auto-deploy configured (optional but recommended)
- ✅ Commands tested and working

## 🆘 Need Help?

### Wispbyte Support:
- **Discord:** Join Wispbyte Discord server
- **Tickets:** Open support ticket in client area
- **Knowledge Base:** https://wispbyte.com/kb/

### Bot Issues:
- Check console logs first
- Review error messages
- Test commands in Discord
- Verify all configuration steps

## 🔗 Useful Links

- **Wispbyte:** https://wispbyte.com/
- **Wispbyte Client Area:** https://wispbyte.com/client
- **Knowledge Base:** https://wispbyte.com/kb/getting-started
- **Your GitHub Repo:** https://github.com/abdullah-fr/QuettaTeaBot
- **Discord Developer Portal:** https://discord.com/developers/applications

## 🎉 Alternative: If Wispbyte is Full

If Wispbyte doesn't have free slots available, try:

1. **Replit** - Easiest alternative
2. **Render** - Free tier with auto-sleep
3. **bot-hosting.net** - Similar to Wispbyte
4. **Wait for LemonHost** - Check back later

---

**Your bot is ready to deploy on Wispbyte!** 🚀

Follow the steps above and you'll be live in minutes with automatic GitHub deployments.

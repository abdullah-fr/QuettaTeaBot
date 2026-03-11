# ⚡ Quick Deploy Reference

## 🚀 One-Time Setup

1. **Sign up:** https://lemonhost.me/
2. **Create bot server** → Select Python
3. **Connect GitHub:** `abdullah-fr/QuettaTeaBot`
4. **Add env variable:** `DISCORD_TOKEN=your_token`
5. **Startup command:** `bash start.sh`
6. **Deploy!**

## 🔄 Every Update (Auto-Deploy)

```bash
# Make your changes, then:
git add .
git commit -m "Your update message"
git push origin main

# LemonHost auto-deploys in ~30 seconds! ✅
```

## 🔗 GitHub Webhook (if needed)

**GitHub Repo Settings:**
- Settings → Webhooks → Add webhook
- Payload URL: (from LemonHost dashboard)
- Content type: `application/json`
- Events: "Just the push event"
- Active: ✅

## 📋 Files Ready for Deployment

- ✅ `requirements.txt` - Dependencies
- ✅ `Procfile` - Railway/Heroku style
- ✅ `runtime.txt` - Python 3.11
- ✅ `start.sh` - Startup script
- ✅ `.gitignore` - Excludes .env
- ✅ `src/main_bot.py` - Main bot

## 🎯 Startup Commands (choose one)

```bash
bash start.sh
# OR
cd src && python main_bot.py
# OR
python src/main_bot.py
```

## ✅ Test Auto-Deploy

```bash
# Add a comment to test
echo "# Test deploy" >> README.md
git add README.md
git commit -m "Test auto-deploy"
git push origin main

# Watch LemonHost console - should auto-restart!
```

## 🐛 Quick Troubleshooting

**Bot won't start?**
- Check `DISCORD_TOKEN` in env variables
- View console logs in LemonHost

**Auto-deploy not working?**
- Check GitHub webhook deliveries
- Verify webhook URL matches LemonHost

**Bot crashes?**
- Check console logs
- Ensure `data/bot_data.json` exists

## 📊 Monitor

- **LemonHost Dashboard:** Real-time logs, CPU/RAM
- **Discord:** Check bot online status
- **GitHub:** Webhook delivery status

---

**Ready to deploy!** Follow DEPLOYMENT_GUIDE.md for detailed steps.

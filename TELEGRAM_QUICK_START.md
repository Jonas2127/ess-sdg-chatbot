# 📱 Telegram Bot - Quick Start (100% FREE - 5 Minutes)

Make your ESS chatbot available on Telegram 24/7 with **NO COST**!

---

## 🚀 100% FREE Setup (Glitch.com)

### Step 1: Create Telegram Bot (2 minutes)

1. Open Telegram → Search: `@BotFather`
2. Send: `/newbot`
3. Bot name: `ESS Statistical Chatbot`
4. Username: `ess_stats_bot` (or any name ending with `bot`)
5. **Copy the token** (looks like: `123456789:ABCdef...`)

### Step 2: Deploy on Glitch (3 minutes)

1. Go to: **https://glitch.com**
2. Sign up with **GitHub** (FREE - no credit card needed!)
3. Click **"New Project"** → **"Import from GitHub"**
4. Enter: `https://github.com/Jonas2127/ess-sdg-chatbot`
5. Click **".env"** file → Add:
   ```
   TELEGRAM_BOT_TOKEN=your_token_from_step_1
   GROQ_API_KEY=your_groq_api_key
   LLM_PROVIDER=groq
   ```
6. Create `glitch.json` file with:
   ```json
   {
     "install": "pip install -r requirements.txt",
     "start": "python telegram_bot.py"
   }
   ```

### Step 3: Keep Bot Awake (FREE)

1. Go to: **https://uptimerobot.com**
2. Sign up (FREE)
3. Add monitor:
   - URL: `https://YOUR-PROJECT-NAME.glitch.me`
   - Interval: 5 minutes
4. This pings your bot every 5 minutes → Stays awake 24/7!

### Step 4: Test Your Bot

1. Open Telegram
2. Search for your bot (e.g., `@ess_stats_bot`)
3. Click **"Start"**
4. Send: `What is Ethiopia's population?`

**Done! Your bot is live 24/7 for FREE!** 🎉

---

## 💰 Cost: $0/month

- ✅ Glitch hosting: FREE
- ✅ UptimeRobot: FREE
- ✅ Telegram: FREE
- ✅ Groq API: FREE
- ✅ NO credit card required!

---

## 📚 Full Documentation

See `docs/TELEGRAM_FREE_DEPLOYMENT.md` for:
- Alternative free platforms (Replit)
- Running on your own computer
- Detailed troubleshooting
- More configuration options

---

## 🎯 What You Get

✅ **24/7 availability** - Bot never sleeps (with UptimeRobot)
✅ **100% FREE** - No credit card, no hidden costs
✅ **Fast responses** - 1-3 seconds via Groq
✅ **Full RAG access** - 221 PDFs + 12,037 indicators
✅ **No maintenance** - Auto-restarts on errors

---

## ⚡ Commands Your Bot Understands

- `/start` - Welcome message
- `/help` - How to use the bot
- `/about` - Bot information
- Any question - Get AI-powered answers!

---

## 🔗 Quick Links

- **Get Bot Token:** https://t.me/BotFather
- **Deploy on Glitch:** https://glitch.com
- **Keep Awake:** https://uptimerobot.com
- **Full Free Guide:** `docs/TELEGRAM_FREE_DEPLOYMENT.md`

---

**Questions?** Read the full free deployment guide!

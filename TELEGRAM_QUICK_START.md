# 📱 Telegram Bot - Quick Start (5 Minutes)

Make your ESS chatbot available on Telegram 24/7!

---

## 🚀 Super Quick Setup (Railway - Recommended)

### Step 1: Create Telegram Bot (2 minutes)

1. Open Telegram → Search: `@BotFather`
2. Send: `/newbot`
3. Bot name: `ESS Statistical Chatbot`
4. Username: `ess_stats_bot` (or any name ending with `bot`)
5. **Copy the token** (looks like: `123456789:ABCdef...`)

### Step 2: Deploy on Railway (3 minutes)

1. Go to: **https://railway.app**
2. Sign in with **GitHub**
3. Click **"Deploy from GitHub repo"**
4. Select: `Jonas2127/ess-sdg-chatbot`
5. Go to **"Variables"** → Add:
   ```
   TELEGRAM_BOT_TOKEN = your_token_from_step_1
   GROQ_API_KEY = your_groq_api_key_here
   LLM_PROVIDER = groq
   ```
6. Go to **"Settings"** → Set start command:
   ```
   python telegram_bot.py
   ```
7. Click **"Deploy"**

### Step 3: Test Your Bot

1. Open Telegram
2. Search for your bot (e.g., `@ess_stats_bot`)
3. Click **"Start"**
4. Send: `What is Ethiopia's population?`

**Done! Your bot is live 24/7!** 🎉

---

## 📚 Full Documentation

See `docs/TELEGRAM_BOT_DEPLOYMENT.md` for:
- Alternative hosting platforms (Render, PythonAnywhere)
- Detailed configuration
- Troubleshooting
- Monitoring

---

## 🎯 What You Get

✅ **24/7 availability** - Bot never sleeps
✅ **Free hosting** - Railway gives 500 hours/month
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
- **Deploy on Railway:** https://railway.app
- **Full Guide:** `docs/TELEGRAM_BOT_DEPLOYMENT.md`

---

**Questions?** Read the full deployment guide or check the logs!

# 📱 Telegram Bot Deployment Guide

Deploy your ESS RAG Chatbot as a 24/7 Telegram bot for FREE!

---

## 🎯 Overview

Your chatbot will be available on Telegram with:
- ✅ 24/7 availability
- ✅ Instant responses (1-3 seconds)
- ✅ Access to 221 ESS PDFs + 12,037 SDG indicators
- ✅ FREE hosting (using Railway, Render, or PythonAnywhere)

---

## 📋 Prerequisites

1. **Telegram Bot Token** (from @BotFather)
2. **Your code on GitHub** (already done ✅)
3. **Free hosting account** (Railway, Render, or PythonAnywhere)

---

## 🤖 Step 1: Create Your Telegram Bot

### 1.1 Open Telegram and Search for @BotFather

1. Open Telegram app
2. Search for: `@BotFather`
3. Start chat with BotFather

### 1.2 Create New Bot

Send these commands to @BotFather:

```
/newbot
```

BotFather will ask for:

**1. Bot Name** (display name):
```
ESS Statistical Chatbot
```

**2. Bot Username** (must end with 'bot'):
```
ess_stats_bot
```
(or any available name ending with `bot`)

### 1.3 Get Your Bot Token

BotFather will give you a token like:
```
123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567
```

**⚠️ KEEP THIS SECRET!** This is your bot's access key.

### 1.4 Optional: Customize Your Bot

Set description:
```
/setdescription
```
Then paste:
```
Ask questions about Ethiopian statistics! Access 221 ESS reports and 12,037 UN SDG indicators. Powered by AI.
```

Set about text:
```
/setabouttext
```
Then paste:
```
ESS RAG Chatbot - Your AI assistant for Ethiopian statistical data. Available 24/7!
```

Set profile photo (optional):
```
/setuserpic
```

---

## ☁️ Step 2: Deploy on Railway (FREE - Recommended)

Railway offers **500 hours/month FREE** ($5 credit) - perfect for 24/7 bots!

### 2.1 Create Railway Account

1. Go to: https://railway.app
2. Click **"Start a New Project"**
3. Sign up with **GitHub** (easiest)

### 2.2 Deploy from GitHub

1. Click **"Deploy from GitHub repo"**
2. Select: `Jonas2127/ess-sdg-chatbot`
3. Railway will detect Python and start building

### 2.3 Configure Environment Variables

In Railway dashboard:

1. Click on your project
2. Go to **"Variables"** tab
3. Add these secrets:

```bash
GROQ_API_KEY=your_groq_api_key_here
LLM_PROVIDER=groq
TELEGRAM_BOT_TOKEN=your_token_from_botfather_here
```

### 2.4 Set Start Command

1. Go to **"Settings"** tab
2. Find **"Custom Start Command"**
3. Set to:
```bash
python telegram_bot.py
```

### 2.5 Deploy

1. Click **"Deploy"**
2. Wait 5-10 minutes for:
   - Package installation
   - ChromaDB download from Hugging Face
   - Bot startup

### 2.6 Check Logs

1. Go to **"Deployments"** tab
2. Click latest deployment
3. Check logs for:
```
✅ Telegram bot is running!
```

---

## 🎨 Alternative: Deploy on Render (FREE)

Render offers **750 hours/month FREE**!

### 3.1 Create Render Account

1. Go to: https://render.com
2. Sign up with **GitHub**

### 3.2 Create New Web Service

1. Click **"New +"** → **"Background Worker"**
2. Connect your GitHub repo: `Jonas2127/ess-sdg-chatbot`
3. Configure:
   - **Name**: `ess-telegram-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python telegram_bot.py`

### 3.3 Add Environment Variables

In the **"Environment"** section, add:

```bash
GROQ_API_KEY=your_groq_api_key_here
LLM_PROVIDER=groq
TELEGRAM_BOT_TOKEN=your_token_from_botfather_here
```

### 3.4 Deploy

1. Click **"Create Background Worker"**
2. Wait for deployment (5-10 minutes)
3. Check logs for success message

---

## 🐍 Alternative: Deploy on PythonAnywhere (FREE)

PythonAnywhere offers **always-free tier**!

### 4.1 Create Account

1. Go to: https://www.pythonanywhere.com
2. Sign up for **FREE Beginner account**

### 4.2 Upload Code

**Option A: From GitHub (easier)**
1. Open Bash console
2. Clone repository:
```bash
git clone https://github.com/Jonas2127/ess-sdg-chatbot.git
cd ess-sdg-chatbot
```

**Option B: Upload files manually**
1. Go to **"Files"** tab
2. Upload all project files

### 4.3 Install Dependencies

In Bash console:
```bash
cd ess-sdg-chatbot
pip3.11 install -r requirements.txt --user
```

### 4.4 Create .env File

```bash
nano .env
```

Add:
```bash
GROQ_API_KEY=your_groq_api_key_here
LLM_PROVIDER=groq
TELEGRAM_BOT_TOKEN=your_token_from_botfather_here
```

Save with `Ctrl+X`, then `Y`, then `Enter`

### 4.5 Run Bot as Always-On Task

1. Go to **"Tasks"** tab
2. Add a new scheduled task:
   - **Command**: `python3.11 /home/yourusername/ess-sdg-chatbot/telegram_bot.py`
   - **Time**: `Daily at 00:00` (will keep running)

OR run in console:
```bash
python3.11 telegram_bot.py &
```

---

## ✅ Step 3: Test Your Bot

### 3.1 Find Your Bot on Telegram

1. Open Telegram
2. Search for your bot username (e.g., `@ess_stats_bot`)
3. Click **"Start"**

### 3.2 Test Commands

Try these:
```
/start
/help
/about
```

### 3.3 Ask Questions

Try:
```
What is Ethiopia's population?
Show me inflation trends
What is the GDP?
```

---

## 📊 Monitoring

### Check if Bot is Running

**Railway:**
- Dashboard → Deployments → View Logs

**Render:**
- Dashboard → Your Service → Logs

**PythonAnywhere:**
- Bash console → Check process:
```bash
ps aux | grep telegram_bot
```

### Restart Bot

**Railway/Render:**
- Click **"Restart"** button in dashboard

**PythonAnywhere:**
```bash
pkill -f telegram_bot.py
python3.11 telegram_bot.py &
```

---

## 🔧 Troubleshooting

### Bot Not Responding

1. **Check logs** for errors
2. **Verify environment variables** are set correctly
3. **Ensure ChromaDB downloaded** (check logs)
4. **Test Groq API key** is valid

### "Connection timeout" errors

- Bot token is incorrect
- Railway/Render service is sleeping (free tier limitation)
- Solution: Use "Always On" setting or upgrade plan

### Memory Issues

- ChromaDB is large (400MB)
- Ensure hosting has 1GB+ RAM
- Railway/Render free tier has enough

### Bot Stops After Some Time

**PythonAnywhere:**
- Free tier tasks run for 100 seconds only
- Solution: Use Railway or Render instead

**Railway/Render:**
- Free tier sleeps after 30 minutes inactivity
- Solution: Keep bot active with webhook or upgrade

---

## 💰 Cost Comparison

| Platform | Free Tier | RAM | Storage | Uptime |
|----------|-----------|-----|---------|--------|
| **Railway** | 500 hours/month | 512MB | 1GB | 99.9% |
| **Render** | 750 hours/month | 512MB | 1GB | 99.9% |
| **PythonAnywhere** | Always-free | 512MB | 512MB | 95% |

**Recommendation:** Use **Railway** or **Render** for best reliability.

---

## 🎯 Quick Start (Railway - 5 Minutes)

1. **Get bot token:** Message @BotFather on Telegram → `/newbot`
2. **Deploy:** https://railway.app → Deploy from GitHub → Select repo
3. **Add secrets:** Variables tab → Add `TELEGRAM_BOT_TOKEN`, `GROQ_API_KEY`, `LLM_PROVIDER`
4. **Set command:** Settings → Custom Start Command → `python telegram_bot.py`
5. **Test:** Find your bot on Telegram → Send `/start`

Done! Your bot is live 24/7! 🎉

---

## 🔗 Useful Links

- **Telegram BotFather:** https://t.me/BotFather
- **Railway:** https://railway.app
- **Render:** https://render.com
- **PythonAnywhere:** https://www.pythonanywhere.com
- **Bot API Docs:** https://core.telegram.org/bots

---

## 🆘 Need Help?

Check the logs first! Most issues show clear error messages.

Common issues and solutions are in the Troubleshooting section above.

---

**🎉 Congratulations! Your ESS RAG Chatbot is now available 24/7 on Telegram!**

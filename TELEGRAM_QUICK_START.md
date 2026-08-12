# 📱 Telegram Bot - 100% FREE Setup (10 Minutes)

Deploy your Telegram bot **completely FREE** on PythonAnywhere!

---

## 🚀 FREE Setup (PythonAnywhere - Always Free)

### Step 1: Create Telegram Bot (2 minutes)

1. Open Telegram → Search: `@BotFather`
2. Send: `/newbot`
3. Bot name: `ESS Statistical Chatbot`
4. Username: `ess_stats_bot` (or any name ending with `bot`)
5. **Copy the token**

### Step 2: Sign Up on PythonAnywhere (1 minute)

1. Go to: **https://www.pythonanywhere.com**
2. Click **"Create a Beginner account"** (100% FREE forever)
3. No credit card needed!

### Step 3: Upload Code (3 minutes)

1. Click **"Consoles"** → **"Bash"**
2. Run:
```bash
git clone https://github.com/Jonas2127/ess-sdg-chatbot.git
cd ess-sdg-chatbot
pip3.11 install --user -r requirements.txt
```

Wait 5-10 minutes for packages to install.

### Step 4: Configure Bot (2 minutes)

```bash
nano .env
```

Add:
```
TELEGRAM_BOT_TOKEN=your_token_from_step_1
GROQ_API_KEY=your_groq_api_key
LLM_PROVIDER=groq
```

Save: `Ctrl+X` → `Y` → `Enter`

### Step 5: Create Keep-Alive Script (2 minutes)

```bash
nano keep_alive.sh
```

Add:
```bash
#!/bin/bash
while true; do
    cd /home/YOUR_USERNAME/ess-sdg-chatbot
    python3.11 telegram_bot.py
    sleep 5
done
```

Replace `YOUR_USERNAME` with your PythonAnywhere username.

Make executable and run:
```bash
chmod +x keep_alive.sh
nohup ./keep_alive.sh > bot.log 2>&1 &
```

### Step 6: Test

1. Open Telegram
2. Find your bot (e.g., `@ess_stats_bot`)
3. Send: `What is Ethiopia's population?`

**Done! Bot runs 24/7 for FREE!** 🎉

---

## 💰 Cost: $0 Forever

PythonAnywhere's Beginner account is **always FREE** with:
- ✅ No expiration
- ✅ No credit card required
- ✅ 24/7 uptime
- ✅ 512MB storage (enough!)

---

## 📚 Full Guide

See `docs/PYTHONANYWHERE_SETUP.md` for:
- Detailed setup instructions
- Troubleshooting
- Bot management commands
- How to check logs

---

## 🎯 What You Get

✅ **24/7 availability** - Runs continuously
✅ **100% FREE** - No hidden costs
✅ **Fast responses** - 1-3 seconds
✅ **Full RAG access** - 221 PDFs + 12,037 indicators
✅ **Auto-restart** - Never stops

---

## 🔗 Quick Links

- **PythonAnywhere:** https://www.pythonanywhere.com
- **Get Bot Token:** https://t.me/BotFather
- **Full Setup Guide:** `docs/PYTHONANYWHERE_SETUP.md`

---

**Simple. Free. Forever.** 🚀

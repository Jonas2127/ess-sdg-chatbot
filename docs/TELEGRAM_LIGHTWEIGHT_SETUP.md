# 📱 Lightweight Telegram Bot Setup (PythonAnywhere FREE)

Run a tiny Telegram bot that directs users to your Streamlit app!

**Size:** < 10 MB (fits PythonAnywhere free 512 MB limit)
**Cost:** $0 forever

---

## 🎯 How It Works

Your bot will:
1. ✅ Respond to commands (`/start`, `/help`, `/about`)
2. ✅ Receive user questions
3. ✅ Direct users to your Streamlit app for answers
4. ✅ Run 24/7 on PythonAnywhere for FREE

---

## 📋 Setup Steps (5 Minutes)

### Step 1: Create Telegram Bot

1. Open Telegram → Search: `@BotFather`
2. Send: `/newbot`
3. Name: `ESS Statistical Chatbot`
4. Username: `ess_stats_bot` (or similar)
5. Copy the token

### Step 2: Sign Up on PythonAnywhere

1. Go to: https://www.pythonanywhere.com
2. Create **"Beginner account"** (FREE)
3. Verify your email

### Step 3: Upload Bot Code

In PythonAnywhere **Bash console**:

```bash
# Download just the bot files
wget https://raw.githubusercontent.com/Jonas2127/ess-sdg-chatbot/main/telegram_bot_lightweight.py
wget https://raw.githubusercontent.com/Jonas2127/ess-sdg-chatbot/main/requirements_lightweight.txt
```

### Step 4: Install Dependencies (< 10 MB)

```bash
pip3.11 install --user -r requirements_lightweight.txt
```

This takes **30 seconds** (not 10 minutes!) and uses < 10 MB!

### Step 5: Create .env File

```bash
nano .env
```

Add:
```
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
STREAMLIT_APP_URL=https://ess-rag-chatbot.streamlit.app
```

Save: `Ctrl+X` → `Y` → `Enter`

### Step 6: Test the Bot

```bash
python3.11 telegram_bot_lightweight.py
```

If you see `✅ Telegram bot is running!` → Success!

Test on Telegram → Find your bot → Send `/start`

Press `Ctrl+C` to stop.

### Step 7: Run 24/7

```bash
nohup python3.11 telegram_bot_lightweight.py > bot.log 2>&1 &
```

Done! Bot runs forever!

---

## 🎯 What Your Bot Does

When users message your bot, it will:
1. ✅ Greet them with welcome message
2. ✅ Show help and commands
3. ✅ Receive their questions
4. ✅ **Direct them to your Streamlit app** for full answers

**Why this approach:**
- ✅ Bot is tiny (< 10 MB) - fits free tier
- ✅ Your Streamlit app is already running 24/7
- ✅ Users get full RAG system via web app
- ✅ Both are FREE!

---

## 📊 User Experience

**User:** Sends question to Telegram bot

**Bot replies:**
```
Thank you for your question: What is Ethiopia's population?

For the most accurate and detailed response, please visit our web application:
🌐 https://ess-rag-chatbot.streamlit.app

The web app provides:
✅ Full access to 221 PDF reports
✅ 12,037 SDG indicators
✅ Interactive visualizations
✅ Source citations
✅ Export to PDF/Word

Simply paste your question there!
```

---

## 🔧 Bot Management

### Check if running:
```bash
ps aux | grep telegram_bot_lightweight
```

### View logs:
```bash
tail -f bot.log
```

### Stop bot:
```bash
pkill -f telegram_bot_lightweight
```

### Restart bot:
```bash
nohup python3.11 telegram_bot_lightweight.py > bot.log 2>&1 &
```

---

## 💰 Cost Breakdown

| Item | Cost |
|------|------|
| PythonAnywhere hosting | $0 |
| Telegram bot | $0 |
| Streamlit web app | $0 |
| Storage (< 10 MB) | $0 |
| **TOTAL** | **$0** |

---

## ✅ Advantages of This Approach

1. **Fits free tier:** < 10 MB vs 2+ GB for full system
2. **Fast setup:** 5 minutes vs 30+ minutes
3. **No disk errors:** Tiny footprint
4. **Same result:** Users access your full RAG system via web app
5. **Professional:** Telegram presence + powerful web app

---

## 🎉 You Now Have:

✅ **Streamlit web app** - Full RAG system (already deployed)
✅ **Lightweight Telegram bot** - Directs users to web app
✅ **Both run 24/7 for FREE!**

Total investment: **$0 and 5 minutes** 🚀

---

## 🔗 Quick Reference

- **PythonAnywhere:** https://www.pythonanywhere.com
- **Your Streamlit app:** https://ess-rag-chatbot.streamlit.app
- **Get bot token:** https://t.me/BotFather

---

**Simple. Lightweight. Free. Forever.** ✨

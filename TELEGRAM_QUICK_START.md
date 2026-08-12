# 📱 Telegram Bot - 100% FREE Setup (5 Minutes)

Deploy a lightweight Telegram bot that connects users to your Streamlit app!

---

## 🚀 Quick Setup (PythonAnywhere - Always Free)

### What You Get:
- ✅ Telegram bot running 24/7 (FREE)
- ✅ Directs users to your Streamlit web app
- ✅ Uses < 10 MB (fits free tier perfectly)
- ✅ No credit card required

---

### Step 1: Create Telegram Bot (2 minutes)

1. Open Telegram → Search: `@BotFather`
2. Send: `/newbot`
3. Bot name: `ESS Statistical Chatbot`
4. Username: `ess_stats_bot` (or any name ending with `bot`)
5. **Copy the token**

---

### Step 2: Deploy on PythonAnywhere (3 minutes)

1. Go to: **https://www.pythonanywhere.com**
2. Create **"Beginner account"** (FREE forever)
3. Open **Bash console** (Consoles tab → Bash)
4. Run these commands:

```bash
# Download lightweight bot files
wget https://raw.githubusercontent.com/Jonas2127/ess-sdg-chatbot/main/telegram_bot_lightweight.py
wget https://raw.githubusercontent.com/Jonas2127/ess-sdg-chatbot/main/requirements_lightweight.txt

# Install packages (30 seconds, < 10 MB)
pip3.11 install --user -r requirements_lightweight.txt

# Create environment file
nano .env
```

5. In nano editor, type:
```
TELEGRAM_BOT_TOKEN=your_token_from_step_1
STREAMLIT_APP_URL=https://ess-rag-chatbot.streamlit.app
```

6. Save: `Ctrl+X` → `Y` → `Enter`

7. Run bot in background:
```bash
nohup python3.11 telegram_bot_lightweight.py > bot.log 2>&1 &
```

---

### Step 3: Test Your Bot

1. Open Telegram
2. Find your bot (e.g., `@ess_stats_bot`)
3. Send: `/start`
4. Ask a question!

**Done! Bot runs 24/7 for FREE!** 🎉

---

## 🎯 How It Works

Your bot will:
1. ✅ Receive questions on Telegram
2. ✅ Direct users to your Streamlit web app
3. ✅ Users get full RAG answers with visualizations
4. ✅ Run 24/7 using only 10 MB storage

**Why this approach:**
- Telegram bot fits PythonAnywhere free tier (512 MB limit)
- Your Streamlit app provides full functionality (already running 24/7)
- Both services are 100% FREE
- Users get better experience (web has more features)

---

## 💰 Total Cost: $0

| Service | Cost |
|---------|------|
| PythonAnywhere hosting | $0 |
| Streamlit web app | $0 |
| Telegram bot | $0 |
| Groq API | $0 |
| **TOTAL** | **$0** |

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

## 🔗 Quick Links

- **PythonAnywhere:** https://www.pythonanywhere.com
- **Get Bot Token:** https://t.me/BotFather  
- **Your Web App:** https://ess-rag-chatbot.streamlit.app

---

**Lightweight. Free. Forever.** 🚀

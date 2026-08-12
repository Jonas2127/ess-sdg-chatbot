# 🤖 Two Telegram Bots Setup Guide

You now have TWO Telegram bots for different purposes!

---

## 📱 Bot #1: Lightweight (24/7 on PythonAnywhere)

**Username:** `@ess_stats_bot`  
**Token:** `8908371770:AAEgKeISiu-GpkWgZK0SIecBbQK81Wg-A_s`

**What it does:**
- ✅ Runs 24/7 for FREE on PythonAnywhere
- ✅ Receives user questions
- ✅ Directs users to web app for full answers
- ✅ Uses < 10 MB storage

**Best for:** Always-on presence, when you're not at your computer

**File:** `telegram_bot_lightweight.py`

---

## 🚀 Bot #2: Full RAG (Local on Your PC)

**Username:** `@ess_stats_full_bot` (or whatever you named it)  
**Token:** Get from @BotFather

**What it does:**
- ✅ Answers questions DIRECTLY using full RAG system
- ✅ Searches 221 ESS PDF reports
- ✅ Queries 12,037 UN SDG indicators
- ✅ Provides source citations
- ✅ Fast responses (1-3 seconds)

**Best for:** When your computer is on and you want direct answers

**File:** `telegram_bot.py`

---

## 🔧 Setup Instructions

### Step 1: Create Second Bot

1. Open Telegram → Message `@BotFather`
2. Send: `/newbot`
3. **Name:** `ESS Statistical Chatbot Full`
4. **Username:** `ess_stats_full_bot` (must end with 'bot')
5. **Copy the token** BotFather gives you

### Step 2: Add Token to .env File

1. Open `.env` file in your project folder
2. Find this line:
   ```
   TELEGRAM_BOT_TOKEN=PASTE_YOUR_NEW_TOKEN_HERE
   ```
3. Replace `PASTE_YOUR_NEW_TOKEN_HERE` with your actual token
4. Save the file

### Step 3: Run the Full Bot

**Option A - Double-click:**
- Double-click `RUN_TELEGRAM_BOT.bat`

**Option B - Command line:**
```cmd
python telegram_bot.py
```

### Step 4: Test Both Bots

**Test Bot #1 (Lightweight):**
1. Search `@ess_stats_bot` on Telegram
2. Send a question
3. Bot redirects you to web app

**Test Bot #2 (Full):**
1. Search `@ess_stats_full_bot` on Telegram  
2. Send a question
3. Bot answers directly with full RAG!

---

## 📊 Comparison

| Feature | Bot #1 (Lightweight) | Bot #2 (Full RAG) |
|---------|---------------------|-------------------|
| **Availability** | 24/7 | Only when PC is on |
| **Location** | PythonAnywhere | Your computer |
| **Answers** | Redirects to web | Direct answers |
| **RAG System** | ❌ No | ✅ Yes |
| **Cost** | $0 | $0 (electricity) |
| **Storage** | < 10 MB | 2+ GB |
| **Best For** | Always-on presence | Direct answers |

---

## 💡 Usage Strategy

**Recommended approach:**

1. **Share Bot #1** (`@ess_stats_bot`) with public users
   - Always available 24/7
   - No dependency on your PC
   - Users get answers via web app

2. **Use Bot #2** (`@ess_stats_full_bot`) for yourself
   - Run when you're working
   - Get instant answers in Telegram
   - No need to open web browser

---

## 🔄 Managing Both Bots

### Bot #1 (PythonAnywhere):
**Start:**
```bash
nohup python3.11 telegram_bot_lightweight.py > bot.log 2>&1 &
```

**Stop:**
```bash
pkill -f telegram_bot_lightweight
```

**Check status:**
```bash
ps aux | grep telegram_bot_lightweight
```

### Bot #2 (Your PC):
**Start:**
- Double-click `RUN_TELEGRAM_BOT.bat`
- OR run: `python telegram_bot.py`

**Stop:**
- Close the terminal window
- OR press `Ctrl+C`

---

## ✅ Benefits of Two Bots

1. **24/7 Availability:** Bot #1 always responds
2. **Full Power When Needed:** Bot #2 gives complete answers
3. **No Conflicts:** Each bot has its own token
4. **Flexible:** Choose based on your needs
5. **Free:** Both cost $0 to run

---

## 🎯 Current Status

- ✅ **Bot #1 running** on PythonAnywhere
- ⏳ **Bot #2 ready** to run (just add token to .env)

Once you add the token, you're all set!

---

**Questions? Just run the bot that fits your needs!** 🚀

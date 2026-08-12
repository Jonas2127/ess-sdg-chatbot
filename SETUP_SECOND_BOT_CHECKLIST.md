# ✅ Quick Checklist: Setup Second Bot

## Step-by-Step:

### ☐ Step 1: Create New Bot (2 minutes)
1. Open Telegram
2. Message `@BotFather`
3. Send: `/newbot`
4. Name: `ESS Statistical Chatbot Full`
5. Username: `ess_stats_full_bot`
6. **COPY THE TOKEN** ← Don't forget this!

---

### ☐ Step 2: Add Token to .env (30 seconds)
1. Open file: `C:\Users\HP\ESSFINALPROJECT\.env`
2. Find line: `TELEGRAM_BOT_TOKEN=PASTE_YOUR_NEW_TOKEN_HERE`
3. Replace `PASTE_YOUR_NEW_TOKEN_HERE` with your token
4. Save file

---

### ☐ Step 3: Run Full Bot (10 seconds)
**Double-click:** `RUN_TELEGRAM_BOT.bat`

You should see:
```
🚀 Starting Telegram bot...
Initializing RAG system...
✅ Telegram bot is running!
```

---

### ☐ Step 4: Test It! (1 minute)
1. Open Telegram
2. Search: `@ess_stats_full_bot`
3. Send: `/start`
4. Ask: `What is Ethiopia's population?`
5. **You should get a REAL answer!** (not a redirect)

---

## ✅ Done!

Now you have:
- 🤖 Bot #1 (`@ess_stats_bot`) - 24/7 on PythonAnywhere
- 🚀 Bot #2 (`@ess_stats_full_bot`) - Full RAG on your PC

Both work independently! 🎉

---

## 🆘 Troubleshooting

**Bot doesn't respond:**
- Check: Is the token in `.env` correct?
- Check: Did you save the `.env` file?
- Check: Is `RUN_TELEGRAM_BOT.bat` still running?

**"System is initializing" message:**
- Wait 30 seconds for ChromaDB to load
- First run takes longer

**Still getting redirects:**
- You're messaging the WRONG bot
- Make sure you're messaging `@ess_stats_full_bot` (the new one)
- Not `@ess_stats_bot` (the old one)

---

**Total Time: 3 minutes** ⏱️

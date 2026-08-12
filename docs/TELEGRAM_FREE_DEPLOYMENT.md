# 📱 100% FREE Telegram Bot Deployment (No Credit Card)

Deploy your Telegram bot **completely FREE** with **NO credit card required**!

---

## 🎯 Best Option: Glitch.com (100% FREE Forever)

Glitch offers **unlimited free hosting** with no credit card!

### ✅ Features:
- 💯 **100% FREE** - No credit card required
- 🔄 **24/7 uptime** - Automatically stays awake
- 🚀 **Easy setup** - 5 minutes
- 📊 **Built-in editor** - Edit code directly
- 🔒 **Secure** - Environment variables protected

---

## 📋 Step-by-Step Guide

### Step 1: Create Telegram Bot (2 minutes)

1. Open Telegram → Search: `@BotFather`
2. Send: `/newbot`
3. **Bot name:** `ESS Statistical Chatbot`
4. **Username:** `ess_stats_bot` (or any name ending with `bot`)
5. **Copy the token** (format: `123456789:ABCdef...`)

---

### Step 2: Deploy on Glitch (3 minutes)

#### 2.1 Create Glitch Account

1. Go to: **https://glitch.com**
2. Click **"Sign up"**
3. Sign up with **GitHub** (easiest)

#### 2.2 Import Project

1. Click **"New Project"** → **"Import from GitHub"**
2. Enter: `https://github.com/Jonas2127/ess-sdg-chatbot`
3. Wait for import (30 seconds)

#### 2.3 Add Environment Variables

1. Click **".env"** file in the left sidebar
2. Add these lines:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_from_step_1
GROQ_API_KEY=your_groq_api_key
LLM_PROVIDER=groq
```

Replace with your actual tokens!

#### 2.4 Modify glitch.json (Create if not exists)

1. Click **"New File"** → Name it `glitch.json`
2. Add this content:

```json
{
  "install": "pip install -r requirements.txt",
  "start": "python telegram_bot.py",
  "watch": {
    "ignore": [
      "data/"
    ]
  }
}
```

#### 2.5 Keep Bot Awake

Glitch projects sleep after 5 minutes of inactivity. Fix this:

1. Click **"Tools"** → **"Terminal"**
2. Run:
```bash
curl https://YOUR-PROJECT-NAME.glitch.me
```

OR use **UptimeRobot** (free service to ping your bot):
1. Go to: https://uptimerobot.com
2. Sign up (FREE)
3. Add monitor:
   - **URL:** `https://YOUR-PROJECT-NAME.glitch.me`
   - **Monitoring Interval:** 5 minutes
   - This keeps your bot awake 24/7!

---

### Step 3: Test Your Bot

1. Open Telegram
2. Search for your bot (e.g., `@ess_stats_bot`)
3. Click **"Start"**
4. Send: `What is Ethiopia's population?`

**Done! Your bot is live 24/7!** 🎉

---

## 🔄 Alternative: Replit (Also 100% FREE)

Another free option with NO credit card!

### Quick Setup:

1. Go to: **https://replit.com**
2. Sign up with **GitHub**
3. Click **"Create Repl"** → **"Import from GitHub"**
4. Enter: `https://github.com/Jonas2127/ess-sdg-chatbot`
5. Set **"Run command"** to: `python telegram_bot.py`
6. Add **Secrets** (equivalent to environment variables):
   ```
   TELEGRAM_BOT_TOKEN=your_token
   GROQ_API_KEY=your_key
   LLM_PROVIDER=groq
   ```
7. Click **"Run"**
8. Enable **"Always On"** (may require Hacker plan - but has 3 free repls)

---

## 🏠 Run on Your Computer (Completely FREE)

If you have a computer that's always on:

### Windows:

1. Open Command Prompt
2. Navigate to project:
```cmd
cd C:\Users\HP\ESSFINALPROJECT
```

3. Run bot:
```cmd
python telegram_bot.py
```

4. Keep terminal open!

### To run in background:
Create a batch file `run_bot.bat`:
```batch
@echo off
python telegram_bot.py
```

Add to **Windows Startup**:
1. Press `Win+R`
2. Type: `shell:startup`
3. Copy `run_bot.bat` there

Bot starts automatically when you log in!

---

### Linux/Mac:

1. Open Terminal
2. Navigate to project:
```bash
cd ~/ESSFINALPROJECT
```

3. Run bot in background:
```bash
nohup python telegram_bot.py &
```

Bot runs even after closing terminal!

---

## 📊 Comparison: FREE Options

| Platform | Cost | Credit Card | Uptime | Setup Time |
|----------|------|-------------|--------|------------|
| **Glitch** | FREE | ❌ No | 99% (with UptimeRobot) | 5 min |
| **Replit** | FREE | ❌ No | 90% (sleeps) | 5 min |
| **Your Computer** | FREE | ❌ No | Depends on you | 2 min |

**Recommendation:** **Glitch + UptimeRobot** = 100% free, 99% uptime! 🏆

---

## 🛠️ Keep Glitch Bot Awake (100% FREE)

### Using UptimeRobot (Recommended):

1. Go to: https://uptimerobot.com
2. Sign up (FREE - no credit card)
3. Add **"New Monitor"**:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** ESS Telegram Bot
   - **URL:** `https://YOUR-PROJECT-NAME.glitch.me`
   - **Monitoring Interval:** 5 minutes

4. UptimeRobot pings your bot every 5 minutes → Bot never sleeps!

### Using Cron-job.org:

1. Go to: https://cron-job.org
2. Sign up (FREE)
3. Create cronjob:
   - **URL:** `https://YOUR-PROJECT-NAME.glitch.me`
   - **Interval:** Every 5 minutes

---

## 🆘 Troubleshooting

### Bot Not Responding

**Check Glitch Logs:**
1. Click **"Tools"** → **"Logs"**
2. Look for errors

**Common Issues:**
- **Token error:** Check `.env` file has correct token
- **Module not found:** Glitch is installing packages (wait 1-2 minutes)
- **Memory error:** ChromaDB is downloading (wait 5 minutes first time)

### Glitch Project Sleeping

**Solution:** Use UptimeRobot (see above)

### Bot Stops After Some Time

**Glitch:** Projects sleep after 5 min inactivity
**Fix:** Use UptimeRobot to ping every 5 minutes

---

## 💰 Total Cost Breakdown

| Service | Monthly Cost |
|---------|-------------|
| **Glitch Hosting** | $0 |
| **UptimeRobot** | $0 |
| **Telegram Bot** | $0 |
| **Groq API** | $0 |
| **Hugging Face** | $0 |
| **TOTAL** | **$0** 🎉 |

---

## 🎯 Quick Start Summary

1. **Create bot:** @BotFather → `/newbot` → Copy token
2. **Deploy:** Glitch.com → Import GitHub repo
3. **Configure:** Add environment variables in `.env`
4. **Keep awake:** UptimeRobot → Ping every 5 minutes
5. **Test:** Find bot on Telegram → Send message

**Total time: 10 minutes**
**Total cost: $0** 
**Uptime: 99%** ✅

---

## 🔗 Useful Links

- **Glitch:** https://glitch.com
- **Replit:** https://replit.com
- **UptimeRobot:** https://uptimerobot.com
- **Cron-job.org:** https://cron-job.org
- **BotFather:** https://t.me/BotFather

---

**🎉 Congratulations! You now have a FREE 24/7 Telegram bot!**

No credit card. No hidden costs. Just FREE! 🚀

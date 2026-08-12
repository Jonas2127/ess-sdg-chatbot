# 🐍 PythonAnywhere - 100% FREE Telegram Bot Setup

Deploy your Telegram bot on PythonAnywhere's **always-free tier**!

---

## ✅ What You Get (FREE Forever):

- 💯 **Always FREE** - No credit card required
- 🔄 **24/7 available** - Runs continuously  
- 💾 **512 MB storage** - Enough for our bot
- 🐍 **Python 3.11** - Perfect for our needs
- 🌐 **Public API access** - Telegram works great

---

## 📋 Step-by-Step Setup (10 Minutes)

### Step 1: Create PythonAnywhere Account

1. Go to: **https://www.pythonanywhere.com**
2. Click **"Pricing & signup"**
3. Select **"Create a Beginner account"** (FREE - bottom of page)
4. Sign up with email (no credit card needed!)
5. Verify your email

---

### Step 2: Upload Your Code

#### Option A: From GitHub (Easier)

1. Click **"Consoles"** tab
2. Click **"Bash"** to open a terminal
3. Clone your repository:
```bash
git clone https://github.com/Jonas2127/ess-sdg-chatbot.git
cd ess-sdg-chatbot
```

#### Option B: Upload Manually

1. Click **"Files"** tab
2. Click **"Upload a file"**
3. Upload all your project files

---

### Step 3: Install Dependencies

In the Bash console:

```bash
cd ess-sdg-chatbot
pip3.11 install --user -r requirements.txt
```

**Wait 5-10 minutes** for installation (ChromaDB and PyTorch are large).

---

### Step 4: Create Environment File

Still in Bash console:

```bash
nano .env
```

Add your credentials:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
GROQ_API_KEY=your_groq_api_key
LLM_PROVIDER=groq
```

Save with:
- Press `Ctrl + X`
- Press `Y`
- Press `Enter`

---

### Step 5: Test the Bot

Run manually first to test:

```bash
python3.11 telegram_bot.py
```

If you see: `✅ Telegram bot is running!` → Success!

Press `Ctrl + C` to stop (we'll make it run always in next step).

---

### Step 6: Make Bot Run 24/7

PythonAnywhere FREE tier doesn't support scheduled tasks that run forever, so we'll use a workaround:

#### Create a Keep-Alive Script:

```bash
nano keep_alive.sh
```

Add this:
```bash
#!/bin/bash
while true; do
    cd /home/YOUR_USERNAME/ess-sdg-chatbot
    python3.11 telegram_bot.py
    echo "Bot stopped. Restarting in 5 seconds..."
    sleep 5
done
```

Replace `YOUR_USERNAME` with your PythonAnywhere username.

Make it executable:
```bash
chmod +x keep_alive.sh
```

#### Run in Background:

```bash
nohup ./keep_alive.sh > bot.log 2>&1 &
```

This runs the bot in the background and restarts it automatically if it crashes!

---

### Step 7: Verify Bot is Running

Check if bot is running:
```bash
ps aux | grep telegram_bot
```

You should see a process running.

Test on Telegram:
1. Find your bot (e.g., `@ess_stats_bot`)
2. Send `/start`
3. Ask a question!

---

## 🔄 Managing Your Bot

### Check Bot Status:
```bash
ps aux | grep telegram_bot
```

### View Logs:
```bash
tail -f bot.log
```

### Stop Bot:
```bash
pkill -f telegram_bot
```

### Restart Bot:
```bash
pkill -f telegram_bot
nohup ./keep_alive.sh > bot.log 2>&1 &
```

---

## ⚠️ PythonAnywhere FREE Tier Limitations

1. **CPU limit:** Bot will run but may be slow during peak times
2. **Console disconnects:** After 24 hours, console disconnects but bot keeps running
3. **No outbound HTTPS:** Can't call external HTTPS APIs except whitelisted ones
   - ✅ Telegram API is whitelisted
   - ✅ Most APIs work fine

---

## 🔧 Troubleshooting

### "Module not found" error:
```bash
pip3.11 install --user <module-name>
```

### Bot stops after some time:
Check if process is still running:
```bash
ps aux | grep telegram_bot
```

If not, restart with keep_alive script.

### "Cannot connect to Telegram":
Check your bot token in `.env` file.

### ChromaDB not downloading:
First run takes 5-10 minutes to download ChromaDB from Hugging Face. Be patient!

---

## 💰 Cost: $0/month Forever

PythonAnywhere Beginner account is **always FREE** with no expiration!

---

## 🎯 Summary

1. ✅ Sign up at PythonAnywhere (FREE)
2. ✅ Clone repo from GitHub
3. ✅ Install dependencies (`pip install -r requirements.txt`)
4. ✅ Create `.env` file with tokens
5. ✅ Run bot with keep-alive script
6. ✅ Bot runs 24/7 for FREE!

**Total time:** 10 minutes  
**Total cost:** $0

---

## 🔗 Useful Commands Cheat Sheet

```bash
# Check if bot is running
ps aux | grep telegram_bot

# View live logs
tail -f bot.log

# Stop bot
pkill -f telegram_bot

# Start bot
cd ~/ess-sdg-chatbot
nohup ./keep_alive.sh > bot.log 2>&1 &

# Check Python version
python3.11 --version

# List installed packages
pip3.11 list --user
```

---

**🎉 Your bot is now running 24/7 for FREE on PythonAnywhere!**

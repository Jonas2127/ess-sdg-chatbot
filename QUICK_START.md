# 🚀 Quick Start Guide

## Run ESS SDG Chatbot in 5 Minutes

### Prerequisites
- Python 3.8+ installed
- 8GB+ RAM
- 10GB free disk space

---

## Step 1: Install Ollama

Download and install from: **https://ollama.com/download**

Then pull the model:
```bash
ollama pull llama3.2:1b
```

---

## Step 2: Install Dependencies

```bash
cd ess-sdg-chatbot
pip install -r requirements.txt
```

---

## Step 3: Download Databases (First Time Only)

```bash
python download_chromadb.py
```

This downloads ~800MB of data. Takes 2-5 minutes.

---

## Step 4: Run the Chatbot

```bash
streamlit run streamlit_app.py
```

Open your browser: **http://localhost:8501**

---

## 🎉 You're Ready!

### Try These Questions:
- "What is the Consumer Price Index?"
- "Show me Ethiopia's population statistics"
- "What is the poverty rate?"
- "Who are you?"

---

## 📖 Need More Help?

- **Full Setup Guide:** See `LOCAL_DEPLOYMENT_GUIDE.md`
- **Project Overview:** See `README.md`
- **Troubleshooting:** See `docs/SETUP.md`

---

## 🛑 To Stop

Press `Ctrl + C` in the terminal

---

## 📱 Mobile Access

1. Find your computer's IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. On your phone (same Wi-Fi): Open `http://YOUR_IP:8501`

---

**That's it!** 🚀

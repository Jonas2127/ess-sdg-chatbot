# 🖥️ Local Deployment Guide

## ESS SDG Chatbot - Run on Your Computer

This guide will help you run the ESS SDG Chatbot on your local machine.

---

## ✅ Why Run Locally?

- **FREE**: No API costs, no subscriptions
- **PRIVATE**: Your data stays on your computer
- **OFFLINE**: Works without internet (after initial setup)
- **FAST**: Direct access to local Ollama LLM
- **FULL FEATURES**: All functionality available

---

## 📋 Prerequisites

Before you start, make sure you have:

- **Windows 10/11**, **macOS**, or **Linux**
- **Python 3.8 or higher**
- **8GB RAM minimum** (16GB recommended)
- **10GB free disk space**
- **Internet connection** (for initial download only)

---

## 🚀 Installation Steps

### Step 1: Install Python

**Check if Python is installed:**
```bash
python --version
```

If not installed, download from: https://www.python.org/downloads/

**Important:** During installation, check "Add Python to PATH"

---

### Step 2: Install Ollama

Ollama is the local LLM that powers the chatbot.

1. **Download Ollama:**
   - Go to: https://ollama.com/download
   - Download for your operating system
   - Run the installer

2. **Install the model:**
```bash
ollama pull llama3.2:1b
```

This will download ~1GB model (one-time download)

3. **Verify Ollama is working:**
```bash
ollama run llama3.2:1b "Hello"
```

You should see a response. Press `/bye` to exit.

---

### Step 3: Download the Project

**Option A: Using Git (Recommended)**
```bash
git clone https://github.com/Jonas2127/ess-sdg-chatbot.git
cd ess-sdg-chatbot
```

**Option B: Download ZIP**
1. Go to: https://github.com/Jonas2127/ess-sdg-chatbot
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Open terminal/command prompt in the extracted folder

---

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install all required Python packages (takes 2-3 minutes).

---

### Step 5: Configure Environment

1. **Copy the example environment file:**
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

2. **Edit `.env` file** (use Notepad or any text editor):
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:1b
```

That's it! No API keys needed for local use.

---

### Step 6: Download Databases (First Time Only)

The chatbot needs two databases:
- **ChromaDB**: Vector database with ESS PDF documents (~800MB)
- **SQLite**: Structured database with SDG indicators (~10MB)

**Run the download script:**
```bash
python download_chromadb.py
```

This downloads from HuggingFace (takes 2-5 minutes depending on your internet speed).

---

### Step 7: Run the Chatbot!

```bash
streamlit run streamlit_app.py
```

The chatbot will open in your browser at: `http://localhost:8501`

**You're ready to go!** 🎉

---

## 💬 Using the Chatbot

### Example Questions to Try:

**ESS Statistics:**
- "What is the current Consumer Price Index?"
- "Show me agricultural production data"
- "What is Ethiopia's population by region?"

**SDG Indicators:**
- "What is the poverty rate in 2021?"
- "Show education enrollment trends"
- "What is the child mortality rate?"

**Meta Questions:**
- "Who are you?"
- "What can you do?"

---

## 🛑 Stopping the Chatbot

In the terminal where you ran `streamlit run`, press:
- **Windows**: `Ctrl + C`
- **macOS/Linux**: `Ctrl + C`

---

## 🔄 Restarting After Computer Reboot

1. **Make sure Ollama is running:**
```bash
# Check if Ollama is running
ollama list

# If not, start it by running any model
ollama run llama3.2:1b "test"
# Then press /bye
```

2. **Navigate to project folder:**
```bash
cd path/to/ess-sdg-chatbot
```

3. **Run the chatbot:**
```bash
streamlit run streamlit_app.py
```

---

## 🆘 Troubleshooting

### "Ollama not found" error

**Solution:** Make sure Ollama is installed and running
```bash
ollama --version
ollama list
```

### "Module not found" errors

**Solution:** Reinstall dependencies
```bash
pip install -r requirements.txt
```

### "ChromaDB not found" error

**Solution:** Re-download databases
```bash
python download_chromadb.py
```

### Slow responses (>30 seconds)

**Possible causes:**
- Computer is busy with other tasks
- Not enough RAM (close other applications)
- Using CPU instead of GPU (expected for this model)

**Tip:** llama3.2:1b is optimized for speed. Responses should be 5-10 seconds.

### Port already in use (8501)

**Solution:** Kill the existing Streamlit process or use a different port
```bash
streamlit run streamlit_app.py --server.port 8502
```

---

## 📊 Performance Tips

1. **Close unnecessary applications** to free up RAM
2. **Use Chrome or Edge browser** for best Streamlit performance
3. **Keep Ollama running** in the background for faster startups
4. **Don't open multiple tabs** of the chatbot (uses more memory)

---

## 🔐 Privacy & Security

✅ **All data stays on your computer**
- No data sent to cloud services
- Ollama runs 100% locally
- Conversations saved locally only

✅ **No API keys required**
- No registration needed
- No tracking or analytics
- Completely private

---

## 🆕 Updating the Chatbot

To get the latest version:

```bash
cd ess-sdg-chatbot
git pull origin main
pip install -r requirements.txt
```

---

## 📁 Data Location

The chatbot stores data in:
```
ess-sdg-chatbot/
├── data/
│   ├── vectorstore/chromadb/     # Vector database (~800MB)
│   ├── sql_database/              # SQLite database (~10MB)
│   └── conversation_history.json  # Your chat history
```

To **reset** everything:
```bash
# Delete databases (will need to re-download)
rm -rf data/vectorstore/chromadb/
rm -rf data/sql_database/

# Delete conversation history
rm data/conversation_history.json
```

---

## 🎓 For Academic Presentations

**To demonstrate the chatbot:**

1. **Start the app** before your presentation:
```bash
streamlit run streamlit_app.py
```

2. **Open in browser**: `http://localhost:8501`

3. **Prepare example questions** (see "Using the Chatbot" section)

4. **Show the features**:
   - Semantic routing (check console for routing decisions)
   - Source display (shows exact documents used)
   - Export functionality (PDF/Word export)

5. **Explain the architecture** using the README.md diagrams

---

## 📞 Support

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review `docs/` folder for detailed documentation
3. Check console output for error messages
4. Ensure all prerequisites are met

---

## ✨ Summary

**One-Time Setup:**
1. Install Python
2. Install Ollama and download llama3.2:1b
3. Clone project and install dependencies
4. Download databases
5. Run: `streamlit run streamlit_app.py`

**Daily Use:**
```bash
streamlit run streamlit_app.py
```

**That's it!** Enjoy your local ESS SDG Chatbot! 🚀

---

**System Requirements Met?** ✅
- Python 3.8+
- Ollama with llama3.2:1b
- 8GB+ RAM
- 10GB free space

**You're ready to run the chatbot!** 🎉

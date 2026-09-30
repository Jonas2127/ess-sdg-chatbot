# Setup Guide

Complete installation and configuration guide for the ESS SDG Chatbot.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Building Databases](#building-databases)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.11 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: 5GB free space
- **Internet**: Required for initial setup and cloud LLM providers

### Required Software

1. **Python 3.11+**
   - Download from: https://www.python.org/downloads/
   - Verify installation: `python --version`

2. **Git** (for cloning repository)
   - Download from: https://git-scm.com/
   - Verify installation: `git --version`

3. **pip** (Python package manager, usually included with Python)
   - Verify installation: `pip --version`

### Optional Software

1. **Ollama** (for local LLM)
   - Download from: https://ollama.ai/
   - Required only if using local LLM
   - After installation, run: `ollama pull llama3.2:1b`

2. **Telegram App** (for bot interface)
   - Only if you want to use Telegram bot

---

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/Jonas2127/ess-sdg-chatbot.git
cd ess-sdg-chatbot
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages (~2GB download, takes 10-15 minutes).

**Note**: If you encounter issues with torch installation, visit: https://pytorch.org/get-started/locally/

### Step 4: Verify Installation

```bash
python -c "import streamlit; import langchain; print('Installation successful!')"
```

If you see "Installation successful!", proceed to configuration.

---

## Configuration

### Step 1: Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### Step 2: Configure LLM Provider

Open `.env` and choose your LLM provider:

**Option A: Groq (Recommended - Fast & Free)**

1. Get API key from: https://console.groq.com/keys
2. Add to `.env`:
```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_key_here
```

**Option B: Gemini (Alternative - Google's API)**

1. Get API key from: https://aistudio.google.com/app/apikey
2. Add to `.env`:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```

**Option C: HuggingFace (Backup Option)**

1. Get token from: https://huggingface.co/settings/tokens
2. Add to `.env`:
```env
LLM_PROVIDER=huggingface
HUGGINGFACE_API_TOKEN=hf_your_token_here
```

**Option D: Ollama (Local - No API Key Needed)**

1. Install Ollama from https://ollama.ai/
2. Pull model: `ollama pull llama3.2:1b`
3. Add to `.env`:
```env
LLM_PROVIDER=ollama
```

### Step 3: Configure Telegram Bot (Optional)

Only if you want to use Telegram interface:

1. Create bot via BotFather: https://t.me/botfather
2. Get bot token
3. Add to `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### Example `.env` File

```env
# LLM Configuration
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_abc123...
GEMINI_API_KEY=AIza...
HUGGINGFACE_API_TOKEN=hf_xyz789...

# Telegram Bot (Optional)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
```

---

## Building Databases

### Overview

Before first use, you need to build two databases:
1. **ChromaDB** (vector database for PDFs)
2. **SQLite** (structured database for Excel files)

### Step 1: Organize Data Files

Ensure your data files are in the correct locations:

```
data/
├── raw/
│   ├── ess_reports/pdfs/        # Place 221 ESS PDFs here
│   ├── afdb_reports/            # Place AfDB PDF here
│   └── un_sdg_excel/            # Place 17 Excel files here
```

**Note**: If you don't have the data files, see [Data Acquisition](#data-acquisition) section.

### Step 2: Run Database Builder

```bash
python build_dual_engine.py
```

This process will:
1. Extract text from all PDFs (~5 minutes)
2. Create chunks with metadata
3. Generate embeddings (~10 minutes)
4. Store in ChromaDB vector database
5. Process Excel files
6. Create SQLite database

**Total time**: 15-20 minutes

**Expected output**:
```
[INFO] Initializing Dual-Engine Build
[LOADING] Engine A (PDF RAG)
[PROCESSING] Processing 221 PDFs...
[OK] Extracted 15,432 chunks
[LOADING] Creating ChromaDB vector store
[OK] ChromaDB ready (805MB)
[LOADING] Engine B (Excel SQL)
[PROCESSING] Processing 17 Excel files...
[OK] SQLite database created (10MB)
[DONE] Build complete!
```

### Step 3: Verify Databases

Check that databases were created:

```bash
# Check ChromaDB
ls -lh data/vectorstore/chromadb/

# Check SQLite  
ls -lh data/sql_database/sdg_ethiopia.db
```

You should see:
- ChromaDB: ~800MB
- SQLite: ~10MB

---

## Running the Application

### Web Interface (Streamlit)

Start the web application:

```bash
streamlit run streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

**First run**: System will initialize RAG components (~30 seconds)

### Telegram Bot

Start the Telegram bot:

```bash
python telegram_bot.py
```

**Note**: Requires `TELEGRAM_BOT_TOKEN` in `.env`

The bot will run continuously. Press Ctrl+C to stop.

### Test Query

Try a sample query to verify setup:

**Web Interface**: Type "What is Ethiopia's poverty rate?" in the chat input

**Telegram Bot**: Send message to your bot: "What is Ethiopia's poverty rate?"

**Expected response**: Answer with source citations from SDG database

---

## Data Acquisition

### ESS PDF Reports

If you don't have the ESS PDF files:

1. **Contact Ethiopian Statistical Service**
   - Website: https://www.statsethiopia.gov.et/
   - Request access to statistical reports

2. **Download from Hugging Face** (if available)
   ```bash
   python download_chromadb.py
   ```

### UN SDG Excel Files

Download from UN Statistics Division:
- Website: https://unstats.un.org/sdgs/dataportal/
- Filter: Ethiopia
- Download all 17 goal files

Place files in: `data/raw/un_sdg_excel/`

Expected filenames: `Goal1.xlsx`, `Goal2.xlsx`, ..., `Goal17.xlsx`

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Error**: `ModuleNotFoundError: No module named 'langchain'`

**Solution**:
```bash
pip install -r requirements.txt
```

#### 2. ChromaDB Build Failed

**Error**: `Error processing PDF: ...`

**Solution**:
- Check PDF files are not corrupted
- Ensure sufficient disk space (5GB free)
- Try processing files in batches

#### 3. LLM Connection Failed

**Error**: `[ERROR] Groq initialization failed`

**Solution**:
- Verify API key is correct
- Check internet connection
- Try alternative provider (Gemini or Ollama)

#### 4. Ollama Not Responding

**Error**: `Connection refused to localhost:11434`

**Solution**:
```bash
# Start Ollama service
ollama serve

# Pull model (in another terminal)
ollama pull llama3.2:1b
```

#### 5. Out of Memory

**Error**: `MemoryError` or system freezing

**Solution**:
- Close other applications
- Reduce batch size in `build_dual_engine.py`
- Use cloud LLM instead of Ollama

#### 6. Streamlit Port Already in Use

**Error**: `Port 8501 is already in use`

**Solution**:
```bash
# Use different port
streamlit run streamlit_app.py --server.port 8502
```

### Debugging Steps

1. **Check Python version**:
   ```bash
   python --version  # Should be 3.11+
   ```

2. **Verify dependencies**:
   ```bash
   pip list | grep langchain
   pip list | grep streamlit
   ```

3. **Test database connections**:
   ```python
   from src.dual_engine_router import LangChainDualEngineRAG
   rag = LangChainDualEngineRAG()
   ```

4. **Check log files**:
   - Streamlit logs: Terminal output
   - Telegram bot logs: Console output

5. **Test individual components**:
   ```python
   # Test PDF engine
   result = rag.query_engine_a("test query")
   print(result)
   
   # Test SQL engine  
   result = rag.query_engine_b("poverty rate")
   print(result)
   ```

### Getting Help

If you encounter issues not covered here:

1. Check GitHub Issues: https://github.com/Jonas2127/ess-sdg-chatbot/issues
2. Review error logs carefully
3. Create a detailed bug report with:
   - Python version
   - Operating system
   - Full error message
   - Steps to reproduce

---

## Performance Optimization

### For Faster Responses

1. **Use Groq or Gemini** (fastest LLMs)
   ```env
   LLM_PROVIDER=groq
   ```

2. **Reduce retrieved documents** (in `langchain_rag.py`):
   ```python
   "k": 10,  # Instead of 15
   ```

3. **Disable re-ranking** (if speed is critical):
   Comment out cross-encoder code

### For Better Quality

1. **Increase retrieved documents**:
   ```python
   "k": 20,
   ```

2. **Use larger LLM model**:
   ```bash
   ollama pull llama3:8b  # Instead of llama3.2:1b
   ```

3. **Enable re-ranking** (if disabled)

### For Lower Memory Usage

1. **Use cloud LLM** (Groq/Gemini) instead of Ollama
2. **Close other applications**
3. **Reduce batch size during database building**

---

## Next Steps

After successful setup:

1. **Read [ARCHITECTURE.md](ARCHITECTURE.md)** to understand system design
2. **Read [DEPLOYMENT.md](DEPLOYMENT.md)** for cloud deployment
3. **Explore the codebase** starting with `langchain_rag.py`
4. **Test with various queries** to understand capabilities
5. **Customize** FAQ, prompts, or UI as needed

---

## Quick Reference

### Directory Structure

```
ess-sdg-chatbot/
├── data/                    # Data files
│   ├── raw/                # Original PDFs and Excel
│   ├── vectorstore/        # ChromaDB database
│   └── sql_database/       # SQLite database
├── src/                    # Source code
├── streamlit_app.py        # Web interface
├── telegram_bot.py         # Bot interface
├── build_dual_engine.py    # Database builder
└── requirements.txt        # Dependencies
```

### Key Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Build databases
python build_dual_engine.py

# Run web app
streamlit run streamlit_app.py

# Run Telegram bot
python telegram_bot.py

# Test system
python -c "from src.dual_engine_router import LangChainDualEngineRAG; rag = LangChainDualEngineRAG()"
```

### Configuration Files

- `.env` - Environment variables and API keys
- `.python-version` - Python version specification
- `requirements.txt` - Python dependencies
- `data/faq_database.json` - FAQ questions

---

## Checklist

Before considering setup complete:

- [ ] Python 3.11+ installed
- [ ] Dependencies installed (`requirements.txt`)
- [ ] `.env` file configured with API keys
- [ ] Data files organized in correct folders
- [ ] Databases built successfully
- [ ] Web interface starts without errors
- [ ] Test query returns valid response
- [ ] Sources are cited correctly
- [ ] Export functionality works (PDF/Word)

If all items checked, setup is complete!

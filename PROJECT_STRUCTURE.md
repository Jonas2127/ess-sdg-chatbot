# 📁 Project Structure

## ESS SDG Chatbot - File Organization

```
ess-sdg-chatbot/
│
├── 📄 README.md                          # Main project documentation
├── 📄 QUICK_START.md                     # 5-minute setup guide
├── 📄 DEPLOYMENT_STATUS.md               # Current deployment status
├── 📄 LOCAL_DEPLOYMENT_GUIDE.md          # Detailed local setup
├── 📄 STREAMLIT_CLOUD_DEPLOYMENT_SOLUTION.md  # Cloud deployment options
├── 📄 GET_GEMINI_KEY_GUIDE.md            # API key setup (if needed)
│
├── 🐍 streamlit_app.py                   # Main Streamlit web application
├── 🐍 telegram_bot.py                    # Telegram bot interface (optional)
│
├── 🔧 download_chromadb.py               # Download databases from HuggingFace
├── 🔧 build_dual_engine.py               # Rebuild databases from scratch
├── 🔧 add_new_pdfs.py                    # Add new PDFs incrementally
├── 🔧 download_pdf_files.py              # Download PDF files
│
├── ⚙️ requirements.txt                    # Python dependencies
├── ⚙️ .env.example                        # Example environment variables
├── ⚙️ .env                                # Your local configuration (not in git)
├── ⚙️ .gitignore                          # Git ignore rules
├── ⚙️ .python-version                     # Python version specification
│
├── 📂 src/                                # Source code modules
│   ├── dual_engine_router/               # Main RAG system
│   │   ├── langchain_rag.py              # Dual-engine RAG with semantic routing
│   │   ├── google_genai_llm.py           # Google Gemini LLM wrapper
│   │   └── __init__.py
│   │
│   ├── engine_a_pdf_rag/                 # PDF document processing
│   │   ├── pdf_processor.py              # PDF text extraction
│   │   ├── chromadb_vectorstore.py       # Vector database management
│   │   └── __init__.py
│   │
│   ├── engine_b_excel_sql/               # Excel to SQL conversion
│   │   ├── excel_processor.py            # Excel data processing
│   │   └── __init__.py
│   │
│   └── export/                           # Conversation export
│       ├── pdf_exporter.py               # PDF export with formatting
│       ├── word_exporter.py              # Word document export
│       └── __init__.py
│
├── 📂 data/                               # Data directory
│   ├── raw/                              # Source data (not in git)
│   │   ├── ess_reports/pdfs/             # 221 ESS PDF documents
│   │   ├── afdb_reports/                 # Policy documents
│   │   └── un_sdg_excel/                 # 17 UN SDG Excel files
│   │
│   ├── vectorstore/chromadb/             # ChromaDB vector store (~800MB, not in git)
│   ├── sql_database/                     # SQLite database (~10MB, not in git)
│   └── conversation_history.json         # Your chat history (not in git)
│
├── 📂 docs/                               # Detailed documentation
│   ├── ARCHITECTURE.md                   # System design and architecture
│   ├── DEPLOYMENT.md                     # Deployment instructions
│   ├── SETUP.md                          # Detailed setup guide
│   └── UTILITIES.md                      # Database maintenance utilities
│
├── 📂 assets/                             # Static assets
│   ├── ess_logo_fixed.png                # ESS logo
│   ├── ethiopia_flag.png                 # Ethiopian flag
│   └── ethiopia_map.png                  # Ethiopia map
│
├── 📂 exports/                            # Generated exports (not in git)
│   └── (PDF and Word exports saved here)
│
├── 📂 .streamlit/                         # Streamlit configuration
│   ├── config.toml                       # Streamlit app config
│   └── secrets.toml.example              # Example secrets file
│
└── 📂 .git/                               # Git repository (hidden)
```

---

## 📦 Key Files Explained

### Core Application Files

| File | Purpose |
|------|---------|
| `streamlit_app.py` | Main web interface - run with `streamlit run streamlit_app.py` |
| `telegram_bot.py` | Optional Telegram bot interface |

### Database Setup Files

| File | Purpose |
|------|---------|
| `download_chromadb.py` | Download pre-built databases from HuggingFace (recommended) |
| `build_dual_engine.py` | Build databases from scratch (~20 minutes) |
| `add_new_pdfs.py` | Add new PDFs incrementally without rebuilding |
| `download_pdf_files.py` | Download PDF source files |

### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Complete project overview and features |
| `QUICK_START.md` | **Start here!** 5-minute setup guide |
| `LOCAL_DEPLOYMENT_GUIDE.md` | Detailed step-by-step local setup |
| `DEPLOYMENT_STATUS.md` | Current system status |
| `STREAMLIT_CLOUD_DEPLOYMENT_SOLUTION.md` | Cloud deployment options |
| `GET_GEMINI_KEY_GUIDE.md` | How to get API keys (if needed) |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Your local settings (NOT in git) |
| `.env.example` | Template for environment variables |
| `requirements.txt` | Python package dependencies |
| `.gitignore` | Files to exclude from git |

---

## 🚀 Quick Usage

### First Time Setup
```bash
# 1. Install Ollama and model
ollama pull llama3.2:1b

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download databases
python download_chromadb.py

# 4. Run app
streamlit run streamlit_app.py
```

### Daily Use
```bash
streamlit run streamlit_app.py
```

---

## 📊 Data Flow

```
User Query
    ↓
streamlit_app.py
    ↓
src/dual_engine_router/langchain_rag.py
    ↓
    ├─→ Engine A: src/engine_a_pdf_rag/ → data/vectorstore/chromadb/
    └─→ Engine B: src/engine_b_excel_sql/ → data/sql_database/
    ↓
Response + Sources
    ↓
Optional: src/export/ → exports/ (PDF/Word)
```

---

## 🗂️ What's NOT in Git

The following are excluded via `.gitignore`:

- ✗ `.env` - Your personal API keys
- ✗ `data/vectorstore/chromadb/` - Vector database (~800MB)
- ✗ `data/sql_database/*.db` - SQL database (~10MB)
- ✗ `data/raw/ess_reports/pdfs/` - Source PDFs
- ✗ `data/conversation_history.json` - Your chat history
- ✗ `exports/*.pdf` - Generated exports
- ✗ `venv/` - Virtual environment
- ✗ `__pycache__/` - Python cache files

**Why?** Large files are hosted on HuggingFace and downloaded when needed.

---

## 🔄 Updating the Project

```bash
# Get latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Re-download databases if needed
python download_chromadb.py
```

---

## 🧹 Clean Install

To start fresh:

```bash
# Remove databases
rm -rf data/vectorstore/chromadb/
rm -rf data/sql_database/

# Remove conversation history
rm data/conversation_history.json

# Re-download
python download_chromadb.py
```

---

## 📖 Documentation Hierarchy

1. **QUICK_START.md** ← **Start here for setup**
2. **README.md** ← Project overview and features
3. **LOCAL_DEPLOYMENT_GUIDE.md** ← Detailed setup instructions
4. **docs/SETUP.md** ← Advanced configuration
5. **docs/ARCHITECTURE.md** ← System design details
6. **docs/UTILITIES.md** ← Database maintenance

---

## 🎯 File Size Reference

| Item | Size | Location |
|------|------|----------|
| Source Code | ~500KB | `src/`, `streamlit_app.py` |
| Dependencies | ~500MB | Installed via pip |
| ChromaDB Vector Store | ~800MB | Downloaded from HuggingFace |
| SQLite Database | ~10MB | Downloaded from HuggingFace |
| Source PDFs | ~200MB | Optional download |
| **Total (with data)** | **~1.5GB** | |

---

## ✨ Clean and Organized!

This structure keeps the project:
- ✅ **Easy to navigate**
- ✅ **Well-documented**
- ✅ **Minimal git repository** (< 10MB)
- ✅ **Fast to clone and setup**
- ✅ **Clear separation** of code, data, and docs

---

**Need help?** Start with `QUICK_START.md`! 🚀

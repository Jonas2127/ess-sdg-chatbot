# ET ESS RAG Bot

**Intelligent Statistical Data Assistant & Policy Analyst for Ethiopian Statistical Service**

An advanced dual-engine RAG (Retrieval-Augmented Generation) chatbot that provides natural language access to Ethiopian Statistical Service data and UN Sustainable Development Goal indicators with semantic query routing, intelligent validation, and accurate source attribution.

---

## 🎯 Key Features

### Intelligent Query Processing
- **Semantic Query Routing**: Automatically routes queries to the correct database using 60% semantic similarity + 40% keyword matching
- **Gibberish Detection**: Validates queries and rejects random keyboard inputs
- **Meta Question Handling**: Responds to questions about the bot itself without searching databases
- **Smart Engine Selection**: Intelligently chooses between PDF search, SQL database, or both based on query intent

### Dual-Engine Architecture
- **Engine A (PDF RAG)**: 221 ESS PDF documents with ChromaDB vector search and cross-encoder re-ranking
- **Engine B (SQL Database)**: 17 UN SDG Excel files (12,037 indicators) with structured SQL queries
- **MMR Retrieval**: Maximal Marginal Relevance for diverse document retrieval
- **Cross-Encoder Re-Ranking**: Improves relevance from 15 to 7 top documents

### Quality Assurance
- **Accurate Source Filtering**: Only shows documents actually used in the answer (30% relevance threshold)
- **Smart Result Combining**: Only combines engines when both have relevant data
- **No False Sources**: Sources cleared when no relevant data found
- **Answer Validation**: Checks LLM responses for actual information content

### Multiple LLM Support
- **Ollama**: Local inference (llama3.2:1b) - No API keys required
- **Groq**: Fast cloud inference (~2-3 seconds)
- **Google Gemini**: Alternative cloud option (~1-2 seconds)
- **HuggingFace**: Backup cloud provider

---

## 📊 Data Sources

### ESS PDF Documents (Engine A)
- **Consumer Price Index (CPI)**: Monthly bulletins and inflation reports
- **Agricultural Surveys**: Crop production, livestock statistics
- **Population Census**: Demographics, regional distribution
- **Business Statistics**: Enterprise surveys, economic indicators
- **Total**: 221 PDF documents

### UN SDG Database (Engine B)
- **All 17 SDG Goals**: Comprehensive indicator coverage
- **12,037 Indicators**: Time-series data (2000-2023)
- **Structured Queries**: Direct SQL access for precise data retrieval
- **Regional Breakdowns**: Where available

### Policy Documents
- **AfDB Reports**: Green growth strategy, GTP II framework
- **Infrastructure Priorities**: Development frameworks

---

## 🏗️ Architecture

```
User Query
    ↓
Query Validation (Gibberish/Meta/Greeting Detection)
    ↓
Semantic + Keyword Analysis (60% + 40%)
    ↓
Smart Routing Decision
    ↓
┌─────────────────────────────┬────────────────────────────┐
│   Engine A: PDF RAG         │   Engine B: SQL Database   │
│   • ChromaDB Vector Search  │   • SQLite Queries         │
│   • MMR Retrieval (15 docs) │   • Structured Data        │
│   • Cross-Encoder Rerank    │   • Direct Access          │
│   • Filter to 7 best docs   │                            │
└─────────────────────────────┴────────────────────────────┘
    ↓
Context Assembly + LLM Generation
    ↓
Source Filtering (Only Used Documents)
    ↓
Response + Accurate Citations
```

### Query Routing Logic

**PDF Engine Selected When:**
- CPI, inflation, price survey keywords
- Agricultural surveys, livestock mentions
- Regional names (Amhara, Oromia, etc.)
- ESS-specific terminology

**SQL Engine Selected When:**
- SDG goal numbers, poverty rate
- Mortality, enrollment indicators
- UN data, global indicators
- Structured indicator queries

**Both Engines When:**
- Query spans both domains
- Ambiguous but relevant to both
- Combined score threshold met

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- 4GB+ RAM
- Ollama installed (for local LLM)

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/Jonas2127/ess-sdg-chatbot.git
cd ess-sdg-chatbot
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup Ollama (No API Keys Required)**
```bash
# Download from https://ollama.com/download
ollama pull llama3.2:1b
```

4. **Configure Environment**
```bash
cp .env.example .env
# Edit .env: Set LLM_PROVIDER=ollama
```

5. **Download Databases** (First Time Only)
```bash
python download_chromadb.py
```

6. **Run Application**
```bash
streamlit run streamlit_app.py
```

Visit `http://localhost:8501`

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# LLM Provider Selection
LLM_PROVIDER=ollama  # Options: ollama, groq, gemini, huggingface

# API Keys (Optional - for cloud providers)
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
HUGGINGFACE_API_TOKEN=your_hf_token

# Telegram Bot (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_token
```

### LLM Provider Comparison

| Provider | Speed | Cost | Use Case |
|----------|-------|------|----------|
| **Ollama** | 5-10s | Free | Local, offline, no API keys |
| **Groq** | 2-3s | Free tier | Production (fastest) |
| **Gemini** | 1-2s | Free tier | Production (alternative) |
| **HuggingFace** | 3-5s | Free tier | Backup option |

---

## 🔍 Usage Examples

### ESS Statistics Queries
```
"What is the current Consumer Price Index?"
"Show me agricultural production by region"
"Give me livestock information for all regions"
"What is Ethiopia's population distribution?"
```

### SDG Indicator Queries
```
"What is the poverty rate in 2021?"
"Show education enrollment trends"
"What is the child mortality rate?"
"Compare health indicators over time"
```

### Policy Questions
```
"What is Ethiopia's green growth strategy?"
"Explain the GTP II framework"
```

### Meta Questions
```
"Who are you?"
"What can you do?"
```

---

## 🛠️ Database Maintenance

### Add New PDFs Incrementally

```bash
# Download new PDFs from HuggingFace
python download_pdf_files.py

# Add them to ChromaDB (fast - only processes new files)
python add_new_pdfs.py
```

### Rebuild Entire Database

```bash
# Remove existing database
rm -rf data/vectorstore/chromadb/

# Rebuild from scratch (15-20 minutes)
python build_dual_engine.py
```

See `docs/UTILITIES.md` for detailed maintenance instructions.

---

## 📁 Project Structure

```
ess-sdg-chatbot/
├── src/
│   ├── dual_engine_router/
│   │   └── langchain_rag.py          # Main RAG system with semantic routing
│   ├── engine_a_pdf_rag/
│   │   ├── pdf_processor.py          # PDF extraction
│   │   └── chromadb_vectorstore.py   # Vector DB management
│   ├── engine_b_excel_sql/
│   │   └── excel_processor.py        # Excel to SQL conversion
│   └── export/
│       ├── pdf_exporter.py           # Conversation export
│       └── word_exporter.py
├── data/
│   ├── raw/
│   │   ├── ess_reports/pdfs/         # 221 ESS PDFs
│   │   ├── afdb_reports/             # Policy documents
│   │   └── un_sdg_excel/             # 17 SDG Excel files
│   ├── vectorstore/chromadb/         # Vector database
│   ├── sql_database/                 # SQLite database
│   └── faq_database.json             # FAQ questions
├── streamlit_app.py                  # Web interface
├── telegram_bot.py                   # Telegram interface
├── download_chromadb.py              # Database downloader
├── add_new_pdfs.py                   # Incremental PDF addition
├── download_pdf_files.py             # PDF file downloader
├── build_dual_engine.py              # Full database builder
└── requirements.txt                  # Python dependencies
```

---

## 🧪 Testing

### Test Validation
```python
# Should reject
"hhj"  → Gibberish detection
"hi"   → Greeting response

# Should answer
"who are you?"              → Meta question (no DB search)
"what is CPI?"              → Routes to PDF
"what is poverty rate?"     → Routes to SQL
"population statistics"     → Routes intelligently
```

### Test Routing
Check console output for routing decisions:
```
[SEMANTIC] PDF similarity: 7.85, SQL similarity: 3.21
[ROUTING] PDF score: 6.28, SQL score: 2.53
[INFO] Query type: pdf
```

---

## 🎨 Features Implemented

### Query Processing
- ✅ Gibberish detection (vowel ratio analysis)
- ✅ Meta question handling
- ✅ Greeting detection
- ✅ Semantic similarity routing
- ✅ Keyword matching
- ✅ Combined scoring (60/40 split)

### Retrieval
- ✅ MMR retrieval (diverse results)
- ✅ Cross-encoder re-ranking
- ✅ Source filtering (only used docs)
- ✅ Relevance threshold (30%)

### Answer Generation
- ✅ Context-aware prompting
- ✅ Answer validation
- ✅ Smart result combining
- ✅ Source attribution

### Quality Control
- ✅ No false positives on "no data"
- ✅ Accurate source display
- ✅ Empty source clearing
- ✅ Response time tracking

---

## 📝 Export Functionality

Export conversations to:
- **PDF**: Professional reports with ESS logo
- **Word**: Editable documents for further analysis

---

## 🌐 Deployment

### Streamlit Cloud
Deployed at: `https://ess-rag-chatbot.streamlit.app`

See `docs/DEPLOYMENT.md` for deployment instructions.

### Telegram Bot
24/7 access via Telegram interface.

See `TELEGRAM_QUICK_START.md` for setup instructions.

---

## 🤝 Contributing

This is an academic project for Ethiopian Statistical Service.

**Author**: Yonas Abiyu Gion  
**Institution**: Ethiopian Statistical Service  
**Repository**: https://github.com/Jonas2127/ess-sdg-chatbot

---

## 📚 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Detailed system design
- **[SETUP.md](docs/SETUP.md)** - Complete installation guide
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Cloud deployment
- **[UTILITIES.md](docs/UTILITIES.md)** - Database maintenance

---

## 🔧 Troubleshooting

### Common Issues

**Q: Chatbot says "No relevant data" for valid questions**  
A: Check console for routing decision. Query might be routed to wrong engine.

**Q: Slow responses (>10 seconds)**  
A: Using Ollama locally. Switch to Groq/Gemini for 2-3 second responses.

**Q: "API key invalid" errors**  
A: Get fresh API keys or switch to Ollama (no keys required).

**Q: Sources showing unrelated documents**  
A: Fixed in current version - source filtering uses 30% relevance threshold.

---

## 📊 System Performance

- **Query Validation**: <0.01s
- **Semantic Routing**: ~0.5s
- **Document Retrieval**: 1-2s
- **LLM Generation**: 2-10s (depends on provider)
- **Total Response**: 3-15s

**Database Statistics:**
- ChromaDB: ~15,000 document chunks
- SQLite: 12,037 SDG indicators
- Embedding Model: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)

---

## 🎓 Academic Context

This chatbot demonstrates:
- Advanced RAG architecture
- Semantic search and routing
- Multi-modal data integration
- Quality control mechanisms
- Production-ready deployment

Suitable for academic presentation and demonstration.

---

## 📄 License

[Specify your license]

---

## 🙏 Acknowledgments

- Ethiopian Statistical Service for data
- UN Statistics Division for SDG indicators
- African Development Bank for policy documents
- Open-source community (LangChain, ChromaDB, Streamlit)

---

**Ready for Academic Demonstration** ✨

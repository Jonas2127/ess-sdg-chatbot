# ESS SDG Dual-Engine RAG Chatbot

A retrieval-augmented generation (RAG) chatbot that provides natural language access to Ethiopian Statistical Service data and UN Sustainable Development Goal indicators.

## Overview

This project implements a dual-engine RAG system that processes both unstructured (PDF documents) and structured (Excel spreadsheets) data sources. Users can ask questions in natural language and receive accurate answers with source citations.

### Key Features

- **Dual-Engine Architecture**: Separate engines for unstructured and structured data
- **221 ESS PDF Reports**: Demographics, agriculture, CPI, business statistics
- **17 UN SDG Excel Files**: 12,037 indicators across all SDG goals
- **Source Citation**: All answers include references to source documents
- **Multiple Interfaces**: Web UI (Streamlit) and Telegram bot
- **Export Functionality**: Save conversations as PDF or Word documents

## Architecture

```
User Query
    ↓
Query Router (determines engine)
    ↓
┌─────────────────────┬──────────────────────┐
│   Engine A          │   Engine B           │
│   PDF RAG           │   Excel SQL          │
│                     │                      │
│   ChromaDB          │   SQLite             │
│   Vector Search     │   SQL Queries        │
│   15 docs retrieved │   Structured Data    │
│   Re-ranked to 7    │   Direct Queries     │
└─────────────────────┴──────────────────────┘
    ↓
Context Assembly
    ↓
LLM (Groq/Gemini/Ollama/HuggingFace)
    ↓
Response + Sources
```

### How It Works

1. **Document Processing** (offline):
   - PDFs extracted and split into chunks
   - Text embedded using sentence-transformers
   - Stored in ChromaDB vector database
   - Excel files converted to SQLite database

2. **Query Processing** (runtime):
   - User query analyzed to determine data source
   - Relevant documents/data retrieved
   - Context assembled and passed to LLM
   - Response generated with source citations

3. **Quality Controls**:
   - Cross-encoder re-ranking for relevance
   - Source filtering (only show used documents)
   - Answer validation against sources
   - Gibberish/greeting detection

## Data Sources

### ESS PDF Documents (Engine A)
- **Consumer Price Index (CPI)** reports (monthly bulletins)
- **Agricultural surveys** (crop production, livestock)
- **Population census** data
- **Business statistics**
- Total: 221 PDF documents

### UN SDG Database (Engine B)
- **17 SDG Goals** with associated indicators
- **12,037 indicators** across all goals
- **Time-series data** from 2000-2023
- **Regional breakdowns** where available

### AfDB Policy Documents
- **Green growth strategy**
- **GTP II alignment framework**
- **Infrastructure priorities**

## Technology Stack

### Core Framework
- **LangChain**: RAG orchestration and chaining
- **ChromaDB**: Vector database for semantic search
- **SQLite**: Structured data queries
- **Sentence Transformers**: Text embeddings (all-MiniLM-L6-v2)

### LLM Providers (configurable)
- **Ollama**: Local LLM (Llama 3.2-1B)
- **Groq**: Cloud API (fastest)
- **Gemini**: Google's API
- **HuggingFace**: Alternative cloud option

### User Interfaces
- **Streamlit**: Web application
- **Telegram**: Bot interface for 24/7 access

### Additional Libraries
- **pdfplumber**: PDF text extraction
- **pandas**: Data manipulation
- **ReportLab**: PDF export
- **python-docx**: Word export

## Project Structure

```
ess-sdg-chatbot/
├── src/
│   ├── dual_engine_router/
│   │   ├── langchain_rag.py       # Main RAG system
│   │   └── google_genai_llm.py    # Custom Gemini wrapper
│   ├── engine_a_pdf_rag/
│   │   ├── pdf_processor.py       # PDF extraction
│   │   └── chromadb_vectorstore.py # Vector DB management
│   ├── engine_b_excel_sql/
│   │   └── excel_processor.py     # Excel to SQL conversion
│   └── export/
│       ├── pdf_exporter.py        # Conversation export
│       └── word_exporter.py
├── data/
│   ├── raw/
│   │   ├── ess_reports/pdfs/      # ESS PDF files
│   │   ├── afdb_reports/          # AfDB documents
│   │   └── un_sdg_excel/          # SDG Excel files
│   ├── vectorstore/chromadb/      # Vector database
│   ├── sql_database/              # SQLite database
│   └── faq_database.json          # FAQ questions
├── docs/
│   ├── ARCHITECTURE.md            # System design details
│   ├── SETUP.md                   # Installation guide
│   └── DEPLOYMENT.md              # Cloud deployment
├── assets/                         # Logos and images
├── streamlit_app.py               # Web interface
├── telegram_bot.py                # Telegram interface
├── build_dual_engine.py           # Database builder
├── download_chromadb.py           # HuggingFace integration
├── requirements.txt               # Python dependencies
└── .env.example                   # Environment template
```

## Installation

See [docs/SETUP.md](docs/SETUP.md) for detailed installation instructions.

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jonas2127/ess-sdg-chatbot.git
   cd ess-sdg-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Build databases** (first time only)
   ```bash
   python build_dual_engine.py
   ```

5. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

## Usage

### Web Interface

```bash
streamlit run streamlit_app.py
```

Open your browser to `http://localhost:8501`

### Telegram Bot

```bash
python telegram_bot.py
```

Chat with the bot on Telegram after configuring `TELEGRAM_BOT_TOKEN`

### Example Queries

**ESS Statistics:**
- "What is the current Consumer Price Index?"
- "Show me agricultural production by region"
- "What is Ethiopia's population?"

**SDG Indicators:**
- "What is the poverty rate in 2021?"
- "Show education enrollment trends"
- "Compare health indicators over time"

**Policy Questions:**
- "What is Ethiopia's green growth strategy?"
- "Explain the GTP II framework"

## Configuration

### Environment Variables

Create a `.env` file with:

```env
# LLM Provider (ollama, groq, gemini, huggingface)
LLM_PROVIDER=groq

# API Keys
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
HUGGINGFACE_API_TOKEN=your_hf_token_here

# Telegram (optional)
TELEGRAM_BOT_TOKEN=your_telegram_token_here
```

### LLM Provider Selection

The system supports multiple LLM providers. Configure in `.env`:

| Provider | Speed | Cost | Use Case |
|----------|-------|------|----------|
| **Ollama** | Slow (15-30s) | Free | Local development |
| **Groq** | Fast (2-3s) | Free tier | Production (recommended) |
| **Gemini** | Fast (1-2s) | Free tier | Production (alternative) |
| **HuggingFace** | Medium (3-5s) | Free tier | Backup option |

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for deployment instructions.

### Streamlit Cloud

The application is deployed at: https://ess-rag-chatbot.streamlit.app

For deploying your own instance:
1. Push code to GitHub
2. Upload large files to Hugging Face
3. Configure Streamlit Cloud
4. Add secrets (API keys)

## Development

### Building Databases

To rebuild the vector and SQL databases:

```bash
python build_dual_engine.py
```

This will:
1. Process all PDF files (221 documents)
2. Create ChromaDB vector store
3. Convert Excel files to SQLite
4. Generate statistics

Takes approximately 15-20 minutes.

### Database Maintenance

**Adding new PDFs incrementally:**

```bash
# Download new PDFs from HuggingFace
python download_pdf_files.py

# Add them to the database (much faster than rebuilding)
python add_new_pdfs.py
```

**See [docs/UTILITIES.md](docs/UTILITIES.md) for detailed instructions on:**
- Downloading PDFs from HuggingFace
- Adding new documents to the database
- Syncing with remote repositories
- Troubleshooting common issues

### Testing

```python
from src.dual_engine_router import LangChainDualEngineRAG

rag = LangChainDualEngineRAG()
result = rag.query("What is Ethiopia's poverty rate?")
print(result['answer'])
```

## Limitations

- **Language**: Primarily supports English queries (Amharic support is experimental)
- **Data Coverage**: Limited to documents provided (2000-2023 for SDG data)
- **LLM Constraints**: Responses depend on LLM capabilities and context window
- **Update Frequency**: Manual updates required for new data

## Contributing

This is an academic project. For questions or suggestions, please contact:

- **Author**: Yonas Abiyu Gion
- **Institution**: Ethiopian Statistical Service
- **Repository**: https://github.com/Jonas2127/ess-sdg-chatbot

## License

[Specify your license]

## Acknowledgments

- Ethiopian Statistical Service for providing data
- UN Statistics Division for SDG indicators
- African Development Bank for policy documents
- Open-source community for tools and libraries

## References

- LangChain Documentation: https://python.langchain.com/
- ChromaDB Documentation: https://docs.trychroma.com/
- Sentence Transformers: https://www.sbert.net/
- Streamlit: https://streamlit.io/

---

**For detailed documentation, see:**
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design
- [SETUP.md](docs/SETUP.md) - Installation guide
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Cloud deployment
- [UTILITIES.md](docs/UTILITIES.md) - Database maintenance utilities

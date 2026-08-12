# 🇪🇹 ESS Dual-Engine RAG Chatbot

**Intelligent Statistical Data Assistant & Policy Analyst for Ethiopian Statistical Service**

## 🎯 What is This?

A Dual-Engine Retrieval-Augmented Generation (RAG) chatbot that processes:
- **221 ESS PDF Reports** (Price bulletins, surveys, census data)
- **1 AfDB Policy Document** (Strategic planning & green growth)
- **17 UN SDG Excel Files** (Structured indicators for all 17 goals)

## 🏗️ Architecture

### Engine A: PDF RAG (Unstructured Documents)
- Extracts text from 222 PDFs (ESS + AfDB)
- Handles Amharic/English mixed content
- Stores in ChromaDB vector database
- Answers: "What does the latest CPI say?" "Show Ethiopia's green growth strategy"

### Engine B: Excel SQL (Structured Data)
- Converts 17 UN SDG Excel files to SQLite database
- Executes SQL queries for exact numbers
- Answers: "What is poverty rate in 2021?" "Compare education data 2015 vs 2020"

### Router
- Automatically detects which engine to use
- Routes questions to PDF RAG or Excel SQL
- Cites exact sources

## 📥 Quick Start

### 1. Organize Your Files
```bash
data/raw/ess_reports/pdfs/     ← Put 221 ESS PDFs here
data/raw/afdb_reports/         ← Put 1 AfDB PDF here
data/raw/un_sdg_excel/         ← Put 17 UN SDG Excel files here
```

### 2. Build the Databases
```bash
python build_dual_engine.py
```

### 3. Run the Chatbot
```bash
streamlit run streamlit_app.py
```

## 🛠️ Technical Stack

- **LLM:** Llama-3.1-8B (via Ollama - FREE)
- **Vector DB:** ChromaDB
- **SQL DB:** SQLite
- **Framework:** LangChain
- **UI:** Streamlit
- **Embeddings:** sentence-transformers/all-MiniLM-L6-v2

## 💰 Cost

**$0 - 100% FREE** ✅

All tools and models are open-source and run locally.

## 📚 Documentation

See `FOLDER_STRUCTURE.md` for detailed folder organization guide.

---

**Status:** Environment cleaned, folders created, waiting for 222 files to be organized.

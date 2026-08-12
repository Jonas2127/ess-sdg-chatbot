# 🚀 QUICK START GUIDE

## ✅ Prerequisites Complete

- ✅ 221 ESS PDFs in `data/raw/ess_reports/pdfs/`
- ✅ 1 AfDB PDF in `data/raw/afdb_reports/`
- ✅ 17 UN SDG Excel files in `data/raw/un_sdg_excel/`
- ✅ Ollama installed with Llama 3.1 model
- ✅ All Python packages installed

---

## 📋 Build the Dual-Engine System (One Command!)

```bash
python build_dual_engine.py
```

**This will:**
1. Extract text from 222 PDFs (ESS + AfDB)
2. Create 10,000+ searchable chunks
3. Build ChromaDB vector store (Engine A)
4. Convert 17 Excel files to SQL database (Engine B)
5. Create indexes for fast queries

**Estimated time:** 10-20 minutes (depending on your computer)

---

## 🎯 Run the Chatbot

After build completes:

```bash
streamlit run streamlit_app.py
```

Then open your browser to: `http://localhost:8501`

---

## 💬 Example Questions to Ask

### Engine A Questions (PDF Documents):
- "What does the latest CPI bulletin say?"
- "Show price trends from ESS reports"
- "What is Ethiopia's green growth strategy according to AfDB?"
- "Tell me about agricultural survey results"
- "What are the main findings from population census?"

### Engine B Questions (SQL/Structured Data):
- "What is Ethiopia's poverty rate in 2021?"
- "Show SDG Goal 4 education indicators"
- "Compare 2015 vs 2020 data for gender equality"
- "List all indicators for SDG Goal 8"
- "What is the trend in health indicators?"

### Mixed Questions (Both Engines):
- "How is Ethiopia doing on SDG goals based on reports and data?"
- "Compare policy targets with actual SDG indicators"

---

## 🔧 Troubleshooting

### If build fails:

1. **Check files are in correct folders:**
   ```bash
   dir data\raw\ess_reports\pdfs\*.pdf
   dir data\raw\afdb_reports\*.pdf
   dir data\raw\un_sdg_excel\*.xlsx
   ```

2. **Check Ollama is running:**
   ```bash
   ollama list
   ```

3. **Check Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

### If chatbot doesn't start:

1. **Make sure build completed successfully**
2. **Check databases exist:**
   ```bash
   dir data\vectorstore\chromadb
   dir data\sql_database\sdg_ethiopia.db
   ```

3. **Restart Streamlit:**
   ```bash
   streamlit run streamlit_app.py
   ```

---

## 📊 What the Build Script Does

### Engine A: PDF RAG System
```
221 ESS PDFs + 1 AfDB PDF
        ↓
  Extract Text
  (with tables & footnotes)
        ↓
    Chunk Text
  (500-800 words each)
        ↓
  Generate Embeddings
  (multilingual model)
        ↓
   Store in ChromaDB
  (searchable vector DB)
```

### Engine B: Excel SQL System
```
17 UN SDG Excel Files
        ↓
  Load & Normalize
  (clean column names)
        ↓
 Combine into DataFrame
        ↓
  Convert to SQLite
  (with indexes)
        ↓
   Ready for SQL Queries
```

---

## 🎉 You're Ready!

Once you see:
```
🎉 DUAL-ENGINE SYSTEM READY!
Next step: Run the chatbot
   streamlit run streamlit_app.py
```

You can start using the chatbot immediately!

---

## 💰 Cost

**$0 - Everything is FREE!** ✅

- Ollama (FREE)
- Llama 3.1 (FREE)
- ChromaDB (FREE)
- SQLite (FREE)
- All Python packages (FREE & Open Source)

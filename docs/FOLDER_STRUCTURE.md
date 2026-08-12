# 📁 DUAL-ENGINE SYSTEM FOLDER STRUCTURE

## ✅ CLEAN ENVIRONMENT - ALL OLD DATA REMOVED

All previous data, databases, old scripts, and documentation have been deleted.

---

## 📂 NEW FOLDER STRUCTURE

```
ESSFINALPROJECT/
│
├── data/
│   ├── raw/                              # Raw source files
│   │   ├── ess_reports/
│   │   │   └── pdfs/                     ← PUT YOUR 221 ESS PDF FILES HERE
│   │   ├── afdb_reports/                 ← PUT YOUR 1 AfDB PDF FILE HERE
│   │   └── un_sdg_excel/                 ← PUT YOUR 17 UN SDG EXCEL FILES HERE
│   │
│   ├── vectorstore/
│   │   └── chromadb/                     # Engine A vector database (auto-generated)
│   │
│   └── sql_database/                     # Engine B SQL database (auto-generated)
│
├── src/
│   ├── engine_a_pdf_rag/                 # Engine A: PDF processing & RAG
│   ├── engine_b_excel_sql/               # Engine B: Excel to SQL conversion
│   ├── dual_engine_router/               # Router: decides which engine to use
│   └── rag/                              # Existing RAG components (kept)
│
├── assets/                               # Logo & images (kept)
├── .streamlit/                           # Streamlit config (kept)
├── .env                                  # API keys (kept)
├── streamlit_app.py                      # Main chatbot interface (updated)
└── requirements.txt                      # Dependencies (will be updated)
```

---

## 📥 STEP-BY-STEP: WHERE TO PUT YOUR FILES

### 1. ESS PDF Reports (221 files)
**Folder:** `data/raw/ess_reports/pdfs/`

**What to put here:**
- CPI Bulletins
- Agricultural Surveys
- Household Income/Expenditure Surveys
- Population Census Reports
- Business Surveys
- Any other ESS PDF reports

**Example:**
```
data/raw/ess_reports/pdfs/
├── ESS_CPI_Bulletin_2023.pdf
├── Agricultural_Survey_2022.pdf
├── Household_Income_Survey_2021.pdf
├── Population_Census_2020.pdf
└── ... (217 more PDFs)
```

---

### 2. AfDB Policy Document (1 file)
**Folder:** `data/raw/afdb_reports/`

**What to put here:**
- Ethiopian 2016-2020 Country Strategy Paper

**Example:**
```
data/raw/afdb_reports/
└── Ethiopian_2016-2020_Country_Strategy_Paper.pdf
```

---

### 3. UN SDG Excel Files (17 files)
**Folder:** `data/raw/un_sdg_excel/`

**What to put here:**
- Goal1.xlsx (No Poverty)
- Goal2.xlsx (Zero Hunger)
- Goal3.xlsx (Good Health)
- ... through Goal17.xlsx

**Example:**
```
data/raw/un_sdg_excel/
├── Goal1.xlsx
├── Goal2.xlsx
├── Goal3.xlsx
├── Goal4.xlsx
├── Goal5.xlsx
├── Goal6.xlsx
├── Goal7.xlsx
├── Goal8.xlsx
├── Goal9.xlsx
├── Goal10.xlsx
├── Goal11.xlsx
├── Goal12.xlsx
├── Goal13.xlsx
├── Goal14.xlsx
├── Goal15.xlsx
├── Goal16.xlsx
└── Goal17.xlsx
```

---

## 🚀 NEXT STEPS AFTER ORGANIZING FILES

Once you've put all 222 files in their folders:

1. **Tell me you're ready**
2. **I will create:**
   - Engine A: PDF text extraction & vectorization script
   - Engine B: Excel to SQL conversion script
   - Dual-Engine Router: Auto-routes questions to correct engine
   - Processing pipeline to build both databases

3. **You run one command:**
   ```bash
   python build_dual_engine.py
   ```

4. **Chatbot ready to use!**

---

## 📊 DUAL-ENGINE ARCHITECTURE

### Engine A: PDF RAG (Unstructured Documents)
- **Input:** 221 ESS PDFs + 1 AfDB PDF
- **Processing:** 
  - Extract text with pdfplumber
  - Handle Amharic/English mixed content
  - Preserve tables & footnotes
  - Chunk into 500-800 word segments
- **Storage:** ChromaDB vector store
- **Search:** Hybrid (Dense vector + BM25 keyword)
- **Use Cases:** 
  - "What does the latest CPI bulletin say?"
  - "Show price trends from ESS reports"
  - "What is Ethiopia's green growth strategy?"

### Engine B: Excel SQL (Structured Data)
- **Input:** 17 UN SDG Excel files
- **Processing:**
  - Convert to unified SQLite database
  - Normalize tables and relationships
  - Create indexes for fast queries
- **Storage:** SQLite database
- **Search:** SQL queries via Pandas agent
- **Use Cases:**
  - "What is Ethiopia's poverty rate in 2021?"
  - "Show SDG Goal 4 indicators over time"
  - "Compare education enrollment 2015 vs 2020"

### Router: Auto-Detection
- Analyzes user question
- Routes to Engine A (PDFs) or Engine B (SQL)
- Merges results when needed
- Cites exact sources

---

## 🎯 CURRENT STATUS

✅ Old data cleaned  
✅ Folders created  
✅ Interface updated  
⏳ **WAITING:** You to organize 222 files into folders  
⏳ **NEXT:** Create dual-engine processing scripts

---

**Ready when you are!** 🚀

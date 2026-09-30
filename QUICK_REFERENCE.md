# ET ESS RAG Bot - Quick Reference Guide

**For Academic Demonstration and Daily Use**

---

## 🚀 Quick Start

### Start the Application
```powershell
cd c:\Users\HP\ess-sdg-chatbot
python -m streamlit run streamlit_app.py
```

### Access
- **Local**: http://localhost:8501
- **Cloud**: https://ess-rag-chatbot.streamlit.app

---

## 💡 How to Use

### Good Questions (What Works)
```
✅ "What is the Consumer Price Index?"
✅ "Show me livestock production by region"
✅ "What is Ethiopia's poverty rate in 2021?"
✅ "Give me SDG Goal 1 indicators"
✅ "What is the population growth rate?"
✅ "Explain green growth strategy"
```

### Special Queries
```
🤖 "Who are you?" → Self-introduction
👋 "Hello" → Greeting response
❌ "hhj" → Gibberish rejected
```

---

## 🎯 System Features

### What Makes It Smart

1. **Validates Queries** - Rejects gibberish, handles greetings
2. **Routes Intelligently** - Sends query to right database (PDF/SQL/Both)
3. **Filters Sources** - Only shows documents actually used
4. **Combines Smartly** - Only combines when both databases have data

### Engines

**Engine A (PDF)**: 221 ESS documents
- CPI reports, agricultural surveys, census data

**Engine B (SQL)**: 12,037 SDG indicators  
- Poverty, health, education indicators

---

## 🔧 Troubleshooting

### Problem: Slow Responses (>10 seconds)

**Cause**: Using Ollama (local LLM)

**Solutions**:
1. Get Groq API key: https://console.groq.com/keys
2. Update `.env`: `LLM_PROVIDER=groq`
3. Add key: `GROQ_API_KEY=your_key`
4. Restart: `python -m streamlit run streamlit_app.py`

**Result**: 2-3 second responses instead of 10

### Problem: "No relevant data" for valid questions

**Check**: Console output for routing decision
```
[ROUTING] PDF score: 6.28, SQL score: 2.53
[INFO] Query type: pdf
```

**Solutions**:
- Rephrase with clearer keywords
- Add domain-specific terms (CPI, SDG, etc.)

### Problem: Sources showing unrelated documents

**Fixed**: Current version filters sources (30% relevance threshold)

If still seeing: File a bug report

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Query Validation | <0.01s |
| Routing Decision | ~0.5s |
| Document Retrieval | 1-2s |
| Answer Generation | 2-10s |
| **Total** | **3-15s** |

---

## 🎓 For Your Advisor

### Key Points to Explain

**1. Why Dual-Engine?**
> "Different data types need different approaches. PDFs need semantic search, structured data needs SQL queries."

**2. How Does Routing Work?**
> "The system uses 60% semantic similarity and 40% keyword matching to intelligently route queries to the right database."

**3. Why Is It Accurate?**
> "We use cross-encoder re-ranking and source filtering to ensure only relevant, actually-used documents are shown."

**4. What Makes It Production-Ready?**
> "Multi-layer validation, accurate source attribution, smart result combining, and support for multiple LLM providers."

### Demo Flow

```
1. Show System: "This is the ET ESS RAG Bot"

2. Demo Validation: 
   Input: "hhj" 
   → Shows gibberish rejection

3. Demo Meta Questions:
   Input: "who are you?"
   → Shows self-description, no DB search

4. Demo PDF Engine:
   Input: "what is CPI?"
   → Routes to PDF, shows ESS documents

5. Demo SQL Engine:
   Input: "what is poverty rate?"
   → Routes to SQL, shows SDG data

6. Demo Source Accuracy:
   → Show sources match the answer

7. Demo Export:
   → Generate PDF report
```

---

## 🔄 Maintenance

### Add New PDFs

```bash
# Download new files from HuggingFace
python download_pdf_files.py

# Add to database (only processes new files)
python add_new_pdfs.py
```

**Time**: 30 seconds per PDF

### Rebuild Database (Full)

```bash
# Remove old database
rm -rf data/vectorstore/chromadb/

# Rebuild everything
python build_dual_engine.py
```

**Time**: 15-20 minutes

---

## 📝 Environment Setup

### `.env` File
```env
# Required
LLM_PROVIDER=ollama  # or groq, gemini

# Optional (for cloud LLMs)
GROQ_API_KEY=your_key
GEMINI_API_KEY=your_key
HUGGINGFACE_API_TOKEN=your_token
```

### First Time Setup
```bash
# Install Ollama
# Download from: https://ollama.com/download

# Pull model
ollama pull llama3.2:1b

# Download databases
python download_chromadb.py

# Run app
python -m streamlit run streamlit_app.py
```

---

## 📚 Documentation

- **README.md** - Full system overview
- **IMPROVEMENTS_LOG.md** - All improvements made
- **ARCHITECTURE.md** - System design
- **SETUP.md** - Installation guide
- **UTILITIES.md** - Database maintenance

---

## 🆘 Quick Commands

```bash
# Start app
python -m streamlit run streamlit_app.py

# Check Ollama
ollama list

# Download databases
python download_chromadb.py

# Add new PDFs
python add_new_pdfs.py

# Rebuild database
python build_dual_engine.py

# Run Telegram bot
python telegram_bot.py
```

---

## 📞 Support

**Author**: Yonas Abiyu Gion  
**Institution**: Ethiopian Statistical Service  
**GitHub**: https://github.com/Jonas2127/ess-sdg-chatbot

---

## ✅ Pre-Demo Checklist

- [ ] Application starts without errors
- [ ] Test query: "what is CPI?" returns data
- [ ] Test query: "hhj" shows gibberish rejection
- [ ] Test query: "who are you?" shows intro
- [ ] Sources match the answer content
- [ ] Export to PDF works
- [ ] Response time acceptable (<15s)
- [ ] Ollama running (check `ollama list`)

---

**Last Updated**: September 30, 2026  
**Version**: 2.0 Production

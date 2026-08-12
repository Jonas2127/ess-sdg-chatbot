# 🚀 Streamlit Cloud Deployment Guide
## ET ESS RAG Bot - 24/7 Production Deployment

---

## 📋 Overview

This guide will help you deploy the ET ESS RAG Bot to **Streamlit Community Cloud** for 24/7 availability.

**Deployment Type:** Streamlit Community Cloud (Free Tier)
- ✅ 1 GB RAM
- ✅ 1 CPU core  
- ✅ Always-on (24/7)
- ✅ Free SSL certificate
- ✅ Automatic GitHub sync
- ✅ Custom domain support

---

## 📦 Pre-Deployment Checklist

### ✅ 1. Your System Uses:
- **Engine A:** ChromaDB vector store (221 PDFs)
- **Engine B:** SQLite database (17 Excel files)
- **LLM:** Groq API (FREE, fast responses 1-2s)
- **Total Data:** ~500 MB (ChromaDB + SQLite + PDFs)

### ✅ 2. Critical Files Required in Git:
```
✓ streamlit_app.py
✓ requirements.txt
✓ .streamlit/config.toml
✓ src/ (all Python modules)
✓ data/vectorstore/chromadb/ (vector database - MUST include)
✓ data/sql_database/sdg_ethiopia.db (SQL database - MUST include)
✓ data/raw/un_sdg_excel/ (Excel files for downloads)
✓ assets/ (logos and images)
```

### ⚠️ 3. Files to EXCLUDE from Git (.gitignore):
```
✗ .env (secrets - configure in Streamlit Cloud UI)
✗ data/conversation_history.json (user-generated)
✗ exports/*.pdf, *.docx (user-generated)
✗ __pycache__/ (Python cache)
```

---

## 🔧 Step 1: Prepare Your Repository

### 1.1 Update .gitignore

Ensure your `.gitignore` does NOT exclude these critical files:

```bash
# Remove or comment out these lines if present:
# data/vectorstore/chromadb/
# data/sql_database/*.db
```

**Important:** ChromaDB and SQLite database MUST be in Git for deployment!

### 1.2 Update requirements.txt

Remove Ollama dependency (not needed - using Groq):

```txt
# Remove or comment out:
# ollama>=0.4.4
```

### 1.3 Create .streamlit/secrets.toml Template

This file shows what secrets are needed (DO NOT commit actual values):

```toml
# .streamlit/secrets.toml.example
# Copy this to Streamlit Cloud secrets section

GROQ_API_KEY = "your-groq-api-key-here"
LLM_PROVIDER = "groq"
```

### 1.4 Verify Data Files Exist

Run this check:

```bash
# Windows PowerShell
Test-Path "data\vectorstore\chromadb\*"  # Should return True
Test-Path "data\sql_database\sdg_ethiopia.db"  # Should return True
Get-ChildItem "data\raw\un_sdg_excel\*.xlsx" | Measure-Object  # Should show 17 files
```

---

## 📤 Step 2: Push to GitHub

### 2.1 Initialize Git (if not done)

```bash
git init
git add .
git commit -m "Initial commit - ET ESS RAG Bot for Streamlit Cloud"
```

### 2.2 Create GitHub Repository

1. Go to https://github.com/new
2. Create repository: `ess-rag-bot` (public or private)
3. **DO NOT** initialize with README (you already have one)

### 2.3 Push Code

```bash
# Replace with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/ess-rag-bot.git
git branch -M main
git push -u origin main
```

### 2.4 Verify Upload

Check GitHub repository to ensure these exist:
- ✅ `data/vectorstore/chromadb/` (should have multiple files)
- ✅ `data/sql_database/sdg_ethiopia.db` (should be present)
- ✅ `streamlit_app.py`
- ✅ `requirements.txt`

---

## 🌐 Step 3: Deploy to Streamlit Cloud

### 3.1 Sign Up for Streamlit Cloud

1. Go to https://share.streamlit.io
2. Sign in with **GitHub account**
3. Authorize Streamlit to access your repositories

### 3.2 Create New App

1. Click **"New app"** button
2. Select your repository: `YOUR_USERNAME/ess-rag-bot`
3. Branch: `main`
4. Main file path: `streamlit_app.py`
5. App URL: Choose custom URL like `ess-rag-ethiopia`

**Result:** Your app will be at: `https://ess-rag-ethiopia.streamlit.app`

### 3.3 Configure Secrets

**CRITICAL:** Add secrets before deploying!

1. Click **"Advanced settings"** → **"Secrets"**
2. Add this configuration format:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
LLM_PROVIDER = "groq"
```

**Security Note:** 
- Get your Groq API key from https://console.groq.com/keys
- Never commit API keys to Git repositories
- Replace `your_groq_api_key_here` with your actual key

### 3.4 Deploy

1. Click **"Deploy!"** button
2. Wait 5-10 minutes for:
   - Installing dependencies (requirements.txt)
   - Loading ChromaDB vector store
   - Loading SQLite database
   - Starting Streamlit app

---

## 🔍 Step 4: Monitor Deployment

### 4.1 Check Logs

Watch the deployment logs for:
- ✅ `Installing dependencies...` → Should complete
- ✅ `Starting Streamlit...` → Should show
- ✅ `You can now view your Streamlit app in your browser.`
- ❌ Any errors related to missing files or dependencies

### 4.2 Common Issues & Fixes

#### Issue 1: "ChromaDB files not found"
**Cause:** ChromaDB not committed to Git  
**Fix:**
```bash
# Force add ChromaDB
git add -f data/vectorstore/chromadb/*
git commit -m "Add ChromaDB vector store"
git push
```

#### Issue 2: "SQLite database not found"
**Cause:** Database not committed to Git  
**Fix:**
```bash
# Force add database
git add -f data/sql_database/sdg_ethiopia.db
git commit -m "Add SQLite database"
git push
```

#### Issue 3: "Module not found" errors
**Cause:** Missing dependencies in requirements.txt  
**Fix:** Add missing package to requirements.txt and push

#### Issue 4: "Out of memory" (OOM)
**Cause:** Streamlit Community Cloud has 1GB RAM limit  
**Fix:** Optimize ChromaDB or use external vector DB (see Step 6)

---

## 🎯 Step 5: Verify Deployment

### 5.1 Test Core Functionality

Visit your app URL and test:

1. **PDF RAG (Engine A):**
   - Ask: "What is ESS's role in Ethiopia?"
   - Should return answer from ESS reports

2. **SQL Query (Engine B):**
   - Ask: "What is Ethiopia's poverty rate in 2022?"
   - Should return data from UN SDG database

3. **Dual Engine:**
   - Ask: "Tell me about education in Ethiopia"
   - Should return results from BOTH engines

4. **Export Functionality:**
   - Generate a response
   - Click "📤 EXPORT" → "📄 Export to PDF"
   - Should download PDF

5. **Source Attribution:**
   - Check that sources are displayed
   - Click download buttons for Excel files
   - Verify correct files download

### 5.2 Performance Check

- ⏱️ Response time: Should be **1-3 seconds** (Groq API)
- 🔄 Simultaneous users: Test with 2-3 browser tabs
- 💾 Memory: Check logs for memory warnings

---

## ⚙️ Step 6: Optimize for Production

### 6.1 Enable GitHub Auto-Deployment

Streamlit Cloud automatically redeploys when you push to GitHub:

```bash
# Make changes locally
git add .
git commit -m "Update: feature XYZ"
git push

# App will auto-redeploy in ~2-3 minutes
```

### 6.2 Memory Optimization (If Needed)

If you hit 1GB RAM limit:

**Option A: Use SQLite Only (Remove ChromaDB)**
- Removes vector search capability
- Keeps SQL queries
- Saves ~400 MB RAM

**Option B: External Vector Database**
- Use Qdrant Cloud (free tier: 1GB)
- Update code to connect to cloud instance
- Keeps all functionality

**Option C: Reduce ChromaDB Size**
- Process fewer PDFs (e.g., 100 most important)
- Reduce chunk size
- Use smaller embedding model

### 6.3 Set Up Custom Domain (Optional)

Streamlit Cloud supports custom domains:

1. Go to app settings → **"Custom domain"**
2. Add your domain: `ess.yourdomain.com`
3. Update DNS records as instructed
4. Wait for SSL certificate (automatic)

---

## 📊 Step 7: Monitoring & Maintenance

### 7.1 Usage Monitoring

Streamlit Cloud provides:
- 📈 **Analytics:** Page views, unique users
- 🕒 **Uptime:** Should be 99%+ (24/7)
- 📝 **Logs:** Real-time application logs

Access at: `https://share.streamlit.io/[your-app]/logs`

### 7.2 Update Workflow

To update the app:

```bash
# 1. Make changes locally
# Edit files...

# 2. Test locally
streamlit run streamlit_app.py

# 3. Commit and push
git add .
git commit -m "Update: description"
git push

# 4. Streamlit Cloud auto-deploys
# Wait 2-3 minutes for deployment
```

### 7.3 Backup Strategy

**Important:** Streamlit Cloud can lose data on redeploy!

Backup these regularly:
- `data/conversation_history.json` (user conversations)
- `exports/` folder (generated PDFs/Word docs)

**Solution:** Store these in external storage:
- AWS S3
- Google Cloud Storage
- Dropbox API

---

## 🔒 Security Best Practices

### 1. API Key Management
- ✅ Store in Streamlit Cloud secrets (not in code)
- ✅ Rotate Groq API key every 90 days
- ✅ Monitor API usage at https://console.groq.com

### 2. Repository Security
- ⚠️ **NEVER** commit `.env` file to Git
- ✅ Use `.gitignore` properly
- ✅ If accidentally committed, regenerate all API keys

### 3. User Data Privacy
- Conversation history is stored locally
- No data sent to third parties (except Groq LLM)
- GDPR compliant (user can request data deletion)

---

## 🆘 Troubleshooting

### Problem: App keeps restarting
**Cause:** Memory limit exceeded  
**Fix:** Optimize ChromaDB or use external vector DB

### Problem: Slow responses (>10 seconds)
**Cause:** Groq API rate limiting or network issues  
**Fix:** Check Groq dashboard for rate limits

### Problem: "Secrets not found" error
**Cause:** Secrets not configured in Streamlit Cloud  
**Fix:** Add secrets in app settings (Step 3.3)

### Problem: Sources not downloading
**Cause:** Excel files not in repository  
**Fix:** Ensure `data/raw/un_sdg_excel/*.xlsx` files are committed

### Problem: ChromaDB initialization error
**Cause:** ChromaDB files corrupted or missing  
**Fix:** Rebuild ChromaDB locally and recommit:
```bash
python build_dual_engine.py
git add data/vectorstore/chromadb/
git commit -m "Rebuild ChromaDB"
git push
```

---

## 📞 Support & Resources

### Streamlit Resources
- 📖 Docs: https://docs.streamlit.io/deploy
- 💬 Forum: https://discuss.streamlit.io
- 🐛 Issues: https://github.com/streamlit/streamlit/issues

### Groq API
- 🔑 Console: https://console.groq.com
- 📊 Usage: Free tier = 14,400 requests/day
- 📚 Docs: https://console.groq.com/docs

### Your System
- 🎓 Developer: Yonas Abiyu Gion
- 🏛️ Institution: Bahir Dar University
- 🏢 Client: Ethiopian Statistical Service

---

## ✅ Deployment Checklist

Use this checklist when deploying:

```
☐ Update .gitignore to include ChromaDB and SQLite
☐ Verify ChromaDB files exist locally
☐ Verify SQLite database exists
☐ Update requirements.txt (remove ollama)
☐ Create GitHub repository
☐ Push code to GitHub
☐ Verify data files uploaded to GitHub
☐ Sign up for Streamlit Cloud
☐ Create new app on Streamlit Cloud
☐ Configure secrets (GROQ_API_KEY)
☐ Deploy app
☐ Monitor deployment logs
☐ Test all functionality (PDF, SQL, Export)
☐ Share URL with stakeholders
☐ Set up monitoring/alerts
☐ Document deployment date and URL
```

---

## 🎉 Success Criteria

Your deployment is successful when:

✅ App is accessible 24/7 at your Streamlit URL  
✅ Response time < 3 seconds per query  
✅ Both engines (PDF + SQL) work correctly  
✅ Sources display with download links  
✅ Export to PDF/Word works  
✅ No memory errors in logs  
✅ Auto-redeploy works on GitHub push  

---

**Deployment URL:** `https://your-app-name.streamlit.app`

**Estimated Deployment Time:** 30-45 minutes (first time)

**Cost:** $0 (100% free with Streamlit Community Cloud + Groq Free Tier)

---

*Last Updated: August 12, 2026*  
*For deployment support, contact: Yonas Abiyu Gion*

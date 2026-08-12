# 🚀 Streamlit Cloud Deployment - Quick Reference

## ⚡ 5-Minute Deploy

### 1. Pre-Deployment Check
```bash
python check_deployment_readiness.py
```

### 2. Push to GitHub
```bash
git add .
git commit -m "Deploy to Streamlit Cloud"
git push origin main
```

### 3. Deploy on Streamlit Cloud
1. Go to: https://share.streamlit.io
2. Click "New app"
3. Select: Your repo → `main` branch → `streamlit_app.py`
4. Click "Advanced settings" → Add secrets:
   ```toml
   GROQ_API_KEY = "your-key-here"
   LLM_PROVIDER = "groq"
   ```
5. Click "Deploy!"

---

## 📌 Critical Requirements

### ✅ Must Include in Git:
- `data/vectorstore/chromadb/` (ChromaDB - 200+ MB)
- `data/sql_database/sdg_ethiopia.db` (SQLite - ~50 MB)
- `data/raw/un_sdg_excel/*.xlsx` (17 Excel files)

### ❌ Must Exclude from Git:
- `.env` (contains secrets - use Streamlit secrets instead)
- `data/conversation_history.json` (user-generated)
- `__pycache__/` (Python cache)

---

## 🔑 Required Secrets

Add in Streamlit Cloud → App Settings → Secrets:

```toml
GROQ_API_KEY = "your-groq-api-key"
LLM_PROVIDER = "groq"
```

Get Groq API key: https://console.groq.com/keys

---

## 🐛 Common Issues

### Issue: "ChromaDB not found"
**Fix:**
```bash
git add -f data/vectorstore/chromadb/
git commit -m "Add ChromaDB"
git push
```

### Issue: "Out of memory"
**Fix:** Check logs → May need to optimize ChromaDB size

### Issue: "Module not found"
**Fix:** Add missing package to `requirements.txt`

---

## 📊 Expected Performance

- **Deploy Time:** 5-10 minutes (first time)
- **Response Time:** 1-3 seconds per query
- **Uptime:** 24/7 (99.9%+)
- **Memory:** ~800 MB used (1 GB limit)
- **Cost:** $0 (100% free)

---

## 🔗 Important Links

- **Deployment Guide:** `docs/STREAMLIT_CLOUD_DEPLOYMENT.md`
- **Streamlit Cloud:** https://share.streamlit.io
- **Groq Console:** https://console.groq.com
- **Your App URL:** `https://your-app-name.streamlit.app`

---

## 📞 Quick Help

### Check deployment status:
```bash
# View in browser
https://share.streamlit.io/[your-username]/[repo-name]

# Check logs
Click "Manage app" → "Logs" in Streamlit Cloud dashboard
```

### Update deployed app:
```bash
# Make changes → push to GitHub
git add .
git commit -m "Update X"
git push

# Streamlit Cloud auto-redeploys in 2-3 minutes
```

---

**Last Updated:** August 12, 2026  
**Deployment Time:** ~30-45 minutes (including setup)  
**Difficulty:** ⭐⭐☆☆☆ (Easy-Medium)

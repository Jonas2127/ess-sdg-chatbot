# ⚡ Streamlit Cloud Deployment - Quick Start

## 🚀 Deploy in 30 Minutes!

Follow these 6 steps in order:

---

## ✅ Step 1: Qdrant Cloud (5 min)

1. Go to https://cloud.qdrant.io/
2. Sign up (free)
3. Create cluster (Free plan, 1GB)
4. Copy **Cluster URL** and **API Key**

---

## ✅ Step 2: Upload Data (10 min)

```bash
python upload_to_qdrant_cloud.py
```

Paste your Qdrant URL and API key when prompted.

**Wait 5-10 minutes** for upload to complete.

---

## ✅ Step 3: GitHub Repo (5 min)

```bash
git init
git add .
git commit -m "ESS RAG Chatbot"
git remote add origin https://github.com/YOUR_USERNAME/ess-rag-chatbot.git
git push -u origin main
```

**Important:** Make repo **PUBLIC**!

---

## ✅ Step 4: Test Locally (2 min)

```bash
# Set environment variables
set QDRANT_URL=https://your-cluster.qdrant.io
set QDRANT_API_KEY=your_api_key

# Run
streamlit run streamlit_app.py
```

Test a question. If it works, you're ready!

---

## ✅ Step 5: Deploy (5 min)

1. Go to https://streamlit.io/cloud
2. Sign up with GitHub
3. Click "New app"
4. Select your repo → `streamlit_app.py`
5. Click "Advanced settings"
6. Add secrets:

```toml
GROQ_API_KEY = "your_groq_key"
LLM_PROVIDER = "groq"
QDRANT_URL = "https://your-cluster.qdrant.io"
QDRANT_API_KEY = "your_qdrant_key"
```

7. Click "Deploy"

---

## ✅ Step 6: Test Live App (3 min)

1. Wait for deployment (5-10 min)
2. Open your app URL
3. Test questions
4. Verify everything works

---

## 🎉 Done!

Your app is live at: `https://your-app.streamlit.app`

Share the link with anyone!

---

## 📝 Quick Reference

### Secrets Format

```toml
GROQ_API_KEY = "gsk_xxx..."
LLM_PROVIDER = "groq"
QDRANT_URL = "https://xxx.qdrant.io"
QDRANT_API_KEY = "qdrant_xxx..."
```

### Test Questions

- "What is Ethiopia's poverty rate?"
- "Show me education data for 2021"
- "What is the GDP growth trend?"

### Troubleshooting

**App won't start?**
- Check secrets are correct
- View logs in Streamlit dashboard

**Out of memory?**
- Verify using Qdrant Cloud (not local)
- Check flexible_rag.py shows "Using Qdrant Cloud"

**Slow responses?**
- First load is slow (1-2 min)
- Subsequent loads faster (10-20s)

---

## 📚 Full Guide

See `STREAMLIT_CLOUD_DEPLOY.md` for complete instructions.

---

**Need help?** Check the full deployment guide or ask me!

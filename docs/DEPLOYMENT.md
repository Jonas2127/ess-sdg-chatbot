# Deployment Guide

Guide for deploying the ESS SDG Chatbot to Streamlit Cloud for 24/7 public access.

## Overview

This deployment strategy uses three services:
1. **GitHub**: Source code repository
2. **Hugging Face**: Large file storage (ChromaDB, SQLite)
3. **Streamlit Cloud**: Application hosting (free tier)

**Why this approach?**
- GitHub has file size limits (100MB per file)
- ChromaDB is ~800MB, SQLite is ~10MB
- Hugging Face provides free hosting for datasets
- Streamlit Cloud downloads files on first run

---

## Prerequisites

### Accounts Required

1. **GitHub Account**
   - Sign up: https://github.com/join
   - Repository: https://github.com/Jonas2127/ess-sdg-chatbot

2. **Hugging Face Account**
   - Sign up: https://huggingface.co/join
   - Create dataset repository

3. **Streamlit Cloud Account**
   - Sign up: https://streamlit.io/cloud
   - Connect with GitHub

### Local Setup

Ensure your local environment works:
```bash
streamlit run streamlit_app.py
```

Test a query before deploying!

---

## Step 1: Prepare Repository

### Update .gitignore

Ensure large files are excluded:

```gitignore
# Large data files
data/vectorstore/chromadb/
data/sql_database/*.db
data/raw/ess_reports/pdfs/
data/raw/afdb_reports/
chromadb.zip

# Secrets
.env
.env.local

# User data
data/conversation_history.json
exports/*.pdf
exports/*.docx
```

### Commit Code

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

**What to push**:
- Source code (`src/`)
- Web interfaces (`streamlit_app.py`, `telegram_bot.py`)
- Configuration (`requirements.txt`, `.env.example`)
- Documentation (`README.md`, `docs/`)
- Build scripts (`build_dual_engine.py`, `download_chromadb.py`)

**What NOT to push**:
- Large files (PDFs, databases)
- API keys (`.env`)
- User-generated content

---

## Step 2: Upload to Hugging Face

### Create Dataset Repository

1. Go to: https://huggingface.co/new-dataset
2. Fill in:
   - **Name**: `ess-sdg-chatbot-data`
   - **Type**: Dataset
   - **Visibility**: Public
3. Click "Create dataset"

Your repository will be at: `https://huggingface.co/YOUR_USERNAME/ess-sdg-chatbot-data`

### Prepare Files for Upload

Create ZIP file of ChromaDB:

**Windows:**
```powershell
Compress-Archive -Path "data\vectorstore\chromadb" -DestinationPath "chromadb.zip" -Force
```

**macOS/Linux:**
```bash
cd data/vectorstore
zip -r ../../chromadb.zip chromadb/
cd ../..
```

This creates `chromadb.zip` (~800MB)

### Upload Files via Web Interface

1. Go to your dataset repository
2. Click "Files" → "Add file" → "Upload files"
3. Upload these files:
   - `chromadb.zip` (~800MB, takes 5-10 minutes)
   - `data/sql_database/sdg_ethiopia.db` (~10MB)
4. Click "Commit changes to main"
5. Wait for upload to complete

### Update download_chromadb.py

Edit `download_chromadb.py` line 21:

```python
# Before
HF_USERNAME = "YOUR_USERNAME_HERE"

# After (use your actual HF username)
HF_USERNAME = "yonasabiyu"
```

Commit and push:
```bash
git add download_chromadb.py
git commit -m "Update HuggingFace username"
git push origin main
```

---

## Step 3: Deploy to Streamlit Cloud

### Configure Streamlit App

1. Go to: https://streamlit.io/cloud
2. Click "New app"
3. Fill in:
   - **Repository**: `Jonas2127/ess-sdg-chatbot`
   - **Branch**: `main`
   - **Main file**: `streamlit_app.py`
   - **App URL**: `ess-sdg-chatbot` (or choose your own)

### Add Secrets

Click "Advanced settings" → Scroll to "Secrets"

Paste your configuration:

```toml
# LLM Provider (choose one)
LLM_PROVIDER = "groq"

# API Keys (add all, system will use based on LLM_PROVIDER)
GROQ_API_KEY = "gsk_your_actual_key_here"
GEMINI_API_KEY = "AIza_your_actual_key_here"
HUGGINGFACE_API_TOKEN = "hf_your_actual_token_here"

# Optional: Telegram bot
TELEGRAM_BOT_TOKEN = "your_telegram_token_if_using_bot"
```

**Important**:
- Use actual values, not placeholders
- Choose `LLM_PROVIDER` that matches your API key
- Recommended: `groq` (fastest and most reliable)

### Deploy

1. Click "Deploy!"
2. Watch deployment logs

**Expected process**:
```
[BUILDING] Installing dependencies (2-3 minutes)
[LOADING] Starting application
[INFO] Downloading ChromaDB from HuggingFace
[PROGRESS] 50MB / 800MB (6%)
[PROGRESS] 100MB / 800MB (12%)
...
[OK] ChromaDB ready
[INFO] Downloading SQLite database
[OK] SQLite ready
[INFO] Initializing RAG system
[OK] System ready
```

**Total time**: 10-15 minutes for first deployment

### Verify Deployment

1. Your app will be at: `https://ess-sdg-chatbot.streamlit.app`
2. Test with a query: "What is Ethiopia's poverty rate?"
3. Verify:
   - Response is generated
   - Sources are shown
   - No errors in logs

---

## Step 4: Configure Domain (Optional)

Streamlit provides a subdomain: `your-app.streamlit.app`

For custom domain:
1. Go to app settings
2. Click "Custom domain"
3. Follow instructions to configure DNS

---

## Troubleshooting

### Deployment Failed

**Error**: `ModuleNotFoundError`

**Solution**: Check `requirements.txt` includes all dependencies

---

**Error**: `File not found: chromadb.zip`

**Solution**:
1. Verify HuggingFace username in `download_chromadb.py`
2. Check files uploaded to HuggingFace
3. Verify repository is public

---

**Error**: `API key not found`

**Solution**:
1. Go to app settings → Secrets
2. Verify API keys are correctly pasted
3. Check no extra spaces or quotes
4. Restart app

---

**Error**: `ChromaDB download stuck`

**Solution**:
- Wait (800MB download takes 5-10 minutes)
- Check HuggingFace repository is accessible
- View logs for specific error message

---

### App Running Slowly

**Issue**: Responses take 30+ seconds

**Solutions**:
1. **Check LLM provider**: Use Groq or Gemini, not Ollama
   ```toml
   LLM_PROVIDER = "groq"
   ```

2. **Verify API keys**: Ensure keys are valid and not rate-limited

3. **Check logs**: Look for timeout errors

---

### Out of Memory

**Issue**: App crashes with memory error

**Solutions**:
1. **Streamlit free tier**: 1GB RAM limit
2. **Reduce retrieval**: Edit `langchain_rag.py`
   ```python
   "k": 10,  # Instead of 15
   ```
3. **Disable cross-encoder**: Comment out re-ranking code
4. **Upgrade**: Consider Streamlit Team plan ($250/month)

---

## Updating Deployed App

### Code Updates

When you push to GitHub, Streamlit Cloud detects changes:

1. Push updates:
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```

2. Streamlit will show "App has changed"
3. Click "Reboot app" or wait for auto-reboot

**Note**: Changes take ~30 seconds to deploy

### Data Updates

To update databases:

1. **Update locally**:
   ```bash
   python build_dual_engine.py
   ```

2. **Create new ZIP**:
   ```bash
   zip -r chromadb.zip data/vectorstore/chromadb/
   ```

3. **Upload to HuggingFace**:
   - Go to dataset repository
   - Upload new `chromadb.zip` (overwrites old)

4. **Clear Streamlit cache**:
   - Go to app settings
   - Click "Clear cache"
   - Reboot app

**Note**: App will re-download ~800MB file

### Secrets Updates

To update API keys:

1. Go to app settings → Secrets
2. Edit secrets
3. Click "Save"
4. App auto-reboots

---

## Monitoring

### View Logs

1. Go to app page on Streamlit Cloud
2. Click "Manage app"
3. View logs in real-time

**Useful for**:
- Debugging errors
- Monitoring usage
- Checking performance

### Usage Statistics

Streamlit Cloud provides:
- **Active users**: Current users
- **Total visitors**: All-time count
- **Resource usage**: RAM, CPU

**Free tier limits**:
- Unlimited visitors
- 1GB RAM
- 1 CPU core
- App sleeps after 7 days of inactivity

### App Health Check

Check if app is running:
```bash
curl https://ess-sdg-chatbot.streamlit.app
```

Should return HTML (status 200)

---

## Security Considerations

### API Keys

- **Never commit** API keys to GitHub
- **Use Streamlit secrets** for sensitive data
- **Rotate keys** periodically
- **Monitor usage** on provider dashboards

### Data Privacy

- User queries are stored in `conversation_history.json`
- This file is in `.gitignore` (not pushed to GitHub)
- Each deployment has its own history
- Consider adding privacy notice

### Rate Limiting

Free tier API limits:
- **Groq**: 30 requests/minute
- **Gemini**: 60 requests/minute
- **HuggingFace**: 1000 requests/day

For high traffic, consider:
- Upgrading to paid tiers
- Implementing caching
- Adding rate limiting to app

---

## Scaling

### Current Architecture

- **Single-server**: One Streamlit instance
- **Stateless**: No session persistence
- **Concurrent users**: 5-10 comfortably

### For More Users

**Option 1: Streamlit Teams** ($250/month)
- More resources (4GB RAM, 4 CPUs)
- Custom domain
- Priority support

**Option 2: Self-hosting**
- Deploy to AWS/GCP/Azure
- Use Docker container
- Add load balancer for scale

**Option 3: Optimize Current**
- Add caching (Redis)
- Implement rate limiting
- Reduce resource usage

---

## Backup Strategy

### Code Backup

- **Primary**: GitHub repository
- **Backup**: Local copy
- **Version control**: Git tags for releases

### Data Backup

- **HuggingFace**: Primary storage
- **Local**: Original PDFs and Excel files
- **Cloud**: Optional backup to S3/Google Drive

### Configuration Backup

- **`.env.example`**: Template in repository
- **Secrets**: Document separately (not in Git)
- **Documentation**: All guides in `docs/`

---

## Cost Summary

### Free Tier (Current Setup)

| Service | Cost | Limits |
|---------|------|--------|
| GitHub | Free | 100MB per file |
| HuggingFace | Free | Unlimited datasets |
| Streamlit Cloud | Free | 1GB RAM, sleeps after 7 days |
| Groq API | Free | 30 req/min |
| Gemini API | Free | 60 req/min |
| **Total** | **$0/month** | Suitable for demos/low traffic |

### Paid Options

| Service | Cost | Benefits |
|---------|------|----------|
| Streamlit Teams | $250/month | 4GB RAM, 4 CPU, custom domain |
| Groq Pro | $18/month | Higher rate limits |
| AWS EC2 (t3.medium) | $30/month | Full control, scalable |

---

## Production Checklist

Before launching publicly:

- [ ] Test all functionality locally
- [ ] Push code to GitHub
- [ ] Upload databases to HuggingFace
- [ ] Configure Streamlit secrets
- [ ] Deploy and verify
- [ ] Test all query types
- [ ] Verify source citations
- [ ] Check export functionality (PDF/Word)
- [ ] Test on mobile devices
- [ ] Monitor logs for errors
- [ ] Set up backup strategy
- [ ] Document API keys separately
- [ ] Share link with stakeholders

---

## Support

### Common Deployment Links

- **Your GitHub repo**: https://github.com/Jonas2127/ess-sdg-chatbot
- **Your HuggingFace dataset**: https://huggingface.co/YOUR_USERNAME/ess-sdg-chatbot-data
- **Your deployed app**: https://ess-sdg-chatbot.streamlit.app
- **Streamlit Cloud dashboard**: https://streamlit.io/cloud

### Getting Help

1. **Streamlit Docs**: https://docs.streamlit.io/
2. **Community Forum**: https://discuss.streamlit.io/
3. **GitHub Issues**: Report bugs in your repository
4. **LangChain Docs**: https://python.langchain.com/

---

## Next Steps

After successful deployment:

1. **Share the link** with users and stakeholders
2. **Monitor usage** and collect feedback
3. **Iterate** based on user needs
4. **Consider** adding authentication for private data
5. **Explore** additional features (multilingual, voice input, etc.)

Your chatbot is now live and accessible 24/7! 🎉

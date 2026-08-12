# 📤 Upload ChromaDB to Hugging Face

ChromaDB is too large for GitHub (805 MB > 100 MB limit). We'll host it on Hugging Face (FREE) and download it at runtime.

---

## Step 1: Compress ChromaDB

Run this in PowerShell:

```powershell
# Navigate to project folder
cd C:\Users\HP\ESSFINALPROJECT

# Compress ChromaDB folder to ZIP
Compress-Archive -Path "data\vectorstore\chromadb" -DestinationPath "chromadb.zip" -Force

# Check size
(Get-Item "chromadb.zip").Length / 1MB
```

Expected: ~300-400 MB (compressed from 865 MB)

---

## Step 2: Create Hugging Face Account

1. Go to: **https://huggingface.co/join**
2. Sign up (FREE account)
3. Verify your email

---

## Step 3: Create Dataset on Hugging Face

1. Go to: **https://huggingface.co/new-dataset**
2. Fill in:
   - **Owner:** Your username (e.g., `Jonas2127`)
   - **Dataset name:** `ess-chromadb`
   - **License:** `mit`
   - **Visibility:** Public (required for free hosting)
3. Click **"Create dataset"**

---

## Step 4: Upload chromadb.zip

### Option A: Web Upload (Easiest)

1. On your dataset page: `https://huggingface.co/datasets/YOUR_USERNAME/ess-chromadb`
2. Click **"Files"** tab
3. Click **"Add file"** → **"Upload files"**
4. Drag `chromadb.zip` or click to browse
5. Click **"Commit changes to main"**
6. Wait for upload (5-10 minutes for 300-400 MB)

### Option B: Git Upload (Faster for large files)

```powershell
# Install Git LFS
git lfs install

# Clone your dataset repo
git clone https://huggingface.co/datasets/YOUR_USERNAME/ess-chromadb
cd ess-chromadb

# Track large file with LFS
git lfs track "*.zip"
git add .gitattributes

# Copy and add chromadb.zip
copy ..\chromadb.zip .
git add chromadb.zip
git commit -m "Add ChromaDB vector store"

# Push
git push
```

---

## Step 5: Get Download URL

After upload, your URL will be:
```
https://huggingface.co/datasets/YOUR_USERNAME/ess-chromadb/resolve/main/chromadb.zip
```

Example for user `Jonas2127`:
```
https://huggingface.co/datasets/Jonas2127/ess-chromadb/resolve/main/chromadb.zip
```

---

## Step 6: Update Environment Variable (Optional)

If you used a different username, update the URL in Streamlit Cloud secrets:

```toml
CHROMADB_URL = "https://huggingface.co/datasets/YOUR_USERNAME/ess-chromadb/resolve/main/chromadb.zip"
```

(If you used `Jonas2127`, no change needed - it's the default)

---

## Step 7: Test Locally (Optional)

```powershell
# Delete local ChromaDB to test download
Remove-Item -Recurse -Force data\vectorstore\chromadb

# Run download script
python download_chromadb.py

# Should download and extract successfully
```

---

## ✅ Verification Checklist

```
☐ chromadb.zip created (~300-400 MB)
☐ Hugging Face account created
☐ Dataset created: YOUR_USERNAME/ess-chromadb
☐ chromadb.zip uploaded to Hugging Face
☐ Download URL confirmed working
☐ (Optional) Test download locally
```

---

## 🚀 After Upload - Continue Deployment

Once chromadb.zip is uploaded to Hugging Face:

1. **Remove chromadb from Git history:**
   ```powershell
   git rm -r --cached data/vectorstore/chromadb
   git commit -m "Remove ChromaDB (now hosted on Hugging Face)"
   ```

2. **Push to GitHub:**
   ```powershell
   git push -u origin main
   ```

3. **Deploy on Streamlit Cloud** (follow DEPLOY_NOW.md)

---

## 📊 How It Works

1. **First deploy:** Streamlit app starts → download_chromadb.py runs → Downloads chromadb.zip from Hugging Face → Extracts to `data/vectorstore/chromadb/` → App uses it
2. **Subsequent restarts:** ChromaDB already exists → Skip download → App starts immediately
3. **Cost:** $0 (Hugging Face datasets are free for public repos)

---

## 🆘 Troubleshooting

### Upload fails on Hugging Face website
- File too large for browser
- Use Git LFS method (Option B) instead

### Download fails in Streamlit
- Check URL is correct in `download_chromadb.py`
- Verify dataset is public on Hugging Face
- Check Hugging Face isn't down: https://status.huggingface.co

### "chromadb.zip not found" error
- Ensure file is named exactly `chromadb.zip` (not `chromadb (1).zip`)
- Upload to root of dataset (not in a folder)

---

**Next:** After uploading to Hugging Face, return to DEPLOY_NOW.md Step 2 (Push to GitHub)

---

*This solution bypasses GitHub's 100 MB file limit while keeping everything FREE!*

# 🔑 Get Google Gemini API Key - Step by Step

## Why Gemini Instead of Groq?
- ✅ More reliable (better uptime)
- ✅ More generous free tier
- ✅ Faster responses
- ✅ Better model access

## Steps to Get FREE Gemini API Key:

### 1. Go to Google AI Studio
Open: https://aistudio.google.com/app/apikey

### 2. Sign in with Google Account
Use any Gmail account

### 3. Create API Key
- Click "Create API Key" button
- Select "Create API key in new project" (or use existing project)
- Copy the key

### 4. Verify Key Format
Valid Gemini key looks like:
```
AIzaSyAbc123Def456Ghi789Jkl012Mno345Pqr678Stu901Vwx
```
- Starts with `AIza`
- About 39 characters long
- No spaces

### 5. Update Your .env File
Open `.env` and update:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyAbc123Def456Ghi789Jkl012Mno345Pqr678Stu901Vwx
```

### 6. Test It
Run:
```bash
python test_gemini_new.py
```

You should see:
```
✅ Gemini API key is VALID!
📝 Response: Hello, I work!
```

### 7. Update Streamlit Cloud Secrets
Go to: https://share.streamlit.io
- Open your app settings
- Go to Secrets
- Add:
```toml
LLM_PROVIDER = "gemini"
GEMINI_API_KEY = "AIzaSyAbc123Def456Ghi789Jkl012Mno345Pqr678Stu901Vwx"
HF_REPO_ID = "yonasabiyu/ess-sdg-chatbot-data"
```

### 8. Reboot App
Click "Reboot app" and wait for deployment!

---

## Troubleshooting

**"API key invalid"**
- Make sure you copied the ENTIRE key
- No extra spaces or line breaks
- Must start with `AIza`

**"Module not found"**
- Run: `pip install -r requirements.txt`

**Still not working?**
- Create a NEW API key
- Make sure you're signed in to Google AI Studio
- Check your Google Cloud quotas

---

## Need Help?
1. Get key from: https://aistudio.google.com/app/apikey
2. Paste in `.env` file
3. Test with: `python test_gemini_new.py`
4. If it works locally, copy to Streamlit Cloud secrets

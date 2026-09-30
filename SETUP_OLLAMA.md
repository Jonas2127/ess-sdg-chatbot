# Setup Ollama (No API Keys Required!)

Since your API keys are expired/not working, use Ollama which runs locally without any API keys.

## Step 1: Install Ollama

Download and install Ollama from:
**https://ollama.com/download**

Choose "Download for Windows" and run the installer.

## Step 2: Install a Model

After installation, open PowerShell and run:

```powershell
ollama pull llama3.2:1b
```

This downloads a fast, small model (~1.3GB). Takes 2-5 minutes depending on internet speed.

## Step 3: Verify Ollama is Running

```powershell
ollama list
```

You should see `llama3.2:1b` in the list.

## Step 4: Test Your Chatbot

```powershell
streamlit run streamlit_app.py
```

The chatbot will now work without any API keys!

**Response time**: 5-10 seconds per query (slower than cloud APIs but works offline and free forever)

## Alternative: Get Fresh API Keys

If you prefer faster responses (2-3 seconds), get new free API keys:

1. **Groq** (recommended): https://console.groq.com/keys
   - Sign up/login
   - Create new API key
   - Update `.env`: `GROQ_API_KEY=your_new_key_here`
   - Update `.env`: `LLM_PROVIDER=groq`

2. **Google Gemini**: https://aistudio.google.com/app/apikey
   - Sign in with Google account
   - Create new API key
   - Update `.env`: `GEMINI_API_KEY=your_new_key_here`
   - Update `.env`: `LLM_PROVIDER=gemini`

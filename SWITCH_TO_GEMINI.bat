@echo off
echo ========================================
echo Switch to Gemini (More Reliable!)
echo ========================================
echo.
echo Installing required packages...
pip install -q google-genai langchain-google-genai
echo.
echo ========================================
echo.
echo Next steps:
echo 1. Get Gemini API key from: https://aistudio.google.com/app/apikey
echo 2. Open .env file
echo 3. Update these lines:
echo    LLM_PROVIDER=gemini
echo    GEMINI_API_KEY=your_key_here
echo 4. Run: python test_gemini_new.py
echo.
echo ========================================
pause

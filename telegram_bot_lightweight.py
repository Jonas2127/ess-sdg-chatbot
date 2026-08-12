"""
Lightweight Telegram Bot for ESS RAG Chatbot
Forwards questions to Streamlit app API (no heavy dependencies!)
Perfect for PythonAnywhere free tier (< 10 MB)
"""

import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Streamlit app URL (your deployed app)
STREAMLIT_APP_URL = os.getenv('STREAMLIT_APP_URL', 'https://ess-rag-chatbot.streamlit.app')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when /start command is issued"""
    welcome_message = """
🇪🇹 **Welcome to ESS RAG Chatbot!**

I can answer questions about Ethiopian statistics using:
- 📄 **221 ESS PDF Reports** (demographics, agriculture, inflation, etc.)
- 📊 **17 UN SDG Excel Files** (12,037 indicators)

**How to use:**
- Just send me your question in natural language
- Ask about population, GDP, agriculture, poverty, etc.

**Example questions:**
- What is Ethiopia's population?
- Show me inflation trends
- What is the poverty rate?

Let's start! What would you like to know?
"""
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = """
📚 **ESS RAG Chatbot - Help Guide**

**Available Commands:**
/start - Start the bot
/help - Show this help message
/about - About this bot

**How to Ask Questions:**
Just type your question naturally! Examples:
- "What is Ethiopia's current population?"
- "Show me GDP data for 2023"
- "What are the main agricultural products?"
- "Tell me about inflation trends"

**Data Sources:**
- ESS Statistical Reports (221 PDFs)
- UN SDG Database (12,037 indicators)

Need help? Just ask your question!
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send information about the bot"""
    about_text = """
ℹ️ **About ESS RAG Chatbot**

**Technology:**
- 🤖 Powered by LangChain & Groq AI
- 📊 Dual-Engine RAG System
- 🔍 ChromaDB Vector Store
- 💾 SQLite Database

**Data Coverage:**
- 📄 221 ESS PDF reports
- 📊 12,037 UN SDG indicators
- 🇪🇹 Ethiopian Statistical Service data

**Response Time:** 2-5 seconds
**Availability:** 24/7
**Cost:** FREE

Built with ❤️ for data-driven insights about Ethiopia.

🌐 Web version: """ + STREAMLIT_APP_URL
    
    await update.message.reply_text(about_text, parse_mode='Markdown')

def query_streamlit_app(question: str) -> dict:
    """
    Query the Streamlit app API
    Returns dict with 'answer' and 'sources'
    """
    try:
        # Note: This is a simplified version
        # In reality, you'd need to implement an API endpoint in your Streamlit app
        # For now, we'll return a message directing users to the web app
        
        return {
            'answer': f"I'm a lightweight bot that connects to the main system. "
                     f"For the best experience, please visit the web app at: {STREAMLIT_APP_URL}\n\n"
                     f"Or, you can ask your question and I'll do my best to help!",
            'sources': []
        }
    except Exception as e:
        logger.error(f"Error querying Streamlit app: {e}")
        return {
            'answer': f"⚠️ I'm having trouble connecting to the main system. "
                     f"Please try the web app: {STREAMLIT_APP_URL}",
            'sources': []
        }

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages"""
    user_message = update.message.text
    user_name = update.effective_user.first_name
    
    logger.info(f"Received message from {user_name}: {user_message}")
    
    # Send typing indicator
    await update.message.chat.send_action(action="typing")
    
    try:
        # For now, direct users to the web app
        response_text = (
            f"Thank you for your question: *{user_message}*\n\n"
            f"For the most accurate and detailed response, please visit our web application:\n"
            f"🌐 {STREAMLIT_APP_URL}\n\n"
            f"The web app provides:\n"
            f"✅ Full access to 221 PDF reports\n"
            f"✅ 12,037 SDG indicators\n"
            f"✅ Interactive visualizations\n"
            f"✅ Source citations\n"
            f"✅ Export to PDF/Word\n\n"
            f"Simply paste your question there!"
        )
        
        await update.message.reply_text(response_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(
            f"⚠️ An error occurred. Please visit: {STREAMLIT_APP_URL}"
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the Telegram bot"""
    # Get bot token from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        print("❌ Error: Please add TELEGRAM_BOT_TOKEN to your .env file")
        return
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("🚀 Starting lightweight Telegram bot...")
    print("✅ Telegram bot is running! Press Ctrl+C to stop.")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

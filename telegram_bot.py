"""
Telegram Bot Interface for ESS SDG Chatbot

Provides 24/7 access to the dual-engine RAG system via Telegram.
Users can query Ethiopian statistical data and SDG indicators through chat.

Author: Yonas Abiyu Gion
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

from src.dual_engine_router.langchain_rag import LangChainDualEngineRAG

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

rag_system = None


def initialize_rag():
    """Initialize the RAG system."""
    global rag_system
    try:
        logger.info("[LOADING] Initializing RAG system")
        rag_system = LangChainDualEngineRAG()
        logger.info("[OK] RAG system ready")
        return True
    except Exception as e:
        logger.error(f"[ERROR] RAG initialization failed: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when /start is issued."""
    welcome_message = """
**Welcome to ESS Statistical Chatbot**

I can answer questions about Ethiopian statistics using:
- 221 ESS PDF Reports (demographics, agriculture, inflation)
- 17 UN SDG Excel Files (12,037 indicators)

**How to use:**
Just send your question in natural language.

**Example questions:**
- What is Ethiopia's population?
- Show me inflation trends
- What is the poverty rate?

Type /help for more information.
"""
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message."""
    help_text = """
**ESS Chatbot - Help**

**Commands:**
/start - Start the bot
/help - Show this message
/about - About this bot

**How to ask questions:**
Type your question naturally. Examples:
- "What is Ethiopia's current population?"
- "Show me GDP data for 2023"
- "What are the main agricultural products?"

**Data Sources:**
- ESS Statistical Reports (221 PDFs)
- UN SDG Database (12,037 indicators)

**Tips:**
• Ask specific questions
• Mention time periods if relevant
• Use natural language
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send information about the bot."""
    about_text = """
**About ESS SDG Chatbot**

**Technology:**
• Powered by LangChain RAG system
• ChromaDB Vector Store
• SQLite Database

**Data Coverage:**
• 221 ESS PDF reports
• 12,037 UN SDG indicators
• Ethiopian Statistical Service data

**Response Time:** 2-5 seconds
**Availability:** 24/7
**Cost:** FREE

Web version: https://ess-rag-chatbot.streamlit.app
"""
    await update.message.reply_text(about_text, parse_mode='Markdown')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and generate responses."""
    global rag_system
    
    user_message = update.message.text
    user_name = update.effective_user.first_name
    
    logger.info(f"[INFO] Message from {user_name}: {user_message[:50]}")
    
    await update.message.chat.send_action(action="typing")
    
    try:
        if rag_system is None:
            await update.message.reply_text(
                "[WARN] System is initializing. Please try again in a moment."
            )
            return
        
        # Query RAG system
        response = rag_system.query(user_message, verbose=False)
        
        if response and response.get('answer'):
            answer = response['answer']
            sources = response.get('sources', [])
            
            # Send answer (Telegram has 4096 char limit)
            if len(answer) > 4000:
                # Split long answers
                parts = [answer[i:i+4000] for i in range(0, len(answer), 4000)]
                for part in parts:
                    await update.message.reply_text(part)
            else:
                await update.message.reply_text(answer)
            
            # Send sources if available
            if sources:
                source_text = "\n**Sources:**\n"
                for i, source in enumerate(sources[:3], 1):
                    if isinstance(source, dict):
                        metadata = source.get('metadata', {})
                        filename = metadata.get('filename', 'Unknown')
                        source_text += f"{i}. {filename}\n"
                
                await update.message.reply_text(source_text, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                "I couldn't find relevant information. Could you rephrase your question?"
            )
    
    except Exception as e:
        logger.error(f"[ERROR] Processing message: {e}")
        await update.message.reply_text(
            "[ERROR] An error occurred. Please try again."
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log and handle errors."""
    logger.error(f"[ERROR] Update {update} caused error: {context.error}")
    
    if update and update.message:
        await update.message.reply_text(
            "[ERROR] An unexpected error occurred. Please try again later."
        )


def main():
    """Start the Telegram bot."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        logger.error("[ERROR] TELEGRAM_BOT_TOKEN not found in environment")
        print("[ERROR] Please add TELEGRAM_BOT_TOKEN to your .env file")
        return
    
    # Initialize RAG system
    if not initialize_rag():
        logger.error("[ERROR] Failed to initialize RAG system")
        return
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("[INFO] Starting Telegram bot")
    print("[OK] Telegram bot is running. Press Ctrl+C to stop.")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

"""
Telegram Bot for ESS RAG Chatbot
Connects to the dual-engine RAG system for 24/7 availability
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Import the RAG system
from src.dual_engine_router.langchain_rag import LangChainDualEngineRAG

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize RAG system
rag_system = None

def initialize_rag():
    """Initialize the RAG system"""
    global rag_system
    try:
        logger.info("Initializing RAG system...")
        rag_system = LangChainDualEngineRAG()
        logger.info("RAG system initialized successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        return False

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
- Use /help for more information

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

**Tips:**
✅ Ask specific questions
✅ Mention time periods if relevant
✅ Use natural language

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

**Response Time:** 1-3 seconds
**Availability:** 24/7
**Cost:** FREE

Built with ❤️ for data-driven insights about Ethiopia.

🌐 Web version: https://ess-rag-chatbot.streamlit.app
"""
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages and generate responses"""
    global rag_system
    
    user_message = update.message.text
    user_name = update.effective_user.first_name
    
    logger.info(f"Received message from {user_name}: {user_message}")
    
    # Send typing indicator
    await update.message.chat.send_action(action="typing")
    
    try:
        if rag_system is None:
            await update.message.reply_text(
                "⚠️ System is initializing. Please try again in a moment..."
            )
            return
        
        # Get response from RAG system
        response = rag_system.query(user_message)
        
        # Format and send response
        if response and response.get('answer'):
            answer = response['answer']
            sources = response.get('sources', [])
            
            # Send answer
            await update.message.reply_text(answer)
            
            # Send sources if available
            if sources:
                source_text = "\n\n📚 **Sources:**\n"
                for i, source in enumerate(sources[:3], 1):  # Limit to 3 sources
                    if isinstance(source, dict):
                        source_text += f"{i}. {source.get('source', 'Unknown')}\n"
                    else:
                        source_text += f"{i}. {source}\n"
                
                await update.message.reply_text(source_text, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                "I couldn't find relevant information. Could you rephrase your question?"
            )
    
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(
            "⚠️ An error occurred while processing your request. Please try again."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.message:
        await update.message.reply_text(
            "⚠️ An unexpected error occurred. Please try again later."
        )

def main():
    """Start the Telegram bot"""
    # Get bot token from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        print("❌ Error: Please add TELEGRAM_BOT_TOKEN to your .env file")
        return
    
    # Initialize RAG system
    if not initialize_rag():
        logger.error("Failed to initialize RAG system. Exiting...")
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
    logger.info("🚀 Starting Telegram bot...")
    print("✅ Telegram bot is running! Press Ctrl+C to stop.")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

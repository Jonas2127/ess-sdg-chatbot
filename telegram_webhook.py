"""
Telegram Bot Webhook Handler for Vercel
Works with Vercel's serverless functions (100% FREE)
"""

import os
import json
from http.server import BaseHTTPRequestHandler
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv

# Import the RAG system
from src.dual_engine_router.langchain_rag import LangChainDualEngineRAG

# Load environment variables
load_dotenv()

# Initialize RAG system (cached)
rag_system = None

def get_rag_system():
    """Get or initialize RAG system"""
    global rag_system
    if rag_system is None:
        rag_system = LangChainDualEngineRAG()
    return rag_system

def start(update, context):
    """Welcome message"""
    welcome_message = """
🇪🇹 **Welcome to ESS RAG Chatbot!**

I can answer questions about Ethiopian statistics using:
- 📄 221 ESS PDF Reports
- 📊 17 UN SDG Excel Files (12,037 indicators)

**Just send me your question!**

Examples:
- What is Ethiopia's population?
- Show me inflation trends
- What is the poverty rate?
"""
    update.message.reply_text(welcome_message, parse_mode='Markdown')

def help_command(update, context):
    """Help message"""
    help_text = """
📚 **How to use:**
- Just type your question naturally
- Ask about population, GDP, agriculture, poverty, etc.

**Commands:**
/start - Welcome message
/help - This help
/about - About this bot
"""
    update.message.reply_text(help_text, parse_mode='Markdown')

def about_command(update, context):
    """About message"""
    about_text = """
ℹ️ **ESS RAG Chatbot**

Powered by AI • 24/7 Available • FREE

🌐 Web: https://ess-rag-chatbot.streamlit.app
"""
    update.message.reply_text(about_text, parse_mode='Markdown')

def handle_message(update, context):
    """Handle user messages"""
    user_message = update.message.text
    
    try:
        rag = get_rag_system()
        response = rag.query(user_message)
        
        if response and response.get('answer'):
            answer = response['answer']
            update.message.reply_text(answer)
            
            # Send sources
            sources = response.get('sources', [])
            if sources:
                source_text = "\n📚 **Sources:**\n"
                for i, source in enumerate(sources[:3], 1):
                    if isinstance(source, dict):
                        source_text += f"{i}. {source.get('source', 'Unknown')}\n"
                    else:
                        source_text += f"{i}. {source}\n"
                update.message.reply_text(source_text, parse_mode='Markdown')
        else:
            update.message.reply_text(
                "I couldn't find relevant information. Could you rephrase?"
            )
    except Exception as e:
        print(f"Error: {e}")
        update.message.reply_text(
            "⚠️ An error occurred. Please try again."
        )

class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler"""
    
    def do_POST(self):
        """Handle POST requests from Telegram"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            # Parse update
            update_data = json.loads(post_data.decode('utf-8'))
            update = Update.de_json(update_data, bot)
            
            # Process with dispatcher
            dp.process_update(update)
            
            # Send success response
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
            
        except Exception as e:
            print(f"Error processing update: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
    
    def do_GET(self):
        """Handle GET requests (for health checks)"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Telegram Bot is running!')

# Initialize bot and dispatcher
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
bot = Bot(token=bot_token)
dp = Dispatcher(bot, None, use_context=True)

# Register handlers
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('help', help_command))
dp.add_handler(CommandHandler('about', about_command))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

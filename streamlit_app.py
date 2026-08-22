"""
ESS SDG Chatbot - Streamlit Web Interface

A dual-engine RAG chatbot for Ethiopian Statistical Service data.
Provides natural language access to ESS reports and UN SDG indicators.

Author: Yonas Abiyu Gion
"""

import streamlit as st
import sys
import os
import json
from datetime import datetime

# Download vector database on first run (Streamlit Cloud deployment)
if not os.path.exists("data/vectorstore/chromadb/chroma.sqlite3"):
    with st.spinner("[LOADING] Downloading vector database from Hugging Face (first time only, ~5 minutes)"):
        from download_chromadb import download_large_files
        download_large_files()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from dual_engine_router import LangChainDualEngineRAG

HISTORY_FILE = "data/conversation_history.json"
FAQ_FILE = "data/faq_database.json"


def load_conversation_history():
    """Load saved conversation history."""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"[ERROR] Loading history: {e}")
    return []


def save_conversation_history(conversations):
    """Save conversation history to file."""
    try:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERROR] Saving history: {e}")


def load_faq_database():
    """Load FAQ questions from JSON file."""
    try:
        if os.path.exists(FAQ_FILE):
            with open(FAQ_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"[ERROR] Loading FAQ: {e}")
    return {"categories": []}


# Page configuration
st.set_page_config(
    page_title="ESS SDG Chatbot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS for clean appearance
st.markdown("""
<style>
    /* Dark theme styling */
    [data-testid="stAppViewContainer"] {
        background: #0f172a;
    }
    
    [data-testid="stSidebar"] {
        background: #1e293b;
        padding: 1rem;
    }
    
    /* Input styling */
    .stTextInput input {
        background: #1e293b;
        border: 2px solid #334155;
        border-radius: 8px;
        color: #e2e8f0;
        padding: 0.75rem;
    }
    
    .stTextInput input:focus {
        border-color: #10b981;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background: #10b981;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: #059669;
    }
    
    /* Message styling */
    .user-message {
        background: #1e40af;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #e2e8f0;
    }
    
    .bot-message {
        background: #1e293b;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #10b981;
        color: #e2e8f0;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #e2e8f0;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: #1e293b;
        border-radius: 8px;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)


# Initialize RAG system
@st.cache_resource
def init_rag_system():
    """Initialize and cache the RAG system."""
    return LangChainDualEngineRAG()


# Initialize session state
if 'rag_system' not in st.session_state:
    with st.spinner("[LOADING] Initializing RAG system..."):
        st.session_state.rag_system = init_rag_system()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = load_conversation_history()


# Sidebar
with st.sidebar:
    st.title("📊 ESS SDG Chatbot")
    st.markdown("---")
    
    # System information
    with st.expander("🔍 About", expanded=False):
        st.markdown("""
        **Dual-Engine RAG System**
        
        This chatbot uses two specialized engines:
        - **Engine A**: 221 ESS PDF reports
        - **Engine B**: 17 UN SDG Excel files (12,037 indicators)
        
        Ask questions about Ethiopian statistics, demographics, SDG progress, and policy frameworks.
        """)
    
    # Data sources
    with st.expander("📚 Data Sources", expanded=False):
        st.markdown("""
        **ESS PDF Documents:**
        - Consumer Price Index (CPI) reports
        - Agricultural surveys
        - Population census data
        - Business statistics
        
        **UN SDG Database:**
        - All 17 SDG goals
        - 12,037 indicators
        - Time-series data (2000-2023)
        
        **AfDB Policy Documents:**
        - Green growth strategy
        - GTP II framework
        """)
    
    # FAQ section
    st.markdown("---")
    st.subheader("💡 Example Questions")
    
    faq_data = load_faq_database()
    
    for category in faq_data.get("categories", []):
        with st.expander(category["name"], expanded=False):
            for question in category["questions"]:
                if st.button(question, key=f"faq_{question}"):
                    st.session_state.current_query = question
                    st.rerun()
    
    # Conversation history
    st.markdown("---")
    with st.expander("📝 Conversation History", expanded=False):
        if st.session_state.conversation_history:
            st.write(f"Total conversations: {len(st.session_state.conversation_history)}")
            if st.button("Clear All History"):
                st.session_state.conversation_history = []
                st.session_state.messages = []
                save_conversation_history([])
                st.success("History cleared!")
                st.rerun()
        else:
            st.info("No conversation history yet")


# Main chat interface
st.title("Ethiopian Statistical Service Chatbot")
st.markdown("Ask questions about Ethiopian statistics and SDG indicators")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message"><strong>Assistant:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        
        # Display sources if available
        if "sources" in message and message["sources"]:
            with st.expander(f"📄 Sources ({len(message['sources'])})", expanded=False):
                for i, source in enumerate(message["sources"], 1):
                    metadata = source.get("metadata", {})
                    filename = metadata.get("filename", "Unknown")
                    st.markdown(f"**Source {i}:** {filename}")
                    st.text(source.get("content", "")[:300] + "...")
                    st.markdown("---")

# Chat input
if hasattr(st.session_state, 'current_query'):
    user_input = st.session_state.current_query
    del st.session_state.current_query
else:
    user_input = st.chat_input("Ask about ESS statistics, SDG indicators, or policy frameworks...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get response from RAG system
    with st.spinner("[PROCESSING] Analyzing query and retrieving information..."):
        try:
            import time
            start_time = time.time()
            
            result = st.session_state.rag_system.query(user_input, verbose=True)
            
            response_time = time.time() - start_time
            
            # Format response
            answer = result.get("answer", "No response generated")
            sources = result.get("sources", [])
            source_count = result.get("source_count", 0)
            
            # Add response metadata
            formatted_answer = answer
            formatted_answer += f"\n\n**Response Time:** {response_time:.2f}s"
            
            if source_count > 0:
                formatted_answer += f"\n**Sources:** {source_count} document(s)"
            
            # Add bot message
            bot_message = {
                "role": "assistant",
                "content": formatted_answer,
                "sources": sources,
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.messages.append(bot_message)
            
            # Save to conversation history
            conversation = {
                "timestamp": datetime.now().isoformat(),
                "query": user_input,
                "response": answer,
                "source_count": source_count,
                "response_time": response_time
            }
            st.session_state.conversation_history.append(conversation)
            save_conversation_history(st.session_state.conversation_history)
            
        except Exception as e:
            error_message = f"[ERROR] Failed to process query: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})
    
    st.rerun()

# Export functionality
if st.session_state.messages:
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Export to PDF"):
            try:
                from src.export import PDFExporter
                
                # Prepare conversation for export
                conversation_data = []
                for i in range(0, len(st.session_state.messages), 2):
                    if i + 1 < len(st.session_state.messages):
                        conversation_data.append({
                            "query": st.session_state.messages[i]["content"],
                            "response": st.session_state.messages[i + 1]["content"],
                            "sources": st.session_state.messages[i + 1].get("sources", [])
                        })
                
                exporter = PDFExporter()
                pdf_path = exporter.export(conversation_data)
                
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="Download PDF",
                        data=pdf_file,
                        file_name=f"ess_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                
                st.success("PDF generated successfully!")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
    
    with col2:
        if st.button("📝 Export to Word"):
            try:
                from src.export import WordExporter
                
                # Prepare conversation for export
                conversation_data = []
                for i in range(0, len(st.session_state.messages), 2):
                    if i + 1 < len(st.session_state.messages):
                        conversation_data.append({
                            "query": st.session_state.messages[i]["content"],
                            "response": st.session_state.messages[i + 1]["content"],
                            "sources": st.session_state.messages[i + 1].get("sources", [])
                        })
                
                exporter = WordExporter()
                docx_path = exporter.export(conversation_data)
                
                with open(docx_path, "rb") as docx_file:
                    st.download_button(
                        label="Download Word",
                        data=docx_file,
                        file_name=f"ess_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                
                st.success("Word document generated successfully!")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    <p>Ethiopian Statistical Service Dual-Engine RAG Chatbot</p>
    <p>Powered by LangChain, ChromaDB, and SQLite</p>
</div>
""", unsafe_allow_html=True)

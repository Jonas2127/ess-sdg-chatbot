"""
ET ESS RAG Bot - Modern Dark Theme Interface
============================================
Enhanced with FAQ dropdowns and improved UI

Author: Yonas Abiyu Gion
Client: Ethiopian Statistical Service
"""

import streamlit as st
import sys
import os
import base64
import json
from datetime import datetime

# Download ChromaDB from Hugging Face if not present (for Streamlit Cloud deployment)
if not os.path.exists("data/vectorstore/chromadb/chroma.sqlite3"):
    with st.spinner("📥 Downloading vector database from Hugging Face... (first time only, ~5 minutes)"):
        from download_chromadb import download_large_files
        download_large_files()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from dual_engine_router import LangChainDualEngineRAG

# File to store conversation history
HISTORY_FILE = "data/conversation_history.json"

def load_conversation_history():
    """Load conversation history from file"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading history: {e}")
    return []

def save_conversation_history(conversations):
    """Save conversation history to file"""
    try:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")

# Function to load and encode images
def get_base64_image(image_path):
    """Convert image to base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Load assets
ess_logo_base64 = get_base64_image("assets/ess_logo_fixed.png")
ethiopia_map_base64 = get_base64_image("assets/ethiopia_map.png")
ethiopia_flag_base64 = get_base64_image("assets/ethiopia_flag.png")

# FAQ Database - Updated for Dual-Engine System
FAQ_DATABASE = {
    "📊 Price & Consumer Statistics (ESS)": [
        "What is the current Consumer Price Index (CPI)?",
        "How has inflation changed over time?",
        "What are food vs non-food price trends?",
        "Show regional price variations"
    ],
    "🌾 Agriculture & Food Security (ESS Surveys)": [
        "What is Ethiopia's agricultural productivity?",
        "What are the main crops and production volumes?",
        "How is climate change affecting agriculture?",
        "Show livestock population statistics"
    ],
    "👥 Population & Census (ESS Data)": [
        "What is Ethiopia's current population?",
        "What is the urban vs rural distribution?",
        "Show population by region",
        "What is the population growth rate?"
    ],
    "🏢 Business & Economic Statistics (ESS)": [
        "How many businesses are registered?",
        "What is the GDP composition by sector?",
        "Show employment statistics",
        "What are the major economic indicators?"
    ],
    "🌍 SDG Progress & Indicators (UN Data)": [
        "What is Ethiopia's progress on SDG Goal 1 (Poverty)?",
        "Show all 17 SDG indicators for Ethiopia",
        "Compare SDG performance across years",
        "What is the education enrollment rate?"
    ],
    "🇪🇹 National Strategy & Policy (AfDB)": [
        "What is Ethiopia's green growth strategy?",
        "How does GTP II align with AfDB support?",
        "What are the infrastructure development priorities?",
        "Show macro-governance frameworks"
    ]
}

# Page config
st.set_page_config(
    page_title="ET ESS RAG Bot",
    page_icon="🇪🇹",
    layout="wide",
    initial_sidebar_state="expanded",  # Start expanded, but allow hiding
    menu_items={
        'About': "ET ESS RAG Bot - Dual-Engine Statistical Data Assistant & Policy Analyst for Ethiopian Statistical Service"
    }
)

# Sidebar toggle button and text overflow fixes - FINAL FIX
st.markdown("""
<style>
    /* CUSTOM HAMBURGER BUTTON - Always visible */
    button[kind="header"] {
        background: #10b981 !important;
        border: 3px solid #ffffff !important;
        border-radius: 8px !important;
        padding: 0.6rem !important;
        width: 48px !important;
        height: 48px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.8) !important;
        position: relative !important;
        font-size: 0 !important;
    }
    
    /* Add hamburger icon using ::before */
    button[kind="header"]::before {
        content: "☰" !important;
        font-size: 24px !important;
        color: #ffffff !important;
        display: block !important;
        line-height: 1 !important;
    }
    
    button[kind="header"]:hover {
        background: #059669 !important;
        transform: scale(1.1) !important;
    }
    
    button[kind="header"] svg {
        display: none !important;
    }
    
    /* COLLAPSED BUTTON - When sidebar is hidden */
    [data-testid="collapsedControl"] {
        background: #10b981 !important;
        border: 3px solid #ffffff !important;
        border-radius: 8px !important;
        padding: 0.6rem !important;
        width: 48px !important;
        height: 48px !important;
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.8) !important;
        position: fixed !important;
        top: 1rem !important;
        left: 1rem !important;
        font-size: 0 !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Add hamburger icon for collapsed state */
    [data-testid="collapsedControl"]::before {
        content: "☰" !important;
        font-size: 24px !important;
        color: #ffffff !important;
        display: block !important;
        line-height: 1 !important;
    }
    
    [data-testid="collapsedControl"]:hover {
        background: #059669 !important;
        transform: scale(1.1) !important;
    }
    
    [data-testid="collapsedControl"] svg,
    [data-testid="collapsedControl"] span,
    [data-testid="collapsedControl"] p {
        display: none !important;
    }
    
    /* FORCE SIDEBAR TO DISPLAY PROPERLY - NO ROTATION */
    [data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        min-width: 21rem !important;
        max-width: 21rem !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        width: 21rem !important;
        min-width: 21rem !important;
    }
    
    /* Hide the keyboard_double text and replace with hamburger icon */
    [data-testid="stSidebar"] button[kind="header"] {
        font-size: 0 !important;
        background: #10b981 !important;
        border: 2px solid #ffffff !important;
        border-radius: 6px !important;
        padding: 0.4rem !important;
        width: 36px !important;
        height: 36px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Add hamburger icon to sidebar collapse button */
    [data-testid="stSidebar"] button[kind="header"]::before {
        content: "☰" !important;
        font-size: 20px !important;
        color: #ffffff !important;
        display: block !important;
        line-height: 1 !important;
    }
    
    [data-testid="stSidebar"] button[kind="header"]:hover {
        background: #059669 !important;
        transform: scale(1.05) !important;
    }
    
    /* Hide the SVG and text inside the button */
    [data-testid="stSidebar"] button[kind="header"] svg,
    [data-testid="stSidebar"] button[kind="header"] span,
    [data-testid="stSidebar"] button[kind="header"] p {
        display: none !important;
    }
    
    /* Let Streamlit render text naturally - don't override */
    /* Removed all custom text formatting to preserve expander icons */
    
    /* Hide Streamlit's default expander arrow text (shows as "arrow_") - GLOBAL FIX */
    .streamlit-expanderHeader::before {
        content: none !important;
        display: none !important;
    }
    
    summary::marker {
        display: none !important;
    }
    
    details summary::before {
        display: none !important;
    }
    
    /* Hide first child that contains arrow text in ALL expanders */
    .streamlit-expanderHeader > div:first-child {
        font-size: 0 !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
    }
    
    /* Target the SVG container specifically */
    .streamlit-expanderHeader svg {
        display: inline-block !important;
        width: 16px !important;
        height: 16px !important;
        margin-right: 8px !important;
    }
    
    /* Hide any text node containing "arrow" */
    .streamlit-expanderHeader *:not(svg):not(p) {
        font-size: 0 !important;
    }
    
    /* Keep expander label text visible */
    .streamlit-expanderHeader p {
        font-size: 0.9rem !important;
        color: #cbd5e1 !important;
    }
    
    /* Sidebar specific styling */
    [data-testid="stSidebar"] .streamlit-expanderHeader p {
        color: #cbd5e1 !important;
        background: none !important;
    }
    
    /* Fix buttons - proper sizing and wrapping */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        height: auto !important;
        min-height: 3rem !important;
        padding: 0.75rem 1rem !important;
        text-align: left !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        line-height: 1.4 !important;
        display: block !important;
    }
    
    [data-testid="stSidebar"] .stButton > button p {
        white-space: normal !important;
        word-wrap: break-word !important;
        margin: 0 !important;
    }
    
    /* Fix expanders */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        width: 100% !important;
        height: auto !important;
        min-height: 3rem !important;
        padding: 1rem !important;
        white-space: normal !important;
        word-wrap: break-word !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader p {
        white-space: normal !important;
        word-wrap: break-word !important;
    }
    
    /* Fix markdown text */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        white-space: normal !important;
        word-wrap: break-word !important;
    }
    
    /* Ensure sidebar scrolls properly */
    [data-testid="stSidebar"] {
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# Force sidebar to display correctly (simplified - let Streamlit render naturally)
import streamlit.components.v1 as components

components.html("""
<script>
setTimeout(function() {
    const sidebar = parent.document.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        sidebar.style.display = 'block';
        sidebar.style.visibility = 'visible';
        
        // Find and replace the keyboard_double icon with hamburger menu
        const sidebarButtons = sidebar.querySelectorAll('button');
        sidebarButtons.forEach(button => {
            // Check if button contains keyboard or collapse-related content
            const buttonText = button.textContent || button.innerText;
            if (buttonText.includes('keyboard') || buttonText.includes('double') || button.getAttribute('kind') === 'header') {
                // Replace content with hamburger icon
                button.innerHTML = '<span style="font-size: 20px; color: white;">☰</span>';
                button.style.background = '#10b981';
                button.style.border = '2px solid white';
                button.style.borderRadius = '6px';
                button.style.padding = '0.4rem';
                button.style.width = '36px';
                button.style.height = '36px';
                button.style.display = 'flex';
                button.style.alignItems = 'center';
                button.style.justifyContent = 'center';
                button.style.cursor = 'pointer';
            }
        });
        
        // Remove "arrow_" text from expander headers
        const expanders = sidebar.querySelectorAll('.streamlit-expanderHeader');
        expanders.forEach(expander => {
            const walker = document.createTreeWalker(
                expander,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );
            
            let node;
            const nodesToRemove = [];
            while(node = walker.nextNode()) {
                if (node.textContent.includes('arrow')) {
                    nodesToRemove.push(node);
                }
            }
            
            nodesToRemove.forEach(n => {
                if (n.parentNode) {
                    n.parentNode.removeChild(n);
                }
            });
        });
    }
}, 500);

// Keep checking and updating
setInterval(function() {
    const sidebar = parent.document.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        // Keep replacing keyboard icon with hamburger
        const sidebarButtons = sidebar.querySelectorAll('button[kind="header"]');
        sidebarButtons.forEach(button => {
            if (!button.querySelector('span') || !button.textContent.includes('☰')) {
                button.innerHTML = '<span style="font-size: 20px; color: white;">☰</span>';
                button.style.background = '#10b981';
                button.style.border = '2px solid white';
                button.style.borderRadius = '6px';
                button.style.padding = '0.4rem';
                button.style.width = '36px';
                button.style.height = '36px';
                button.style.display = 'flex';
                button.style.alignItems = 'center';
                button.style.justifyContent = 'center';
            }
        });
        
        // Remove arrow text
        const expanders = sidebar.querySelectorAll('.streamlit-expanderHeader');
        expanders.forEach(expander => {
            const allElements = expander.querySelectorAll('*');
            allElements.forEach(el => {
                if (el.textContent.includes('arrow_') && !el.textContent.includes('▶')) {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                    el.style.fontSize = '0';
                }
            });
        });
    }
}, 1000);
</script>
""", height=0)

# Modern Dark Theme CSS
st.markdown(f"""
<style>
    /* Global font - Times New Roman for entire interface */
    * {{
        font-family: 'Times New Roman', Times, serif !important;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Dark background with Ethiopia map as FULL watermark */
    .stApp {{
        background: linear-gradient(135deg, rgba(10, 25, 41, 0.95) 0%, rgba(26, 35, 50, 0.95) 50%, rgba(13, 27, 42, 0.95) 100%),
                    url('data:image/png;base64,{ethiopia_map_base64 or ""}');
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: #e0e0e0;
    }}
    
    /* Main container */
    .main .block-container {{
        padding-top: 1rem;
        max-width: 1600px;
    }}
    
    /* Sidebar - Dark theme */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0d1520 0%, #1a1f2e 100%);
        border-right: 1px solid #2d3748;
    }}
    
    /* Sidebar header with logo */
    .sidebar-header {{
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1.5rem 1rem;
        text-align: center;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    
    .sidebar-logo {{
        width: 120px;
        height: 120px;
        margin: 0 auto 0.5rem auto;
        display: block;
        background: white;
        padding: 5px;
        border-radius: 50%;
    }}
    
    .sidebar-title {{
        color: #8B6F47;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        letter-spacing: 1px;
    }}
    
    .sidebar-subtitle {{
        color: #6B9BD1;
        font-size: 0.85rem;
        font-style: italic;
    }}
    
    /* Status card */
    .status-card {{
        background: rgba(74, 222, 128, 0.1);
        border-left: 3px solid #4ade80;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }}
    
    .status-title {{
        color: #4ade80;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}
    
    .status-item {{
        background: rgba(255,255,255,0.03);
        border-radius: 6px;
        padding: 0.7rem;
        margin: 0.5rem 0;
        color: #cbd5e1;
        font-size: 0.85rem;
    }}
    
    /* Quick questions section */
    .quick-questions-header {{
        color: #94a3b8;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 1.5rem 0 0.8rem 0;
        font-weight: 600;
    }}
    
    /* Buttons - dark theme with proper text handling */
    .stButton button {{
        background: rgba(255,255,255,0.05);
        color: #cbd5e1;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 6px;
        padding: 0.7rem 0.9rem;
        font-size: 0.85rem;
        width: 100%;
        text-align: left;
        transition: all 0.2s;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        line-height: 1.4 !important;
        min-height: 3rem !important;
        height: auto !important;
        display: flex !important;
        align-items: center !important;
        overflow: visible !important;
    }}
    
    .stButton button p {{
        margin: 0 !important;
        padding: 0 !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        line-height: 1.4 !important;
    }}
    
    .stButton button:hover {{
        background: rgba(74, 222, 128, 0.1);
        border-color: #4ade80;
        color: #4ade80;
    }}
    
    /* Main content header */
    .main-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 2rem;
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    
    .header-left {{
        display: flex;
        align-items: center;
        gap: 1rem;
    }}
    
    .header-logo {{
        width: 120px;
        height: 120px;
        background: white;
        padding: 5px;
        border-radius: 50%;
    }}
    
    .header-title {{
        color: #8B6F47;
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: 2px;
    }}
    
    .header-subtitle {{
        color: #6B9BD1;
        font-size: 0.9rem;
        font-style: italic;
    }}
    
    .header-right {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    
    .header-flag-wrapper {{
        width: 50px;
        height: 50px;
        border-radius: 50%;
        overflow: hidden;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        position: relative;
    }}
    
    .header-flag {{
        width: 120%;
        height: 120%;
        object-fit: cover;
        object-position: center;
        position: absolute;
        top: -10%;
        left: -10%;
    }}
    
    .header-text {{
        color: #e0e0e0;
        font-size: 0.9rem;
    }}
    
    /* Welcome section with map */
    .welcome-section {{
        position: relative;
        background: rgba(255,255,255,0.02);
        border-radius: 16px;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        overflow: hidden;
    }}
    
    .map-background {{
        position: absolute;
        right: -50px;
        top: 50%;
        transform: translateY(-50%);
        width: 500px;
        height: 500px;
        opacity: 0.15;
        background-image: url('data:image/png;base64,{ethiopia_map_base64 or ""}');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
    }}
    
    .welcome-text {{
        position: relative;
        z-index: 1;
    }}
    
    .welcome-title {{
        color: #e0e0e0;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }}
    
    .welcome-main {{
        color: #8B6F47;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    
    .welcome-main-et {{
        color: #4ade80;
    }}
    
    .welcome-subtitle {{
        color: #6B9BD1;
        font-size: 1.1rem;
        font-style: italic;
    }}
    
    /* SDG Category cards */
    .sdg-categories {{
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 0.8rem;
        margin: 2rem 0;
        position: relative;
        z-index: 1;
    }}
    
    .sdg-card {{
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 0.8rem 0.6rem;
        text-align: center;
        transition: all 0.3s;
        cursor: pointer;
        position: relative;
    }}
    
    .sdg-card:hover {{
        background: rgba(74, 222, 128, 0.1);
        border-color: #4ade80;
        transform: translateY(-3px);
    }}
    
    /* Tooltip styling */
    .sdg-card .tooltip {{
        visibility: hidden;
        width: 280px;
        background-color: rgba(15, 23, 42, 0.98);
        color: #e0e0e0;
        text-align: left;
        border-radius: 8px;
        padding: 12px;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -140px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.75rem;
        line-height: 1.4;
        border: 1px solid rgba(74, 222, 128, 0.3);
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }}
    
    .sdg-card .tooltip::after {{
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: rgba(15, 23, 42, 0.98) transparent transparent transparent;
    }}
    
    .sdg-card:hover .tooltip {{
        visibility: visible;
        opacity: 1;
    }}
    
    .tooltip-title {{
        color: #4ade80;
        font-weight: 600;
        font-size: 0.8rem;
        margin-bottom: 0.4rem;
    }}
    
    .sdg-icon {{
        font-size: 1.5rem;
        margin-bottom: 0.3rem;
    }}
    
    .sdg-title {{
        color: #e0e0e0;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }}
    
    .sdg-subtitle {{
        color: #94a3b8;
        font-size: 0.65rem;
    }}
    
    /* Chat input - green accent - FIXED for typing */
    .stChatInput > div {{
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(74, 222, 128, 0.3) !important;
        border-radius: 30px !important;
    }}
    
    .stChatInput input {{
        color: #e0e0e0 !important;
        background: transparent !important;
        z-index: 100 !important;
        pointer-events: auto !important;
    }}
    
    .stChatInput input::placeholder {{
        color: #64748b !important;
    }}
    
    .stChatInput textarea {{
        color: #e0e0e0 !important;
        background: transparent !important;
        z-index: 100 !important;
        pointer-events: auto !important;
    }}
    
    /* Chat messages */
    .stChatMessage {{
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        color: #4ade80;
        font-size: 1.3rem;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: #94a3b8;
    }}
    
    /* Expander for FAQ dropdowns - fix text overflow */
    .streamlit-expanderHeader {{
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        color: #cbd5e1 !important;
        font-size: 0.9rem !important;
        padding: 0.9rem 1rem !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        line-height: 1.4 !important;
        min-height: 3rem !important;
        height: auto !important;
    }}
    
    .streamlit-expanderHeader p {{
        margin: 0 !important;
        padding: 0 !important;
        white-space: normal !important;
        line-height: 1.4 !important;
    }}
    
    .streamlit-expanderHeader:hover {{
        background: rgba(74, 222, 128, 0.1) !important;
        border-color: #4ade80 !important;
    }}
    
    .streamlit-expanderContent {{
        background: rgba(0,0,0,0.3) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 0 0 8px 8px !important;
        padding: 0.5rem !important;
    }}
    
    /* Clear button styling */
    .clear-button {{
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        color: #ef4444 !important;
    }}
    
    .clear-button:hover {{
        background: rgba(239, 68, 68, 0.2) !important;
        border-color: #ef4444 !important;
    }}
    
    /* Text color fixes */
    p, span, div {{
        color: #e0e0e0;
    }}
    
    /* Footer */
    .footer-text {{
        text-align: center;
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding: 1rem;
    }}
</style>
""", unsafe_allow_html=True)

# Initialize session state with proper cleanup handling
if 'rag' not in st.session_state:
    try:
        with st.spinner('🚀 Initializing LangChain Dual-Engine RAG...'):
            st.session_state.rag = LangChainDualEngineRAG()
            
            # Load conversation history from file ONLY on first load
            st.session_state.conversations = load_conversation_history()
            st.session_state.active_conversation = None
            st.session_state.current_messages = []
            st.session_state.query_count = 0
            st.session_state.init_time = True
            st.session_state._first_load = True
    except Exception as e:
        st.error(f"❌ Error initializing RAG system: {str(e)}")
        st.stop()

# Register cleanup handler for when script ends
import atexit

def cleanup_connections():
    """Clean up RAG connections on exit"""
    if 'rag' in st.session_state:
        try:
            pass  # LangChain handles cleanup automatically
        except:
            pass

atexit.register(cleanup_connections)

# ===== SIDEBAR =====
with st.sidebar:
    # Sidebar header with logo
    logo_img = f'<img src="data:image/png;base64,{ess_logo_base64}" class="sidebar-logo">' if ess_logo_base64 else '<div style="font-size: 3rem;">🇪🇹</div>'
    
    st.markdown(f"""
    <div class="sidebar-header">
        {logo_img}
        <div class="sidebar-title">ET ESS RAG Bot</div>
        <div class="sidebar-subtitle">Intelligent Statistical Data Assistant & Policy Analyst</div>
        <div style="margin-top: 0.8rem; font-size: 0.75rem; font-weight: 600; color: #4ade80; letter-spacing: 1.5px; text-align: center;">
            "YOUR RELIABLE DATA SOURCE"
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Status card with connection indicator
    provider = os.getenv("LLM_PROVIDER", "ollama").upper()
    
    # Show initialization success message once
    if st.session_state.get('init_time', False):
        st.success("✅ RAG Agent initialized successfully!", icon="✅")
        # Show conversation restore info if any conversations exist
        if st.session_state.conversations:
            st.info(f"📂 Restored {len(st.session_state.conversations)} previous conversation(s) from history", icon="📂")
        st.session_state.init_time = False
    
    st.markdown(f"""
    <div class="status-card">
        <div class="status-title">● Dual-Engine System Ready</div>
        <div class="status-item">Engine A: PDF RAG (ChromaDB)</div>
        <div class="status-item">Engine B: Excel SQL (Pandas)</div>
        <div class="status-item">LLM: Llama-3.1-8B via Ollama (LangChain)</div>
    </div>
    """, unsafe_allow_html=True)
    
    # EXPORT SECTION - Export conversation to PDF/Word (Collapsible)
    st.markdown("---")
    
    # Initialize export visibility state
    if 'export_expanded' not in st.session_state:
        st.session_state.export_expanded = False
    
    # Check if there's a current conversation to export
    if st.session_state.current_messages and len(st.session_state.current_messages) > 0:
        try:
            from src.export import PDFExporter, WordExporter
            EXPORT_AVAILABLE = True
        except ImportError:
            # Try to provide helpful error message
            EXPORT_AVAILABLE = False
        
        # Toggle button with arrow icon
        arrow_icon = "▼" if st.session_state.export_expanded else "▶"
        if st.button(f"{arrow_icon} 📤 EXPORT", use_container_width=True, key="export_toggle"):
            st.session_state.export_expanded = not st.session_state.export_expanded
        
        # Show export options if expanded
        if st.session_state.export_expanded:
            if EXPORT_AVAILABLE:
                # PDF Export Button
                if st.button("📄 Export to PDF", use_container_width=True, key="export_pdf"):
                    with st.spinner("Generating PDF..."):
                        try:
                            pdf_exporter = PDFExporter()
                            result = pdf_exporter.export_conversation(st.session_state.current_messages)
                            
                            if result['success']:
                                # Provide download button
                                with open(result['filepath'], 'rb') as f:
                                    st.download_button(
                                        label="📥 Download PDF",
                                        data=f,
                                        file_name=result['filename'],
                                        mime="application/pdf",
                                        use_container_width=True,
                                        key="download_pdf"
                                    )
                                st.success(f"✅ PDF generated: {result['filename']}")
                            else:
                                st.error(f"❌ Error: {result['error']}")
                        except Exception as e:
                            st.error(f"❌ Export failed: {str(e)}")
                
                # Word Export Button
                if st.button("📝 Export to Word", use_container_width=True, key="export_word"):
                    with st.spinner("Generating Word document..."):
                        try:
                            word_exporter = WordExporter()
                            result = word_exporter.export_conversation(st.session_state.current_messages)
                            
                            if result['success']:
                                # Provide download button
                                with open(result['filepath'], 'rb') as f:
                                    st.download_button(
                                        label="📥 Download Word",
                                        data=f,
                                        file_name=result['filename'],
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                        use_container_width=True,
                                        key="download_word"
                                    )
                                st.success(f"✅ Word document generated: {result['filename']}")
                            else:
                                st.error(f"❌ Error: {result['error']}")
                        except Exception as e:
                            st.error(f"❌ Export failed: {str(e)}")
                
                # Info about exports
                st.caption("💡 Exports saved to /exports folder")
            else:
                st.warning("📦 Export libraries not available")
                st.code("pip install reportlab python-docx", language="bash")
        
    else:
        # Show export button in disabled state
        arrow_icon = "▼" if st.session_state.export_expanded else "▶"
        if st.button(f"{arrow_icon} 📤 EXPORT", use_container_width=True, key="export_toggle_disabled"):
            st.session_state.export_expanded = not st.session_state.export_expanded
        
        if st.session_state.export_expanded:
            st.info("💡 Ask a question first to enable export", icon="💡")
    
    st.markdown("---")
    
    # Quick questions with FAQ dropdowns - OPTIMIZED (minimal rerun delay)
    st.markdown('<div class="quick-questions-header">QUICK QUESTIONS</div>', unsafe_allow_html=True)
    
    # Initialize expanded state for each category
    if 'expanded_categories' not in st.session_state:
        st.session_state.expanded_categories = set()
    
    # Track if we need to rerun (only once at the end)
    needs_rerun = False
    
    for category, questions in FAQ_DATABASE.items():
        # Create a unique key for this category
        cat_key = category.replace(" ", "_").replace("&", "and")
        is_expanded = cat_key in st.session_state.expanded_categories
        
        # Create clickable category button with arrow on the LEFT
        arrow = "▼" if is_expanded else "▶"
        button_text = f"{arrow} {category}"
        
        if st.button(button_text, key=f"toggle_{cat_key}", use_container_width=True):
            if is_expanded:
                st.session_state.expanded_categories.remove(cat_key)
            else:
                st.session_state.expanded_categories.add(cat_key)
            needs_rerun = True
        
        # Show questions if expanded
        if is_expanded:
            for question in questions:
                if st.button(f"    • {question}", key=f"faq_{question[:30]}", use_container_width=True):
                    # Just fill the input box, don't auto-submit
                    st.session_state.prefilled_question = question
                    needs_rerun = True
    
    # Only rerun once if needed
    if needs_rerun:
        st.rerun()
    
    # Conversation History Section with collapse/expand
    st.markdown("---")
    
    # Initialize history section expanded state
    if 'history_section_expanded' not in st.session_state:
        st.session_state.history_section_expanded = False
    
    # Count conversations
    conv_count = len(st.session_state.conversations)
    history_arrow = "▼" if st.session_state.history_section_expanded else "▶"
    
    if st.button(f"{history_arrow} CONVERSATION HISTORY ({conv_count})", key="toggle_history_section", use_container_width=True):
        st.session_state.history_section_expanded = not st.session_state.history_section_expanded
        st.rerun()
    
    # Show conversations if section is expanded
    if st.session_state.history_section_expanded and st.session_state.conversations:
        # Initialize history expanded state
        if 'expanded_history' not in st.session_state:
            st.session_state.expanded_history = set()
        
        for idx, conv in enumerate(reversed(st.session_state.conversations)):
            conv_idx = len(st.session_state.conversations) - 1 - idx
            first_question = conv['messages'][0]['content'] if conv['messages'] else "Empty conversation"
            # Truncate long questions
            question_preview = first_question[:40] + "..." if len(first_question) > 40 else first_question
            
            hist_key = f"hist_{conv_idx}"
            is_expanded = hist_key in st.session_state.expanded_history
            
            # Highlight active conversation
            is_active = st.session_state.active_conversation == conv_idx
            button_style = "🟢 " if is_active else "• "
            
            arrow = "▼" if is_expanded else "▶"
            if st.button(f"{arrow} {button_style}{question_preview}", key=f"conv_{conv_idx}", use_container_width=True):
                if is_expanded:
                    st.session_state.expanded_history.remove(hist_key)
                else:
                    st.session_state.expanded_history.add(hist_key)
                st.rerun()
            
            # Show conversation details when expanded
            if is_expanded:
                if st.button(f"    📂 Load Conversation", key=f"load_{conv_idx}", use_container_width=True):
                    st.session_state.active_conversation = conv_idx
                    st.session_state.current_messages = conv['messages']
                    st.rerun()
                
                # Show Q&A count
                q_count = len([m for m in conv['messages'] if m['role'] == 'user'])
                st.markdown(f"<div style='padding-left: 1.5rem; color: #94a3b8; font-size: 0.8rem;'>{q_count} question(s)</div>", unsafe_allow_html=True)
    elif st.session_state.history_section_expanded and not st.session_state.conversations:
        st.markdown("<div style='color: #64748b; font-size: 0.85rem; text-align: center; padding: 1rem;'>No conversations yet</div>", unsafe_allow_html=True)
    
    # Clear cache button
    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
    if st.button("🗑️ Clear All History", key="clear_chat", use_container_width=True, type="secondary"):
        st.session_state.conversations = []
        st.session_state.current_messages = []
        st.session_state.active_conversation = None
        st.session_state.query_count = 0
        # Also clear from file
        save_conversation_history([])
        st.rerun()
    
    # About section at bottom with custom expand/collapse - OPTIMIZED
    st.markdown("---")
    
    # Initialize about expanded state
    if 'about_expanded' not in st.session_state:
        st.session_state.about_expanded = False
    
    # About toggle button
    about_arrow = "▼" if st.session_state.about_expanded else "▶"
    about_clicked = st.button(f"{about_arrow} ℹ️ ABOUT", key="toggle_about", use_container_width=True)
    
    # Show about content if expanded
    if st.session_state.about_expanded:
        st.markdown("""
        **ET ESS RAG BOT**  
        *AI-Powered Statistical Data Assistant for Ethiopia*
        
        **Purpose:**  
        Provide instant access to Ethiopia's comprehensive statistical data through AI-powered search and analysis
        
        **Dual-Engine Architecture:**  
        • **Engine A:** PDF RAG - ESS Statistical Reports & Policy Documents  
        • **Engine B:** SQL Query - UN SDG Database (17 Goals, 12,037 indicators)  
        
        **Data Coverage:**  
        • **40,325** document chunks from ESS monthly reports  
        • **12,037** SDG indicators for Ethiopia  
        • **Statistics:** CPI/Inflation, Agriculture, Population, Business Surveys, Household Data  
        • **Multi-source validation:** ESS Reports + UN SDG Database
        
        **Technology Stack:**  
        • **LLM:** Llama 3.2-1B via Ollama (Local)  
        • **RAG Framework:** LangChain with Hybrid Search (MMR)  
        • **Vector Store:** ChromaDB with HuggingFace embeddings  
        • **SQL Database:** SQLite for structured indicators  
        • **Calendar Support:** Ethiopian Calendar (EC) ↔ Gregorian Calendar (GC)  
        • **Frontend:** Streamlit
        
        **Key Features:**  
        • Anti-hallucination validation (source verification)  
        • Hybrid search for improved accuracy  
        • Automatic query routing (PDF/SQL/Both)  
        • Ethiopian & Gregorian calendar disambiguation  
        • Full source attribution with document previews
        
        **Developer:** Yonas Abiyu Gion  
        **Institution:** Bahir Dar University  
        **Client:** Ethiopian Statistical Service
        
        ---
        
        ✅ **Production Ready**  
        Cost: $0 (100% Free - Local LLM via Ollama)
        """)
    
    # Handle about toggle after rendering to avoid delay
    if about_clicked:
        st.session_state.about_expanded = not st.session_state.about_expanded
        st.rerun()
# ===== MAIN CONTENT =====

# Top header
# Use the actual flag image (with wrapper to remove white padding)
if ethiopia_flag_base64:
    flag_html = f'<div class="header-flag-wrapper"><img src="data:image/png;base64,{ethiopia_flag_base64}" class="header-flag"></div>'
else:
    flag_html = '<div class="header-flag-wrapper"></div>'

if ess_logo_base64:
    logo_img = f'<img src="data:image/png;base64,{ess_logo_base64}" class="header-logo">'
else:
    logo_img = '<div style="font-size: 2.5rem;">🇪🇹</div>'

st.markdown(f"""
<div class="main-header">
    <div class="header-left">
        {logo_img}
        <div>
            <div class="header-title">ET ESS RAG Bot</div>
            <div class="header-subtitle">Intelligent Statistical Data Assistant & Policy Analyst</div>
        </div>
    </div>
    <div class="header-right">
        <div class="header-text">
            <strong>Ethiopia</strong><br>
            <span style="font-size: 0.75rem;">Building a Sustainable Future</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Welcome section with map background
st.markdown(f"""
<div class="welcome-section">
    <div class="map-background"></div>
    <div class="welcome-text">
        <div class="welcome-title">Welcome to</div>
        <div class="welcome-main"><span class="welcome-main-et">ET</span> ESS RAG Bot</div>
        <div style="width: 100px; height: 3px; background: linear-gradient(90deg, #4ade80 0%, transparent 100%); margin: 1rem auto;"></div>
        <div class="welcome-subtitle">AI-Powered Statistical Data Assistant for Ethiopia</div>
        <div style="margin-top: 1.5rem; font-size: 1.1rem; font-weight: 600; color: #4ade80; letter-spacing: 2px; text-transform: uppercase;">
            "YOUR RELIABLE DATA SOURCE"
        </div>
        <div style="margin-top: 0.3rem; font-size: 0.85rem; color: #94a3b8; font-style: italic;">
            Ethiopian Statistical Service
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Survey Category cards with tooltips
st.markdown("""
<div class="sdg-categories">
    <div class="sdg-card">
        <div class="sdg-icon">💰</div>
        <div class="sdg-title">Price Survey</div>
        <div class="sdg-subtitle">CPI & Inflation</div>
        <span class="tooltip">
            <div class="tooltip-title">Price Statistics</div>
            The Consumer Price Index (CPI), one of the most important economic indicators, measures the average change over time in the prices paid by consumers for a representative basket of goods and services. Published monthly, the CPI is the principal measure of inflation and changes in the cost of living. These statistics support evidence-based policy decisions, wage and income adjustments, business planning, and economic research.
        </span>
    </div>
    <div class="sdg-card">
        <div class="sdg-icon">🌾</div>
        <div class="sdg-title">Agriculture Survey</div>
        <div class="sdg-subtitle">Crops & Livestock</div>
        <span class="tooltip">
            <div class="tooltip-title">Agricultural Statistics</div>
            Agricultural statistics in Ethiopia are produced from several data sources. The most important is the Agricultural Sample Survey, which is conducted twice a year to cover the country's two main cropping seasons. The largest survey covers the Meher (main) season and produces annual reports on topics such as crops, livestock, and farm management. Another sample survey is conducted during the Belg (short rainy) season, focusing mainly on crop production. Data from these surveys are also combined with other sources in agricultural statistical abstracts.
        </span>
    </div>
    <div class="sdg-card">
        <div class="sdg-icon">🏢</div>
        <div class="sdg-title">Business Survey</div>
        <div class="sdg-subtitle">Economic Sectors</div>
        <span class="tooltip">
            <div class="tooltip-title">Business Statistics</div>
            Business statistics are produced from several data sources and statistical operations covering the country's non-agricultural economic sectors. These statistics provide reliable and timely information to support economic planning, industrial development, private sector analysis, employment monitoring, investment promotion, and national accounts compilation.
        </span>
    </div>
    <div class="sdg-card">
        <div class="sdg-icon">🏠</div>
        <div class="sdg-title">Household Survey</div>
        <div class="sdg-subtitle">Budget & Labour</div>
        <span class="tooltip">
            <div class="tooltip-title">Household Statistics</div>
            The Household Budget and Labour Statistics (HBLS) program of the Ethiopian Statistics Service (ESS) conducts nationally representative household surveys to produce official statistics on living standards, labour market conditions, household welfare, consumption, and poverty. These statistics provide essential evidence for employment policies, social protection programs, poverty reduction strategies, and national development planning.
        </span>
    </div>
    <div class="sdg-card">
        <div class="sdg-icon">👥</div>
        <div class="sdg-title">Population Census</div>
        <div class="sdg-subtitle">National Count</div>
        <span class="tooltip">
            <div class="tooltip-title">Population and Housing Census</div>
            The Population and Housing Census is the largest statistical operation conducted by the Ethiopian Statistics Service (ESS). It provides the most comprehensive picture of Ethiopia's population, households, and housing conditions. Ethiopia has conducted three national censuses: 1984, 1994, and 2007.
        </span>
    </div>
    <div class="sdg-card">
        <div class="sdg-icon">💚</div>
        <div class="sdg-title">Population Survey</div>
        <div class="sdg-subtitle">Health & Demographics</div>
        <span class="tooltip">
            <div class="tooltip-title">Demographic and Health Survey</div>
            The Ethiopian Demographic and Health Survey (EDHS) is a nationally representative survey conducted every five years by the Ethiopian Statistics Service (ESS) to provide comprehensive information on the health and demographic status of the population. The survey serves as a key source of data for monitoring health outcomes, evaluating national programs, and supporting evidence-based policy and planning.
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize prefilled question if not exists
if 'prefilled_question' not in st.session_state:
    st.session_state.prefilled_question = ""

# Display chat history with sources - ONLY CURRENT CONVERSATION
for idx, message in enumerate(st.session_state.current_messages):
    if message["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar=f"data:image/png;base64,{ess_logo_base64}" if ess_logo_base64 else "🤖"):
            st.markdown(message["content"])
            
            # Show metrics if available
            if "metadata" in message:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("⏱️ Response Time", f"{message['metadata']['time']:.2f}s")
                with col2:
                    # Calculate unique file count from sources
                    sources_data = message['metadata'].get('sources_data', [])
                    if sources_data:
                        # Count unique files
                        unique_files = set()
                        for source in sources_data:
                            if isinstance(source, dict):
                                metadata = source.get('metadata', {})
                                filename = metadata.get('filename', metadata.get('source', 'Unknown'))
                                unique_files.add(filename)
                        file_count = len(unique_files)
                    else:
                        file_count = 0
                    
                    st.metric("📚 Sources", file_count)
                with col3:
                    st.metric("🎯 Relevance", f"{message['metadata']['top_score']:.2f}")
                
                # Custom Sources expand/collapse
                if 'sources_expanded' not in st.session_state:
                    st.session_state.sources_expanded = {}
                
                sources_key = f"sources_history_{idx}"
                
                if sources_key not in st.session_state.sources_expanded:
                    st.session_state.sources_expanded[sources_key] = False
                
                sources_arrow = "▼" if st.session_state.sources_expanded[sources_key] else "▶"
                
                # Only show sources if answer actually used them (not "I don't have data")
                answer_text = message['content'].lower()
                has_no_data = any(phrase in answer_text for phrase in [
                    "i don't have",
                    "i do not have",
                    "no specific data",
                    "no data available",
                    "cannot find",
                    "not available in the context"
                ])
                
                if has_no_data:
                    # Don't show sources button if answer says no data
                    st.caption("ℹ️ No source data available for this query")
                else:
                    # Show sources button only if data was actually found
                    if st.button(f"{sources_arrow} 📖 Sources ({message['metadata']['sources']})", key=f"toggle_{sources_key}"):
                        st.session_state.sources_expanded[sources_key] = not st.session_state.sources_expanded[sources_key]
                        st.rerun()
                
                if st.session_state.sources_expanded[sources_key] and 'sources_data' in message['metadata']:
                    # Use pre-enhanced sources if available
                    if 'enhanced_sources' in message['metadata']:
                        enhanced_sources = message['metadata']['enhanced_sources']
                        use_enhanced = True
                    else:
                        # Try to enhance, but fallback to basic if not available
                        use_enhanced = False
                        try:
                            from src.citations.citation_enhancer import CitationEnhancer
                            enhancer = CitationEnhancer()
                            
                            sources_for_enhancement = []
                            for source in message['metadata']['sources_data']:
                                if isinstance(source, dict):
                                    goal_num = source.get('metadata', {}).get('goal_number', 0)
                                    score = 0.95
                                else:
                                    goal_num = source.payload.get('goal_number', 0)
                                    score = source.score
                                
                                sources_for_enhancement.append({
                                    'goal': goal_num,
                                    'score': score,
                                })
                            
                            enhanced_sources = enhancer.enhance_sources(sources_for_enhancement)
                            use_enhanced = True
                        except (ImportError, Exception) as e:
                            # Citations module not available or error, show basic sources
                            use_enhanced = False
                    
                    if use_enhanced and enhanced_sources:
                        # Display enhanced sources with Excel download
                        st.markdown("### 📚 Source Documents")
                        st.markdown("*Download the complete datasets used to generate this answer:*")
                        st.markdown("---")
                        
                        for i, source in enumerate(enhanced_sources, 1):
                            goal = source.get('goal', 'N/A')
                            score = source.get('score', 0.0)
                            source_name = source.get('source_name', 'Unknown Source')
                            data_year = source.get('data_year', 'N/A')
                            excel_file = source.get('excel_file')
                            
                            # Display in columns for better layout
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"📊 **SDG Goal {goal}** - {source_name}")
                                st.caption(f"📅 Data Year: {data_year} • Relevance: {score:.1%}")
                            
                            with col2:
                                # Add Excel download button
                                if excel_file and os.path.exists(excel_file):
                                    with open(excel_file, 'rb') as f:
                                        st.download_button(
                                            label="📥 Download",
                                            data=f,
                                            file_name=os.path.basename(excel_file),
                                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                            key=f"download_{sources_key}_{i}",
                                            use_container_width=True
                                        )
                                else:
                                    # Show info message instead of error for missing files
                                    st.caption("ℹ️ Source data only")
                            
                            st.markdown("---")
                    else:
                        # Display file-based sources (fallback when citations module not available)
                        sources_data = message['metadata'].get('sources_data', [])
                        
                        # Group sources by file (PDF or Excel)
                        sources_by_file = {}
                        excel_sources = []  # Track Excel sources from SQL queries
                        
                        for source in sources_data[:10]:  # Check up to 10 sources
                            if isinstance(source, dict):
                                source_type_check = source.get('type', 'pdf')
                                
                                # Handle SQL sources differently
                                if source_type_check == 'sql':
                                    metadata = source.get('metadata', {})
                                    excel_sources.append({
                                        'filename': metadata.get('filename', 'Unknown'),
                                        'goal_number': metadata.get('goal_number', 0)
                                    })
                                    continue
                                
                                # Handle PDF sources
                                metadata = source.get('metadata', {})
                                source_type = metadata.get('source', 'Unknown')
                                filename = metadata.get('filename', 'Unknown')
                            else:
                                metadata = source.metadata if hasattr(source, 'metadata') else {}
                                source_type = metadata.get('source', 'Unknown')
                                filename = metadata.get('filename', 'Unknown')
                            
                            if filename not in sources_by_file:
                                sources_by_file[filename] = {
                                    'source_type': source_type,
                                    'count': 0
                                }
                            sources_by_file[filename]['count'] += 1
                        
                        # Check if this query used SQL database (for Excel sources)
                        query_engines = message['metadata'].get('engines', [])
                        has_sql = 'SQL Database' in query_engines
                        
                        st.markdown("### 📚 Source Documents")
                        st.markdown(f"*{len(sources_by_file)} unique document(s) from {len(sources_data)} total chunks*")
                        st.markdown("---")
                        
                        # Display PDF sources
                        pdf_count = 0
                        for filename, data in sources_by_file.items():
                            source_type = data['source_type']
                            
                            # Determine file path
                            if source_type == 'AfDB':
                                file_path = os.path.join("data", "raw", "afdb_reports", filename)
                                file_type = "PDF"
                                mime_type = "application/pdf"
                                icon = "📄"
                            elif source_type == 'ESS':
                                file_path = os.path.join("data", "raw", "ess_reports", "pdfs", filename)
                                file_type = "PDF"
                                mime_type = "application/pdf"
                                icon = "📄"
                            else:
                                continue  # Skip unknown types
                            
                            pdf_count += 1
                            
                            # Display file info
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"{icon} **{source_type} Report**")
                                st.caption(f"📎 {filename}")
                                if not os.path.exists(file_path):
                                    st.caption("💾 Referenced from vector database")
                            
                            with col2:
                                # Download button - only show if file exists
                                if os.path.exists(file_path):
                                    with open(file_path, 'rb') as f:
                                        st.download_button(
                                            label="📥 Download",
                                            data=f,
                                            file_name=filename,
                                            mime=mime_type,
                                            key=f"download_{sources_key}_{pdf_count}",
                                            use_container_width=True
                                        )
                                else:
                                    # Show info message instead of error
                                    st.caption("ℹ️ Source data only")
                            
                            st.markdown("---")
                        
                        # Display Excel sources if SQL was used OR if excel_sources found
                        if has_sql or excel_sources:
                            st.markdown(f"📊 **UN SDG Database (Excel)**")
                            st.caption("📎 Sustainable Development Goals indicators for Ethiopia")
                            
                            # If we have explicit excel sources from the query result
                            if excel_sources:
                                st.caption(f"📌 Relevant SDG Files: {len(excel_sources)} file(s)")
                                
                                for excel_source in excel_sources:
                                    filename = excel_source['filename']
                                    goal_num = excel_source.get('goal_number', 0)
                                    
                                    excel_file = os.path.join("data", "raw", "un_sdg_excel", filename)
                                    
                                    # Always display the source, even if file doesn't exist locally
                                    col1, col2 = st.columns([3, 1])
                                    with col1:
                                        st.markdown(f"📊 **UN SDG Goal {goal_num}**")
                                        st.caption(f"📎 {filename}")
                                    with col2:
                                        if os.path.exists(excel_file):
                                            with open(excel_file, 'rb') as f:
                                                st.download_button(
                                                    label="📥 Download",
                                                    data=f,
                                                    file_name=filename,
                                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                                    key=f"download_excel_{sources_key}_{goal_num}",
                                                    use_container_width=True
                                                )
                                        else:
                                            st.caption("💾 Source data only")
                                    st.markdown("---")
                            else:
                                # Fallback: detect from query text
                                # Show relevant SDG goal files
                                # Detect which goals might be relevant from the query
                                query_text = message.get('content', '').lower()
                                relevant_goals = []
                                
                                # Map keywords to SDG goals
                                goal_keywords = {
                                    1: ['poverty', 'poor'],
                                    2: ['hunger', 'food', 'agriculture', 'livestock', 'animal', 'cattle', 'farming'],
                                    3: ['health', 'medical', 'disease'],
                                    4: ['education', 'school'],
                                    5: ['gender', 'women'],
                                    6: ['water', 'sanitation'],
                                    7: ['energy', 'electricity'],
                                    8: ['employment', 'economic growth'],
                                    9: ['infrastructure', 'industry'],
                                    10: ['inequality', 'income'],
                                    11: ['cities', 'urban'],
                                    13: ['climate'],
                                    17: ['partnership']
                                }
                                
                                for goal_num, keywords in goal_keywords.items():
                                    if any(kw in query_text for kw in keywords):
                                        relevant_goals.append(goal_num)
                                
                                # If no specific goals detected, offer all SDG files
                                if not relevant_goals:
                                    st.caption("💡 All 17 SDG goal datasets available")
                                    # Provide link to SDG data folder
                                    excel_folder = os.path.join("data", "raw", "un_sdg_excel")
                                    if os.path.exists(excel_folder):
                                        st.info("📁 SDG data files are located in: `data/raw/un_sdg_excel/`")
                                else:
                                    # Show download buttons for relevant goals
                                    st.caption(f"📌 Relevant SDG Goals: {', '.join(map(str, relevant_goals))}")
                                    
                                    for goal_num in relevant_goals[:3]:  # Show top 3
                                        excel_file = os.path.join("data", "raw", "un_sdg_excel", f"Goal{goal_num}.xlsx")
                                        if os.path.exists(excel_file):
                                            col1, col2 = st.columns([3, 1])
                                            with col1:
                                                st.caption(f"Goal {goal_num} indicators")
                                            with col2:
                                                with open(excel_file, 'rb') as f:
                                                    st.download_button(
                                                        label="📥 Download",
                                                        data=f,
                                                        file_name=f"Goal{goal_num}.xlsx",
                                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                                        key=f"download_excel_{sources_key}_{goal_num}",
                                                        use_container_width=True
                                                    )
                        
                        # Show message if no ESS PDF sources found
                        if pdf_count == 0:
                            if has_sql or excel_sources:
                                # SDG has data, but ESS doesn't
                                st.info("ℹ️ No ESS PDF documents found for this query (UN SDG Database provided data above)")
                            else:
                                # Neither engine has data
                                st.info("ℹ️ No source documents available for this response")
                
                # RELATED QUESTIONS (Phase 7C - Task 7C.4)
                # Display AI-generated follow-up questions
                if message.get('metadata', {}).get('related_questions'):
                    st.markdown("---")
                    st.markdown("### 💡 Related Questions")
                    st.caption("Explore these related topics:")
                    
                    for i, question in enumerate(message['metadata']['related_questions']):
                        # Create clickable button for each question
                        if st.button(
                            f"💬 {question}",
                            key=f"related_{idx}_{i}",
                            use_container_width=True
                        ):
                            # Submit the question automatically
                            st.session_state.user_input = question
                            st.rerun()
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if st.button("PNG", key=f"export_png_{idx}"):
                                    export_result = generator.export_chart(
                                        fig, f"chart_{idx}", "png"
                                    )
                                    if export_result['success']:
                                        with open(export_result['file_path'], 'rb') as f:
                                            st.download_button(
                                                "⬇️ Download PNG",
                                                f,
                                                file_name=export_result['filename'],
                                                mime="image/png"
                                            )
                            
                            with col2:
                                if st.button("SVG", key=f"export_svg_{idx}"):
                                    export_result = generator.export_chart(
                                        fig, f"chart_{idx}", "svg"
                                    )
                                    if export_result['success']:
                                        with open(export_result['file_path'], 'rb') as f:
                                            st.download_button(
                                                "⬇️ Download SVG",
                                                f,
                                                file_name=export_result['filename'],
                                                mime="image/svg+xml"
                                            )
                            
                            with col3:
                                if st.button("PDF", key=f"export_pdf_chart_{idx}"):
                                    export_result = generator.export_chart(
                                        fig, f"chart_{idx}", "pdf"
                                    )
                                    if export_result['success']:
                                        with open(export_result['file_path'], 'rb') as f:
                                            st.download_button(
                                                "⬇️ Download PDF",
                                                f,
                                                file_name=export_result['filename'],
                                                mime="application/pdf"
                                            )

# Chat interface - handle new messages
# If there's a prefilled question, show it in a special input area
if st.session_state.prefilled_question:
    col1, col2 = st.columns([5, 1])
    with col1:
        st.text_input("Your Question (Edit if needed):", value=st.session_state.prefilled_question, key="editable_question", label_visibility="collapsed")
    with col2:
        if st.button("Send", type="primary", use_container_width=True):
            prompt = st.session_state.editable_question
            st.session_state.prefilled_question = ""  # Clear after sending
            
            # If starting new conversation
            if st.session_state.active_conversation is None:
                st.session_state.current_messages = []
                st.session_state.active_conversation = len(st.session_state.conversations)
            
            # Add user message
            st.session_state.current_messages.append({"role": "user", "content": prompt})
            st.session_state.query_count += 1
            
            with st.spinner("🤔 Analyzing data..."):
                result = st.session_state.rag.query(prompt, verbose=False)
            
            # Store message with sources data
            # Handle both old format (objects with .score) and new format (dicts)
            if result.get('sources') and len(result['sources']) > 0:
                # Check if sources are dicts or objects
                first_source = result['sources'][0]
                if isinstance(first_source, dict):
                    top_score = 0.95  # Default score for LangChain sources (no scores)
                else:
                    top_score = first_source.score
            else:
                top_score = 0
            
            message_metadata = {
                "sources": result['num_sources'], 
                "time": result['total_time'], 
                "top_score": top_score,
                "sources_data": result['sources']
            }
            
            # RELATED QUESTIONS GENERATION (Phase 7C - Task 7C.4)
            # Generate follow-up questions using LLM
            try:
                from src.citations.related_questions import RelatedQuestionsGenerator
                
                # Extract SDG goal from result - handle both old and new formats
                sdg_goal = 1  # Default
                if result.get('sources') and len(result['sources']) > 0:
                    first_source = result['sources'][0]
                    if isinstance(first_source, dict):
                        sdg_goal = first_source.get('metadata', {}).get('goal_number', 1)
                    else:
                        sdg_goal = first_source.payload.get('goal_number', 1)
                
                # Generate questions
                question_generator = RelatedQuestionsGenerator(groq_client)
                related_questions = question_generator.generate_related_questions(
                    query=prompt,
                    answer=result['answer'],
                    sdg_goal=sdg_goal,
                    language="en",  # TODO: Add language detection
                    max_questions=4
                )
                
                if related_questions:
                    message_metadata['related_questions'] = related_questions
            except Exception as e:
                print(f"⚠️ Related questions generation failed: {e}")
                # Continue without related questions
            
            # ENHANCE CITATIONS (Phase 7C - Revised)
            # Add source metadata and Excel download paths
            try:
                from src.citations.citation_enhancer import CitationEnhancer
                enhancer = CitationEnhancer()
                sources_for_enhancement = []
                seen_goals = set()
                
                for source in result['sources']:
                    # Handle both dict and object formats
                    if isinstance(source, dict):
                        goal_num = source.get('metadata', {}).get('goal_number', 0)
                        score = 0.95  # Default score for dict format
                    else:
                        goal_num = source.payload.get('goal_number', 0)
                        score = source.score
                    
                    if goal_num not in seen_goals:
                        seen_goals.add(goal_num)
                        sources_for_enhancement.append({
                            'goal': goal_num,
                            'score': score,
                        })
                
                enhanced_sources = enhancer.enhance_sources(sources_for_enhancement)
                message_metadata['enhanced_sources'] = enhanced_sources
            except Exception as e:
                print(f"⚠️ Citation enhancement failed: {e}")
            
            st.session_state.current_messages.append({
                "role": "assistant",
                "content": result['answer'],
                "metadata": message_metadata
            })
            
            # Save/update conversation in history
            if st.session_state.active_conversation >= len(st.session_state.conversations):
                st.session_state.conversations.append({
                    'messages': st.session_state.current_messages.copy(),
                    'timestamp': st.session_state.query_count
                })
            else:
                st.session_state.conversations[st.session_state.active_conversation]['messages'] = st.session_state.current_messages.copy()
            
            # Save to file for persistence across refreshes
            save_conversation_history(st.session_state.conversations)
            
            st.rerun()
        
        if st.button("Clear", use_container_width=True):
            st.session_state.prefilled_question = ""
            st.rerun()
else:
    # Normal chat input when no prefilled question
    if prompt := st.chat_input("Ask about ESS statistics, policy analysis, SDG indicators, price data..."):
        # If starting new conversation (no active conversation or active is None)
        if st.session_state.active_conversation is None:
            # Create new conversation - CLEAR previous messages
            st.session_state.current_messages = []
            st.session_state.active_conversation = len(st.session_state.conversations)
        else:
            # New question = new conversation, CLEAR old messages
            st.session_state.current_messages = []
            st.session_state.active_conversation = len(st.session_state.conversations)
        
        # Add user message
        st.session_state.current_messages.append({"role": "user", "content": prompt})
        st.session_state.query_count += 1
        
        with st.spinner("🤔 Analyzing data..."):
            result = st.session_state.rag.query(prompt, verbose=False)
        
        # Store message with sources data
        # Handle both old format (objects with .score) and new format (dicts)
        if result.get('sources') and len(result['sources']) > 0:
            # Check if sources are dicts or objects
            first_source = result['sources'][0]
            if isinstance(first_source, dict):
                top_score = 0.95  # Default score for LangChain sources (no scores)
            else:
                top_score = first_source.score
        else:
            top_score = 0
        
        message_metadata = {
            "sources": result['num_sources'], 
            "time": result['total_time'], 
            "top_score": top_score,
            "sources_data": result['sources']
        }
        
        # RELATED QUESTIONS GENERATION (Phase 7C)
        try:
            from src.citations.related_questions import RelatedQuestionsGenerator
            sdg_goal = 1
            if result.get('sources') and len(result['sources']) > 0:
                first_source = result['sources'][0]
                if isinstance(first_source, dict):
                    sdg_goal = first_source.get('metadata', {}).get('goal_number', 1)
                else:
                    sdg_goal = first_source.payload.get('goal_number', 1)
            
            question_generator = RelatedQuestionsGenerator(groq_client)
            related_questions = question_generator.generate_related_questions(
                query=prompt, answer=result['answer'], sdg_goal=sdg_goal,
                language="en", max_questions=4
            )
            if related_questions:
                message_metadata['related_questions'] = related_questions
        except Exception as e:
            print(f"⚠️ Related questions failed: {e}")
        
        # ENHANCE CITATIONS (Phase 7C - Revised)
        try:
            from src.citations.citation_enhancer import CitationEnhancer
            enhancer = CitationEnhancer()
            sources_for_enhancement = []
            seen_goals = set()
            
            for source in result['sources']:
                # Handle both dict and object formats
                if isinstance(source, dict):
                    goal_num = source.get('metadata', {}).get('goal_number', 0)
                    score = 0.95  # Default score for dict format
                else:
                    goal_num = source.payload.get('goal_number', 0)
                    score = source.score
                
                if goal_num not in seen_goals:
                    seen_goals.add(goal_num)
                    sources_for_enhancement.append({
                        'goal': goal_num,
                        'score': score,
                    })
            enhanced_sources = enhancer.enhance_sources(sources_for_enhancement)
            message_metadata['enhanced_sources'] = enhanced_sources
        except Exception as e:
            print(f"⚠️ Citation enhancement failed: {e}")
        
        st.session_state.current_messages.append({
            "role": "assistant",
            "content": result['answer'],
            "metadata": message_metadata
        })
        
        # Save/update conversation in history
        if st.session_state.active_conversation >= len(st.session_state.conversations):
            # New conversation
            st.session_state.conversations.append({
                'messages': st.session_state.current_messages.copy(),
                'timestamp': st.session_state.query_count
            })
        else:
            # Update existing conversation
            st.session_state.conversations[st.session_state.active_conversation]['messages'] = st.session_state.current_messages.copy()
        
        # Save to file for persistence across refreshes
        save_conversation_history(st.session_state.conversations)
        
        # Rerun to display the new message
        st.rerun()

# Footer
st.markdown("""
<div class="footer-text">
    ET ESS RAG Bot can make mistakes. Consider checking important information.
</div>
""", unsafe_allow_html=True)

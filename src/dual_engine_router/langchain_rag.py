"""
LangChain-Based Dual-Engine RAG System
=======================================
Uses LangChain framework with:
- Llama 3.1-8B via Ollama (local LLM)
- ChromaDB for vector storage
- SQLite for structured queries

Author: Yonas Abiyu Gion
Cost: $0 (100% FREE)
"""

import os
import sys
from typing import Dict, List, Optional
from dotenv import load_dotenv

# LangChain imports - simplified for compatibility
from langchain_community.llms import Ollama as OllamaLLM
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain

# Cross-encoder for re-ranking
try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False
    print("⚠️  Cross-encoder not available. Install with: pip install sentence-transformers")

# For Groq support
try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️  langchain-groq not installed. Install with: pip install langchain-groq")

# For Gemini support
GEMINI_AVAILABLE = True  # Always available now with custom wrapper

# For Hugging Face support
try:
    from langchain_huggingface import HuggingFaceEndpoint
    HF_AVAILABLE = True
except ImportError:
    try:
        from langchain_community.llms import HuggingFaceHub
        HuggingFaceEndpoint = HuggingFaceHub
        HF_AVAILABLE = True
    except ImportError:
        HF_AVAILABLE = False
        print("⚠️  Hugging Face not available")

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

# Configuration
CHROMADB_PATH = "data/vectorstore/chromadb"
SQLITE_PATH = "data/sql_database/sdg_ethiopia.db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3.2:1b"


class LangChainDualEngineRAG:
    """Dual-Engine RAG using LangChain framework"""
    
    def __init__(self):
        """Initialize both engines with LangChain"""
        print("🚀 Initializing LangChain Dual-Engine RAG...")
        
        # Determine LLM provider from environment
        llm_provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        
        # Initialize LLM based on provider
        if llm_provider == "huggingface":
            print("   Loading Hugging Face LLM (free, 3-5s response)...")
            hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
            if not hf_token or hf_token == "your_hf_token_here":
                print("   ⚠️  HUGGINGFACE_API_TOKEN not found, falling back to Ollama...")
                llm_provider = "ollama"
            else:
                try:
                    # Use HuggingFaceHub with a simple model
                    from langchain_community.llms import HuggingFaceHub
                    self.llm = HuggingFaceHub(
                        repo_id="google/flan-t5-large",
                        huggingfacehub_api_token=hf_token,
                        model_kwargs={"temperature": 0.7, "max_length": 512}
                    )
                    print("   ✅ Hugging Face LLM ready (using google/flan-t5-large)")
                except Exception as e:
                    print(f"   ⚠️  Hugging Face error: {str(e)[:100]}")
                    print("   Falling back to Ollama...")
                    llm_provider = "ollama"
        
        elif llm_provider == "gemini" and GEMINI_AVAILABLE:
            print("   Loading Google Gemini (fast, 1-2s response)...")
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                print("   ⚠️  GEMINI_API_KEY not found, falling back to Ollama...")
                llm_provider = "ollama"
            else:
                try:
                    # Use custom Google GenAI wrapper (supports AQ. tokens)
                    from .google_genai_llm import GoogleGenAILLM
                    self.llm = GoogleGenAILLM(
                        api_key=gemini_api_key,
                        model="gemini-2.0-flash-exp",
                        temperature=0.7,
                        max_tokens=512
                    )
                    print("   ✅ Gemini LLM ready (using direct Google GenAI SDK)")
                except Exception as e:
                    print(f"   ⚠️  Gemini error: {str(e)[:100]}")
                    print("   Falling back to Ollama...")
                    llm_provider = "ollama"
        
        elif llm_provider == "groq" and GROQ_AVAILABLE:
            print("   Loading Groq LLM (fast, 2-3s response)...")
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                print("   ⚠️  GROQ_API_KEY not found, falling back to Ollama...")
                llm_provider = "ollama"
            else:
                # Try multiple models in order of preference
                groq_models = [
                    "llama3-8b-8192",
                    "llama3-70b-8192",
                    "mixtral-8x7b-32768",
                    "gemma2-9b-it",
                ]
                
                llm_initialized = False
                for model in groq_models:
                    try:
                        self.llm = ChatGroq(
                            model=model,
                            temperature=0.7,
                            api_key=groq_api_key
                        )
                        # Test with a simple query
                        test_response = self.llm.invoke("test")
                        print(f"   ✅ Groq LLM ready (using {model})")
                        llm_initialized = True
                        break
                    except Exception as e:
                        if "404" in str(e) or "not found" in str(e).lower():
                            continue  # Try next model
                        else:
                            print(f"   ⚠️  Groq error: {str(e)[:100]}")
                            break
                
                if not llm_initialized:
                    print("   ⚠️  No working Groq models found, falling back to Ollama...")
                    llm_provider = "ollama"
        
        if llm_provider == "ollama" or (llm_provider != "groq" and llm_provider != "gemini"):
            print("   Loading Llama 3.2-1B via Ollama (slow, 15-30s response)...")
            self.llm = OllamaLLM(model=OLLAMA_MODEL, temperature=0.7)
            print("   ✅ Ollama LLM ready")
        
        # Initialize embeddings
        print("   Loading embedding model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("   ✅ Embeddings ready")
        
        # Initialize cross-encoder for re-ranking
        if CROSS_ENCODER_AVAILABLE:
            print("   Loading cross-encoder for re-ranking...")
            try:
                self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
                print("   ✅ Cross-encoder ready")
                self.rerank_enabled = True
            except Exception as e:
                print(f"   ⚠️  Cross-encoder load failed: {e}")
                self.rerank_enabled = False
        else:
            self.rerank_enabled = False
            print("   ⚠️  Re-ranking disabled (cross-encoder not available)")
        
        # Initialize Engine A (PDF RAG with ChromaDB)
        self._init_engine_a()
        
        # Initialize Engine B (SQL Database)
        self._init_engine_b()
        
        print("✅ LangChain Dual-Engine RAG ready!\n")
    
    def _init_engine_a(self):
        """Initialize Engine A: PDF RAG with Hybrid Search (MMR for diversity + relevance)"""
        try:
            print("   Initializing Engine A (PDF RAG with Hybrid Search)...")
            
            # Load ChromaDB vector store
            self.vectorstore = Chroma(
                persist_directory=CHROMADB_PATH,
                embedding_function=self.embeddings,
                collection_name="ess_pdf_documents"
            )
            
            # Create hybrid retriever using MMR (Maximal Marginal Relevance)
            # MMR balances relevance with diversity to avoid redundant similar docs
            # This effectively combines semantic (vector) with diversity (keyword-like)
            self.retriever = self.vectorstore.as_retriever(
                search_type="mmr",  # Hybrid approach: relevance + diversity
                search_kwargs={
                    "k": 15,  # Return 15 final documents (increased for better coverage)
                    "fetch_k": 40,  # Fetch 40 candidates before MMR filtering (increased)
                    "lambda_mult": 0.5  # 0.5 = 50% relevance, 50% diversity (balanced)
                }
            )
            
            # Create prompt template with STRICT anti-hallucination instructions
            self.pdf_prompt = PromptTemplate(
                template="""You are an expert on Ethiopian Statistical Service (ESS) and policy documents.

CRITICAL RULES:
1. ONLY use information from the Context below
2. If the Context does not contain the answer, say "The provided context does not contain information about [topic]"
3. NEVER make up data, numbers, or facts
4. NEVER use your general knowledge - ONLY use the Context
5. If you cannot answer from the Context, clearly state that

MANDATORY - ETHIOPIAN CALENDAR SPECIFICATION:
Ethiopia uses two calendar systems:
- Ethiopian Calendar (EC): ~7-8 years behind Gregorian
- Gregorian Calendar (GC): International standard

When providing ANY date or year in your answer, you MUST:
- State "EC [year]" if Ethiopian calendar, AND add "(equivalent to [GC year] GC)"
- State "[year] GC" if Gregorian calendar, AND add "(EC [EC year])"
- If document doesn't specify, mention BOTH possibilities

Examples of CORRECT answers:
✅ "The inflation rate for April EC 2018 (equivalent to 2025/2026 GC) is 11.7%"
✅ "According to the April 2018 GC report (EC 2010/2011), inflation was..."
✅ "The document mentions 2018 but doesn't specify the calendar system. This could refer to either EC 2018 (2025/2026 GC) or 2018 GC (EC 2010/2011)."

DO NOT write: "The inflation rate for 2018 is..." ❌ (MUST specify calendar!)
DO NOT write: "The inflation rate for EFY 2018 is..." ❌ (Use EC, not EFY!)

Context:
{context}

Question: {question}

Answer (ONLY from context, MUST specify EC or GC for all years):""",
                input_variables=["context", "question"]
            )
            
            print("   ✅ Engine A (PDF RAG) ready")
            self.engine_a_available = True
            
        except Exception as e:
            print(f"   ⚠️  Engine A initialization failed: {e}")
            self.engine_a_available = False
    
    def _init_engine_b(self):
        """Initialize Engine B: SQL Database"""
        try:
            print("   Initializing Engine B (SQL Database)...")
            
            # Connect to SQLite database
            db_uri = f"sqlite:///{SQLITE_PATH}"
            self.db = SQLDatabase.from_uri(db_uri)
            
            print("   ✅ Engine B (SQL Database) ready")
            self.engine_b_available = True
            
        except Exception as e:
            print(f"   ⚠️  Engine B initialization failed: {e}")
            self.engine_b_available = False
    
    def detect_query_type(self, query: str) -> str:
        """
        Detect whether to use Engine A (PDF), Engine B (SQL), or both
        
        Returns:
            'pdf' - Use PDF documents only
            'sql' - Use SQL database only
            'both' - Use both engines (most common for indicators)
        """
        query_lower = query.lower()
        
        # Force PDF ONLY for queries that SQL definitely doesn't have
        pdf_only_keywords = [
            'what is ess', 'about ess', 'green growth strategy', 'crge',
            'climate resilient', 'ten year perspective plan',
            'policy framework', 'policy implementation',
            'afdb report', 'african development bank',
            'infrastructure project', 'investment program',
            'explain the strategy', 'describe the policy'
        ]
        
        for keyword in pdf_only_keywords:
            if keyword in query_lower:
                return 'pdf'
        
        # Force SQL ONLY for very specific database queries
        sql_only_keywords = [
            'all sdg indicators', 'list all goals', 'compare all indicators',
            'sdg database', 'show all years', 'trend analysis'
        ]
        
        for keyword in sql_only_keywords:
            if keyword in query_lower:
                return 'sql'
        
        # Most indicator queries should use BOTH engines
        # This includes: poverty, education, health, mortality, etc.
        indicator_keywords = [
            # Poverty
            'poverty', 'poor', 'income level',
            # Education
            'education', 'school', 'enrollment', 'literacy', 'completion',
            'student', 'learning', 'teacher',
            # Health
            'health', 'mortality', 'death', 'disease', 'immunization',
            'vaccination', 'maternal', 'infant', 'child health',
            'life expectancy', 'malnutrition',
            # Employment & Economy
            'employment', 'unemployment', 'job', 'work', 'labor',
            'gdp', 'economic growth', 'productivity',
            # Infrastructure & Access
            'water', 'sanitation', 'electricity', 'energy', 'internet',
            'access to', 'coverage of',
            # Measurements
            'rate', 'percentage', 'proportion', 'ratio', 'number of',
            # SDG specific
            'sdg', 'goal', 'target', 'indicator',
            # Time-based queries
            'in 2020', 'in 2021', 'in 2022', 'latest', 'recent', 'current'
        ]
        
        # Check if query is about an indicator
        is_indicator_query = any(keyword in query_lower for keyword in indicator_keywords)
        
        if is_indicator_query:
            return 'both'  # Get data from BOTH PDF reports and SQL database
        
        # If not an indicator query, check context
        # Questions asking "what", "explain", "describe" without indicators -> PDF
        explanation_words = ['explain', 'describe', 'tell me about', 'what does', 'why does']
        if any(word in query_lower for word in explanation_words) and not is_indicator_query:
            return 'pdf'
        
        # Default: use both engines to be comprehensive
        return 'both'
    
    def _extract_goal_number(self, filename: str) -> int:
        """Extract SDG goal number from filename like 'Goal1.xlsx' -> 1"""
        import re
        match = re.search(r'Goal(\d+)', filename)
        return int(match.group(1)) if match else 0
    
    def _filter_used_sources(self, answer: str, sources: list, min_relevance_score: float = 0.3) -> list:
        """
        Filter sources to only include documents actually used in the answer.
        
        This prevents showing all 12 retrieved documents when only 2-3 were actually used.
        
        Args:
            answer: Generated answer text
            sources: List of retrieved source documents
            min_relevance_score: Minimum relevance score (0-1) for a source to be included
            
        Returns:
            Filtered list of sources that appear to be used in the answer
        """
        if not sources or not answer:
            return sources
        
        try:
            import re
            
            # Clean answer text
            answer_lower = answer.lower()
            
            # Remove common phrases that don't indicate source usage
            noise_phrases = [
                'based on', 'according to', 'the document', 'the report',
                'from ess', 'from un sdg', 'the data shows'
            ]
            for phrase in noise_phrases:
                answer_lower = answer_lower.replace(phrase, '')
            
            # Extract numbers and key phrases from answer
            answer_numbers = set(re.findall(r'\d+\.?\d*', answer))
            answer_words = set(w.lower() for w in re.findall(r'\b\w{5,}\b', answer_lower))
            
            used_sources = []
            
            for doc in sources:
                # Get source content
                if isinstance(doc, dict):
                    content = doc.get('content', '')
                else:
                    content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
                
                content_lower = content.lower()
                
                # Calculate relevance score
                relevance_score = 0.0
                
                # Check if numbers from answer appear in this source
                if answer_numbers:
                    content_numbers = set(re.findall(r'\d+\.?\d*', content))
                    matching_numbers = answer_numbers.intersection(content_numbers)
                    if matching_numbers:
                        number_match_ratio = len(matching_numbers) / len(answer_numbers)
                        relevance_score += number_match_ratio * 0.6  # Numbers are strong signal
                
                # Check if key words from answer appear in this source
                if answer_words:
                    content_words = set(w.lower() for w in re.findall(r'\b\w{5,}\b', content_lower))
                    matching_words = answer_words.intersection(content_words)
                    if matching_words:
                        word_match_ratio = len(matching_words) / len(answer_words)
                        relevance_score += word_match_ratio * 0.4  # Words are weaker signal
                
                # Include source if it meets minimum relevance threshold
                if relevance_score >= min_relevance_score:
                    used_sources.append(doc)
            
            # If no sources passed the filter but we have an answer, return top 3 by rerank score
            if not used_sources and sources:
                # Sort by rerank_score if available
                sources_with_scores = []
                for doc in sources:
                    if isinstance(doc, dict):
                        score = doc.get('metadata', {}).get('rerank_score', 0)
                    else:
                        score = doc.metadata.get('rerank_score', 0) if hasattr(doc, 'metadata') else 0
                    sources_with_scores.append((doc, score))
                
                sources_with_scores.sort(key=lambda x: x[1], reverse=True)
                used_sources = [doc for doc, score in sources_with_scores[:3]]
            
            return used_sources if used_sources else sources[:3]  # Return top 3 as fallback
            
        except Exception as e:
            print(f"   ⚠️  Source filtering failed: {e}, returning all sources")
            return sources
    
    def _validate_answer_against_sources(self, answer: str, sources: list, query: str) -> tuple[str, bool]:
        """
        Validate that the answer is supported by the retrieved sources
        
        Args:
            answer: Generated answer from LLM
            sources: List of source documents
            query: Original query
            
        Returns:
            (validated_answer, is_valid): Tuple of validated answer and validity flag
        """
        try:
            # Check if answer indicates no data
            no_data_indicators = [
                'no relevant data', 'no information', 'does not contain',
                'cannot find', 'not mentioned', 'no data available'
            ]
            
            if any(indicator in answer.lower() for indicator in no_data_indicators):
                return answer, False  # No data found, sources not used
            
            # Extract all text content from sources
            source_texts = []
            for doc in sources:
                if isinstance(doc, dict):
                    source_texts.append(doc.get('content', ''))
                else:
                    source_texts.append(doc.page_content if hasattr(doc, 'page_content') else str(doc))
            
            combined_sources = ' '.join(source_texts).lower()
            
            # Check for specific numbers/facts in the answer
            import re
            numbers_in_answer = re.findall(r'\d+\.?\d*', answer)
            
            if numbers_in_answer:
                # Verify at least some numbers exist in sources
                numbers_found = 0
                for num in numbers_in_answer[:5]:  # Check first 5 numbers
                    if num in combined_sources:
                        numbers_found += 1
                
                # If less than 30% of numbers found in sources, flag as suspicious
                if len(numbers_in_answer) >= 3 and numbers_found / len(numbers_in_answer[:5]) < 0.3:
                    return "⚠️ Warning: Answer may contain data not fully supported by sources.\n\n" + answer, False
            
            # Check key phrases from answer exist in sources
            answer_sentences = answer.split('.')[:3]  # Check first 3 sentences
            sentences_supported = 0
            
            for sentence in answer_sentences:
                sentence = sentence.strip().lower()
                if len(sentence) < 20:  # Skip very short sentences
                    continue
                    
                # Check if key words from sentence appear in sources
                words = sentence.split()
                key_words = [w for w in words if len(w) > 4][:5]  # First 5 significant words
                
                if key_words:
                    words_found = sum(1 for w in key_words if w in combined_sources)
                    if words_found / len(key_words) > 0.5:  # At least 50% of key words found
                        sentences_supported += 1
            
            # If we checked sentences and none are supported, flag it
            if len([s for s in answer_sentences if len(s.strip()) > 20]) > 0:
                if sentences_supported == 0:
                    return "⚠️ Warning: Answer may not be adequately supported by retrieved sources.\n\n" + answer, False
            
            return answer, True  # Answer appears to be supported
            
        except Exception as e:
            print(f"   ⚠️  Answer validation failed: {e}")
            return answer, True  # In case of error, allow answer through
    
    def _rerank_documents(self, query: str, documents: list, top_k: int = 5) -> list:
        """
        Re-rank documents using cross-encoder for better relevance
        
        Args:
            query: User query
            documents: List of retrieved documents
            top_k: Number of top documents to return
            
        Returns:
            Re-ranked list of top_k documents
        """
        if not self.rerank_enabled or not documents:
            return documents[:top_k]
        
        try:
            # Create query-document pairs
            pairs = [[query, doc.page_content] for doc in documents]
            
            # Get relevance scores from cross-encoder
            scores = self.cross_encoder.predict(pairs)
            
            # Sort documents by score (descending)
            scored_docs = list(zip(documents, scores))
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            # Return top-k documents with scores attached as metadata
            reranked_docs = []
            for doc, score in scored_docs[:top_k]:
                doc.metadata['rerank_score'] = float(score)
                reranked_docs.append(doc)
            
            return reranked_docs
            
        except Exception as e:
            print(f"   ⚠️  Re-ranking failed: {e}, using original order")
            return documents[:top_k]
    
    def _preprocess_query(self, query: str) -> str:
        """
        Preprocess query to improve hybrid search performance
        Expands acronyms, adds relevant keywords, and handles Ethiopian/Gregorian calendar
        """
        query_lower = query.lower()
        
        # Handle Ethiopian Calendar (EC) to Gregorian Calendar (GC) conversion
        # Ethiopian Calendar is ~7-8 years behind Gregorian
        import re
        
        # Check if query explicitly mentions Ethiopian calendar
        has_ethiopian_indicator = any(indicator in query_lower for indicator in 
                                     ['efy', 'ec ', ' ec', 'ethiopian fiscal year', 'ethiopian calendar'])
        
        # Extract years from query
        years = re.findall(r'\b(20\d{2}|19\d{2})\b', query)
        
        if years and not has_ethiopian_indicator:
            # User said just "2018" - ambiguous!
            # Add both interpretations to search
            for year in years:
                year_int = int(year)
                if 2010 <= year_int <= 2030:  # Reasonable range
                    # Add Ethiopian interpretation (add ~7 years)
                    ethiopian_year = year_int - 2007 if year_int > 2007 else year_int - 2008
                    query += f" EC {ethiopian_year} Ethiopian calendar {year_int}"
        
        # If explicitly Ethiopian (EC/EFY mentioned), add Gregorian equivalent
        ec_matches = re.findall(r'(?:efy|ec)\s*(\d{4})', query_lower)
        if ec_matches:
            for ec_year in ec_matches:
                ec_int = int(ec_year)
                # Convert EC to Gregorian (add ~7 years)
                gc_year = ec_int + 2007 if ec_int < 100 else ec_int + 2007
                query += f" {gc_year} Gregorian calendar year"
        
        # Expand common acronyms and add full terms for better keyword matching
        expansions = {
            'cpi': 'CPI Consumer Price Index inflation',
            'gdp': 'GDP Gross Domestic Product economic growth',
            'sdg': 'SDG Sustainable Development Goals',
            'ess': 'ESS Ethiopian Statistical Service Ethiopia',
            'afdb': 'AfDB African Development Bank',
            'crge': 'CRGE Climate Resilient Green Economy',
            'gtp': 'GTP Growth Transformation Plan',
            'ec ': 'EC Ethiopian Calendar EFY',
            'efy': 'EFY Ethiopian Fiscal Year EC',
            'edhs': 'EDHS Ethiopian Demographic Health Survey',
            'vacs': 'VACS Violence Against Children Survey',
        }
        
        # Add expansions if acronym found
        for acronym, expansion in expansions.items():
            if acronym in query_lower and expansion not in query:
                query = f"{query} {expansion}"
        
        # Add regional keywords for better regional data matching
        regional_keywords = {
            'amhara': 'Amhara region regional administrative',
            'oromia': 'Oromia region regional administrative',
            'tigray': 'Tigray region regional administrative',
            'snnp': 'SNNP Southern Nations region regional',
            'somali': 'Somali region regional administrative',
            'afar': 'Afar region regional administrative',
            'benishangul': 'Benishangul Gumuz region regional',
            'gambela': 'Gambela region regional administrative',
            'harari': 'Harari region regional administrative',
            'dire dawa': 'Dire Dawa city administration',
            'addis ababa': 'Addis Ababa city capital administration'
        }
        
        for region, expansion in regional_keywords.items():
            if region in query_lower and expansion not in query:
                query = f"{query} {expansion}"
        
        # Add sector-specific keywords for better matching
        sector_keywords = {
            'livestock': 'livestock animal production cattle sheep goat poultry farming beehives dairy meat milk',
            'agriculture': 'agriculture farming crop production cultivation rural harvest land area',
            'population': 'population demographic census people inhabitants residents household',
            'health': 'health medical healthcare disease mortality morbidity hospital clinic',
            'education': 'education school enrollment literacy learning students teacher',
            'employment': 'employment job work labor workforce occupation unemployment',
            'region': 'region regional administrative zone woreda amhara oromia tigray snnp somali afar',
            'production': 'production output yield productivity supply quantity amount'
        }
        
        for sector, expansion in sector_keywords.items():
            if sector in query_lower and expansion not in query:
                query = f"{query} {expansion}"
        
        # Add time-related keywords if date/time mentioned
        time_keywords = ['january', 'february', 'march', 'april', 'may', 'june',
                        'july', 'august', 'september', 'october', 'november', 'december',
                        '2020', '2021', '2022', '2023', '2024', '2025', '2026',
                        'latest', 'recent', 'current', 'last month']
        
        if any(keyword in query_lower for keyword in time_keywords):
            query = f"{query} timeperiod year month report data statistics"
        
        return query
    
    def query_engine_a(self, query: str) -> Dict:
        """Query Engine A (PDF RAG) with Hybrid Search - Retrieval + LLM"""
        if not self.engine_a_available:
            return {
                'error': 'Engine A not available',
                'answer': 'PDF document search is not available.'
            }
        
        try:
            # Preprocess query for better keyword matching
            enhanced_query = self._preprocess_query(query)
            
            # Get relevant documents using hybrid MMR retriever
            docs = self.retriever.invoke(enhanced_query)
            
            # CRITICAL: Apply cross-encoder re-ranking for better relevance
            if self.rerank_enabled and docs:
                print(f"   🔄 Re-ranking {len(docs)} documents...")
                docs = self._rerank_documents(query, docs, top_k=7)  # Keep top 7 after re-ranking (increased from 5)
                print(f"   ✅ Using top {len(docs)} re-ranked documents")
            
            # CRITICAL: Check if we actually retrieved documents
            if not docs or len(docs) == 0:
                return {
                    'engine': 'PDF RAG (LangChain)',
                    'answer': 'No relevant data found in ESS PDF documents for this query.',
                    'sources': [],
                    'source_count': 0
                }
            
            # Format context from documents - TRUNCATE to avoid token limits
            context_parts = []
            max_context_length = 8000  # Increased from 6000 to 8000 for more content
            current_length = 0
            
            for doc in docs:
                content = doc.page_content[:1500]  # Limit each doc to 1500 chars
                if current_length + len(content) < max_context_length:
                    context_parts.append(content)
                    current_length += len(content)
                else:
                    break
            
            context = "\n\n".join(context_parts)
            
            # CRITICAL: Validate context is meaningful
            if not context or len(context.strip()) < 100:
                return {
                    'engine': 'PDF RAG (LangChain)',
                    'answer': 'No relevant data found in ESS PDF documents for this query.',
                    'sources': [],
                    'source_count': 0
                }
            
            # Create prompt with STRICT instructions
            prompt_text = self.pdf_prompt.format(context=context, question=query)
            
            # Get answer from LLM
            answer = self.llm.invoke(prompt_text)
            
            # Extract text from answer (handle both string and AIMessage)
            if hasattr(answer, 'content'):
                answer_text = answer.content
            else:
                answer_text = str(answer)
            
            # CRITICAL: Detect hallucinations - if LLM says it doesn't have info, return no data
            # But be careful not to be TOO strict - sometimes LLM needs a hint to try harder
            strict_no_data_phrases = [
                "does not contain",
                "cannot find",
                "not provided in the context",
                "context does not include",
                "not mentioned in the context"
            ]
            
            # Only reject if LLM STRONGLY indicates no data
            if any(phrase in answer_text.lower() for phrase in strict_no_data_phrases):
                # Double-check: Do we have good documents?
                if len(docs) > 0:
                    # We have documents, but LLM says no data - try a more direct prompt
                    print("   ⚠️  LLM said 'no data' but we have documents. Retrying with direct prompt...")
                    
                    # Create more direct context from top docs
                    direct_context = "\n\n".join([doc.page_content[:1000] for doc in docs[:3]])
                    
                    direct_prompt = f"""You are analyzing Ethiopian statistical documents. Answer ONLY from the context below.

Context (ESS Documents):
{direct_context}

Question: {query}

IMPORTANT: 
- If the context mentions relevant data (numbers, statistics, tables), USE IT
- If you find ANY relevant information, provide it
- Only say "no data" if context is completely irrelevant

Answer:"""
                    
                    retry_response = self.llm.invoke(direct_prompt)
                    retry_answer = retry_response.content if hasattr(retry_response, 'content') else str(retry_response)
                    
                    # If retry still says no data, then truly no data
                    if any(phrase in retry_answer.lower() for phrase in strict_no_data_phrases):
                        return {
                            'engine': 'PDF RAG (LangChain)',
                            'answer': 'No relevant data found in ESS PDF documents for this query.',
                            'sources': [],
                            'source_count': 0
                        }
                    else:
                        # Retry succeeded! Use the new answer
                        answer_text = retry_answer
                        print("   ✅ Retry successful, using new answer")
                else:
                    # Truly no documents
                    return {
                        'engine': 'PDF RAG (LangChain)',
                        'answer': 'No relevant data found in ESS PDF documents for this query.',
                        'sources': [],
                        'source_count': 0
                    }
            
            # CRITICAL: Validate answer against sources
            validated_answer, is_valid = self._validate_answer_against_sources(answer_text, docs, query)
            
            # If answer is not well-supported, filter sources or flag it
            if not is_valid:
                # Return with warning but no sources
                return {
                    'engine': 'PDF RAG (LangChain)',
                    'answer': validated_answer,
                    'sources': [],
                    'source_count': 0
                }
            
            # CRITICAL: Filter sources to only show documents actually used in the answer
            # This prevents showing all 12 retrieved docs when only 2-3 were used
            filtered_docs = self._filter_used_sources(answer_text, docs, min_relevance_score=0.3)
            print(f"   📄 Filtered to {len(filtered_docs)} used documents (from {len(docs)} retrieved)")
            
            # Format sources
            sources = []
            for doc in filtered_docs:
                sources.append({
                    'content': doc.page_content[:500],  # Limit source preview
                    'metadata': doc.metadata
                })
            
            return {
                'engine': 'PDF RAG (LangChain)',
                'answer': answer_text,
                'sources': sources,
                'source_count': len(sources)
            }
            
        except Exception as e:
            return {
                'error': f'Engine A error: {str(e)}',
                'answer': f'Error querying PDF documents: {str(e)}'
            }
    
    def _is_sdg_relevant_query(self, query: str) -> bool:
        """
        Check if query is about SDG indicators that actually exist in the database.
        
        Returns True only if query is about actual SDG indicators, not general questions.
        This prevents SDG engine from attempting to answer questions outside its scope.
        """
        query_lower = query.lower()
        
        # Comprehensive list of SDG indicators ACTUALLY in the database
        sdg_indicators = [
            # Goal 1: No Poverty
            'poverty', 'poor', 'poverty line', 'poverty rate', 'income poverty',
            'social protection', 'social assistance', 'cash benefit', 'social insurance',
            
            # Goal 2: Zero Hunger (LIMITED - mostly not in SDG DB)
            'hunger', 'malnutrition', 'food security', 'undernourishment',
            
            # Goal 3: Good Health
            'mortality', 'death rate', 'maternal mortality', 'infant mortality',
            'child mortality', 'neonatal mortality', 'disease', 'health coverage',
            'universal health', 'immunization', 'vaccination',
            
            # Goal 4: Quality Education
            'education', 'literacy', 'school enrollment', 'primary education',
            'secondary education', 'completion rate', 'out of school',
            
            # Goal 5: Gender Equality
            'gender', 'women', 'female', 'gender parity', 'violence against women',
            
            # Goal 6: Clean Water
            'water', 'drinking water', 'sanitation', 'hygiene', 'wastewater',
            'water quality', 'water scarcity',
            
            # Goal 7: Affordable Energy
            'energy', 'electricity', 'renewable energy', 'energy access',
            
            # Goal 8: Decent Work
            'employment', 'unemployment', 'job', 'labor force', 'wage',
            'child labor', 'economic growth', 'gdp', 'productivity',
            
            # Goal 9: Industry & Infrastructure
            'infrastructure', 'industry', 'manufacturing', 'innovation',
            'research and development', 'internet access',
            
            # Goal 10: Reduced Inequalities
            'inequality', 'income inequality', 'gini', 'disparity',
            
            # Goal 11: Sustainable Cities
            'urban', 'cities', 'housing', 'slum', 'public transport',
            'air quality', 'waste management',
            
            # Goal 13: Climate Action
            'climate', 'emissions', 'greenhouse gas', 'climate change',
            'temperature', 'disaster risk reduction',
            
            # Goal 15: Life on Land
            'forest', 'deforestation', 'land degradation', 'biodiversity',
            
            # Goal 16: Peace & Justice
            'violence', 'homicide', 'justice', 'corruption', 'birth registration',
            
            # Goal 17: Partnerships
            'oda', 'official development assistance', 'aid', 'remittances',
            
            # Disaster-related (in SDG database)
            'disaster', 'affected by disaster', 'deaths due to disaster',
            'economic loss', 'disaster risk',
            
            # Government spending (in SDG database)
            'government spending', 'public spending', 'budget allocation',
            'spending on education', 'spending on health', 'spending on social'
        ]
        
        # Check if query contains any SDG indicator keywords
        has_sdg_keyword = any(indicator in query_lower for indicator in sdg_indicators)
        
        # Additional check: common phrases that suggest SDG-type data
        sdg_phrases = [
            'proportion of', 'percentage of', 'rate of', 'number of',
            'coverage of', 'access to', 'prevalence of', 'incidence of'
        ]
        has_sdg_phrase = any(phrase in query_lower for phrase in sdg_phrases)
        
        # Query must have either:
        # 1. Direct SDG indicator keyword, OR
        # 2. SDG phrase + some indicator term
        return has_sdg_keyword or (has_sdg_phrase and any(word in query_lower for word in ['population', 'people', 'children', 'women', 'men']))
    
    def query_engine_b(self, query: str) -> Dict:
        """Query Engine B (SQL) - Generate SQL, Execute, and Interpret"""
        if not self.engine_b_available:
            return {
                'error': 'Engine B not available',
                'answer': 'SQL database is not available.'
            }
        
        # CRITICAL: Pre-check if query is about SDG indicators
        # Skip SDG engine entirely if query is not about SDG data
        if not self._is_sdg_relevant_query(query):
            return {
                'engine': 'SQL Database (LangChain)',
                'answer': 'No data found in the UN SDG database for this specific query.',
                'sql_query': 'N/A - Query not related to SDG indicators',
                'raw_result': '[]',
                'source_count': 0,
                'sources': []
            }
        
        try:
            # STEP 1: Generate SQL query using LLM
            sql_generation_prompt = f"""You are a SQLite expert. Generate ONLY a valid SQL query with no explanations.

Database schema:
Table: sdg_indicators  
Key columns: indicator, seriesdescription, geoareaname, timeperiod, value, units, sex, age, location

Important notes:
- seriesdescription contains indicators like:
  * "Proportion of population below international poverty line (%)" - THIS IS THE MAIN POVERTY RATE
  * "Employed population below international poverty line, by sex and age (%)"
  * "Official development assistance grants for poverty reduction" - THIS IS NOT POVERTY RATE
- timeperiod is INTEGER (year like 2021, 2020, etc.)
- Multiple rows may exist for same year (broken down by sex, age, location)
- sex column: 'MALE', 'FEMALE', 'BOTHSEX', or NULL
- location column: 'URBAN', 'RURAL', 'ALLAREA', or NULL

CRITICAL RULES:
1. Return ONLY the SQL query - no text before or after
2. For poverty RATE queries:
   - Use: seriesdescription LIKE '%Proportion of population below%poverty%'
   - Prefer sex='BOTHSEX' or sex IS NULL (overall population)
   - Prefer location='ALLAREA' or location IS NULL (entire country)
3. For poverty RATE, exclude "Official development assistance" or "Employed population"
4. timeperiod is INTEGER: timeperiod=2021 (NOT '2021')
5. Always filter by geoareaname='Ethiopia'
6. Use ORDER BY timeperiod DESC to get latest year first
7. Add WHERE sex IS NULL OR sex='BOTHSEX' to get overall population
8. Add WHERE location IS NULL OR location='ALLAREA' to get national level
9. LIMIT 1 for single most recent value

Question: {query}

SQLQuery:"""

            # Generate SQL
            sql_response = self.llm.invoke(sql_generation_prompt)
            
            # Extract SQL text
            if hasattr(sql_response, 'content'):
                sql_query = sql_response.content.strip()
            else:
                sql_query = str(sql_response).strip()
            
            # Clean up SQL (remove any markdown formatting or explanations)
            if "```sql" in sql_query:
                sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
            elif "```" in sql_query:
                sql_query = sql_query.split("```")[1].split("```")[0].strip()
            
            # Remove any trailing semicolons or extra text
            sql_query = sql_query.split(';')[0].strip()
            
            # STEP 2: Execute SQL query
            try:
                query_result = self.db.run(sql_query)
                
                # If no results and query has a specific year, try without year constraint
                if (not query_result or str(query_result).strip() == '[]') and 'timeperiod' in sql_query:
                    # Extract the base query without year constraint
                    fallback_query = sql_query
                    # Remove timeperiod constraint but keep everything else
                    import re
                    fallback_query = re.sub(r'AND\s+timeperiod\s*=\s*\d+', '', fallback_query)
                    fallback_query = re.sub(r'timeperiod\s*=\s*\d+\s+AND', '', fallback_query)
                    
                    # Try fallback query
                    query_result = self.db.run(fallback_query)
                    if query_result and str(query_result).strip() != '[]':
                        sql_query = fallback_query + " (fallback: showing latest available year)"
                        
            except Exception as sql_error:
                return {
                    'error': f'SQL execution error: {str(sql_error)}',
                    'answer': f'Error executing SQL query: {str(sql_error)}\n\nGenerated SQL was:\n{sql_query}',
                    'sql_query': sql_query
                }
            
            # STEP 3: Interpret results using LLM ONLY if we have actual data
            if query_result and str(query_result).strip() and str(query_result).strip() != '[]' and str(query_result).strip() != '()':
                # CRITICAL: Additional validation - check if result contains actual values
                result_str = str(query_result)
                if result_str.count('None') == len(result_str.split(',')) or not any(c.isdigit() for c in result_str):
                    # Result is all None or has no numbers - treat as no data
                    answer = "No data found in the UN SDG database for this specific query."
                    return {
                        'engine': 'SQL Database',
                        'answer': answer,
                        'sql_query': sql_query,
                        'raw_result': '[]',
                        'source_count': 0,
                        'sources': []
                    }
                
                # CRITICAL: TOPIC RELEVANCE CHECK - Ensure SQL result matches query topic
                # This prevents returning poverty data for livestock queries
                query_topics = {
                    'health': ['health', 'disease', 'mortality', 'hospital', 'medical', 'vaccination'],
                    'education': ['education', 'school', 'student', 'literacy', 'enrollment', 'learning'],
                    'employment': ['employment', 'job', 'work', 'labor', 'unemployment', 'workforce'],
                    'poverty': ['poverty', 'poor', 'income', 'wealth', 'inequality'],
                    'population': ['population', 'demographic', 'people', 'census', 'inhabitants'],
                    'water': ['water', 'sanitation', 'hygiene', 'drinking water'],
                    'energy': ['energy', 'electricity', 'power', 'renewable'],
                    'disaster': ['disaster', 'affected', 'deaths', 'damage', 'loss'],
                    'government': ['government spending', 'budget', 'public spending', 'allocation']
                }
                
                # Determine query topic
                detected_topic = None
                for topic, keywords in query_topics.items():
                    if any(keyword in query.lower() for keyword in keywords):
                        detected_topic = topic
                        break
                
                # Check if SQL result topic matches query topic
                if detected_topic:
                    # Get seriesdescription from result if possible
                    result_lower = result_str.lower()
                    
                    # Check if result contains topic-matching keywords
                    topic_match = any(keyword in result_lower for keyword in query_topics.get(detected_topic, []))
                    
                    # General topic mismatch detection
                    if not topic_match:
                        # Result doesn't match query topic
                        # Check if it's actually poverty/employment data instead
                        if 'poverty' in result_lower or 'employment' in result_lower:
                            answer = f"No relevant data found in the UN SDG database for this query."
                            return {
                                'engine': 'SQL Database',
                                'answer': answer,
                                'sql_query': sql_query,
                                'raw_result': '[]',
                                'source_count': 0,
                                'sources': []
                            }
                
                interpretation_prompt = f"""Based on this SQL query result, provide a clear, natural language answer.

Question: {query}

SQL Query: {sql_query}

Query Result: {query_result}

CRITICAL INSTRUCTIONS:
- ONLY use the data shown in Query Result above
- Do NOT make up or infer any data not present in the result
- If the result is for a different year than asked, clearly state which year the data is from
- If no result or result is empty/None, say "No data found"
- Cite "UN SDG database" as source
- Keep answer concise (2-3 sentences maximum)

Answer:"""

                interpretation = self.llm.invoke(interpretation_prompt)
                
                if hasattr(interpretation, 'content'):
                    answer = interpretation.content
                else:
                    answer = str(interpretation)
                
                # CRITICAL: Detect if LLM is hallucinating despite having no real data
                if any(phrase in answer.lower() for phrase in ["no data", "not available", "cannot find", "no information"]):
                    answer = "No data found in the UN SDG database for this specific query."
                    return {
                        'engine': 'SQL Database',
                        'answer': answer,
                        'sql_query': sql_query,
                        'raw_result': '[]',
                        'source_count': 0,
                        'sources': []
                    }
                
                # CRITICAL: Extract sources from SQL result
                # Parse the result to identify which SDG indicators were used
                sources = []
                try:
                    # Extract indicator information from result
                    import re
                    
                    # Try to find indicator/series descriptions in the result
                    if 'Proportion of population below' in result_str:
                        sources.append({
                            'source': 'UN SDG Goal 1 - No Poverty',
                            'file': 'Goal1.xlsx',
                            'description': 'Poverty indicators for Ethiopia'
                        })
                    
                    # Check for other common indicators
                    indicator_mapping = {
                        'employment': {'goal': 'Goal 8 - Decent Work', 'file': 'Goal8.xlsx'},
                        'health': {'goal': 'Goal 3 - Good Health', 'file': 'Goal3.xlsx'},
                        'education': {'goal': 'Goal 4 - Quality Education', 'file': 'Goal4.xlsx'},
                        'gender': {'goal': 'Goal 5 - Gender Equality', 'file': 'Goal5.xlsx'},
                        'water': {'goal': 'Goal 6 - Clean Water', 'file': 'Goal6.xlsx'},
                        'energy': {'goal': 'Goal 7 - Affordable Energy', 'file': 'Goal7.xlsx'},
                        'inequality': {'goal': 'Goal 10 - Reduced Inequalities', 'file': 'Goal10.xlsx'},
                        'climate': {'goal': 'Goal 13 - Climate Action', 'file': 'Goal13.xlsx'},
                    }
                    
                    for keyword, info in indicator_mapping.items():
                        if keyword in result_str.lower():
                            sources.append({
                                'source': f"UN SDG {info['goal']}",
                                'file': info['file'],
                                'description': f'{info["goal"]} indicators for Ethiopia'
                            })
                            break
                    
                    # If no specific mapping found but we have data, use generic SDG source
                    if not sources:
                        sources.append({
                            'source': 'UN SDG Database',
                            'file': 'sdg_ethiopia.db',
                            'description': 'Sustainable Development Goals indicators for Ethiopia'
                        })
                
                except Exception as e:
                    # Fallback: generic SDG source
                    sources = [{
                        'source': 'UN SDG Database',
                        'file': 'sdg_ethiopia.db',
                        'description': 'Sustainable Development Goals indicators for Ethiopia'
                    }]
                
                return {
                    'engine': 'SQL Database (LangChain)',
                    'answer': answer,
                    'sql_query': sql_query,
                    'raw_result': str(query_result),
                    'source_count': len(sources),
                    'sources': sources
                }
                
            else:
                # No results - provide helpful guidance
                answer = "No data found in the UN SDG database for this specific query.\n\n"
                
                # Check if it's a year issue
                if any(year in query.lower() for year in ['2022', '2023', '2024', '2025', '2026']):
                    answer += "**Note:** The UN SDG database may not have data for very recent years. "
                    answer += "The most recent data available is typically from 2021 or earlier.\n\n"
                
                answer += "The database contains indicators like:\n"
                answer += "- Proportion of population below international poverty line (%)\n"
                answer += "- Proportion of population living below national poverty line (%)\n"
                answer += "- Employment poverty indicators\n\n"
                answer += "Try asking: 'What is Ethiopia's poverty rate in 2021?' or 'What is the latest poverty rate for Ethiopia?'"
            
            return {
                'engine': 'SQL Database (LangChain)',
                'answer': answer,
                'sql_query': sql_query,
                'raw_result': str(query_result) if query_result else '[]',
                'source_count': 0,
                'sources': []
            }
            
        except Exception as e:
            error_msg = str(e)
            return {
                'error': f'Engine B error: {error_msg}',
                'answer': f'Error querying database: {error_msg}'
            }
    
    def _is_valid_query(self, query: str) -> tuple[bool, str]:
        """
        Validate if query is meaningful and not gibberish
        
        Returns:
            (is_valid, reason) - True if valid, False with reason if invalid
        """
        query_lower = query.lower().strip()
        
        # Check minimum length
        if len(query_lower) < 2:
            return False, "Query too short. Please ask a complete question."
        
        # SPECIAL CASE: Detect greetings - always valid
        # Use word boundaries to avoid false matches like "what about livestock"
        greeting_patterns = [
            r'\bhello\b', r'\bhi\b', r'\bhey\b', r'\bgreetings\b',
            r'\bgood morning\b', r'\bgood afternoon\b', r'\bgood evening\b', r'\bgood day\b',
            r'\bhowdy\b', r'\bhola\b', r'\bwelcome\b',
            r'\bnice to meet\b', r'\bpleased to meet\b',
            r'\bhow are you\b', r'\bhow do you do\b',
            r'\bwhats up\b', r'\bwhat\'s up\b', r'\bsup\b', r'\byo\b'
        ]
        
        # Check if query is ONLY a greeting (not part of a real question)
        import re
        for pattern in greeting_patterns:
            if re.search(pattern, query_lower):
                # Additional check: ensure it's not part of a data question
                # Exclude if query contains data-related keywords after the greeting word
                data_keywords = ['data', 'statistics', 'rate', 'population', 'inflation', 'poverty', 
                                'production', 'livestock', 'agriculture', 'employment', 'health',
                                'education', 'gdp', 'cpi', 'census', 'survey', 'indicator']
                if not any(keyword in query_lower for keyword in data_keywords):
                    return True, "greeting"  # Pure greeting only
        
        # SPECIAL CASE: Detect thank you / goodbye - always valid
        gratitude_patterns = [
            'thank', 'thanks', 'thx', 'appreciate', 'grateful',
            'bye', 'goodbye', 'see you', 'farewell', 'have a nice',
            'have a good', 'take care'
        ]
        
        if any(pattern in query_lower for pattern in gratitude_patterns):
            return True, "gratitude"  # Special flag for thank you/goodbye
        
        # Check for gibberish - must have at least one recognizable word
        # List of common statistical/data keywords and basic English words
        valid_keywords = [
            # Statistical terms
            'data', 'statistics', 'rate', 'percent', 'number', 'total', 'average',
            'population', 'inflation', 'cpi', 'gdp', 'unemployment', 'poverty',
            'income', 'education', 'health', 'mortality', 'price', 'cost',
            # Query words
            'what', 'when', 'where', 'who', 'how', 'why', 'which', 'is', 'are',
            'was', 'were', 'can', 'could', 'would', 'should', 'tell', 'show',
            'give', 'provide', 'find', 'get', 'explain', 'describe',
            # Common words
            'the', 'a', 'an', 'in', 'of', 'for', 'to', 'from', 'about', 'with',
            # Ethiopia-specific
            'ethiopia', 'ethiopian', 'addis', 'ababa', 'ess', 'sdg',
            # Numbers and years
            '2020', '2021', '2022', '2023', '2024', '2025', '2026',
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ]
        
        # Check if query contains at least 2 valid keywords or is a proper question
        words = query_lower.split()
        valid_word_count = sum(1 for word in words if any(keyword in word for keyword in valid_keywords))
        
        # Calculate vowel ratio (gibberish usually has unusual vowel patterns)
        vowels = 'aeiou'
        vowel_count = sum(1 for char in query_lower if char in vowels)
        consonant_count = sum(1 for char in query_lower if char.isalpha() and char not in vowels)
        
        # Check for reasonable vowel ratio (20-60% is normal English)
        if consonant_count > 0:
            vowel_ratio = vowel_count / (vowel_count + consonant_count)
            if vowel_ratio < 0.15 or vowel_ratio > 0.7:
                # Unusual vowel pattern - likely gibberish
                if valid_word_count < 2:
                    return False, "Query appears to be gibberish. Please ask a clear question about Ethiopian statistics."
        
        # Must have at least 2 valid keywords OR contain a question word
        question_words = ['what', 'when', 'where', 'who', 'how', 'why', 'which', 'tell', 'show', 'give']
        has_question_word = any(qword in query_lower for qword in question_words)
        
        if valid_word_count < 2 and not has_question_word:
            return False, "Query not clear. Please ask a complete question about Ethiopian statistics (e.g., 'What is the inflation rate for 2025?')."
        
        return True, ""
    
    def query(self, question: str, verbose: bool = True) -> Dict:
        """
        Main query method - routes to appropriate engine(s)
        
        Args:
            question: User question
            verbose: Print debug info
            
        Returns:
            Combined results from engine(s) - compatible with Streamlit app
        """
        import time
        start_time = time.time()
        
        # CRITICAL: Validate query is not gibberish
        is_valid, validation_result = self._is_valid_query(question)
        
        # Handle greetings with polite response
        if is_valid and validation_result == "greeting":
            greeting_response = (
                "Hello! 👋 Welcome to the Ethiopian Statistical Service (ESS) Data Assistant.\n\n"
                "I can help you find statistical data about Ethiopia, including:\n"
                "- 📊 **Inflation & CPI data** (Consumer Price Index, monthly reports)\n"
                "- 📈 **Economic indicators** (GDP, employment, poverty rates)\n"
                "- 👥 **Population statistics** (demographics, census data)\n"
                "- 🎯 **SDG indicators** (Sustainable Development Goals for Ethiopia)\n"
                "- 🌾 **Agriculture & household surveys**\n\n"
                "**Example questions you can ask:**\n"
                "- What is the inflation rate for April 2025?\n"
                "- What is Ethiopia's poverty rate in 2021?\n"
                "- Show me CPI data for the latest month\n"
                "- What is the population growth rate?\n\n"
                "Feel free to ask any question about Ethiopian statistics! 🇪🇹"
            )
            return {
                'answer': greeting_response,
                'sources': [],
                'num_sources': 0,
                'engines_used': ['Greeting Handler'],
                'total_time': 0.0
            }
        
        # Handle gratitude/goodbye with polite response
        if is_valid and validation_result == "gratitude":
            gratitude_response = (
                "You're welcome! 😊\n\n"
                "Thank you for using the Ethiopian Statistical Service Data Assistant.\n\n"
                "If you have any more questions about Ethiopian statistics, "
                "feel free to ask anytime. Have a great day! 🇪🇹"
            )
            return {
                'answer': gratitude_response,
                'sources': [],
                'num_sources': 0,
                'engines_used': ['Gratitude Handler'],
                'total_time': 0.0
            }
        
        # Reject invalid queries
        if not is_valid:
            return {
                'answer': f"❌ **Invalid Query:** {validation_result}",
                'sources': [],
                'num_sources': 0,
                'engines_used': [],
                'total_time': 0.0,
                'error': validation_result
            }
        
        if verbose:
            print(f"\n🔍 Question: {question}")
        
        # Detect query type
        query_type = self.detect_query_type(question)
        
        if verbose:
            print(f"🎯 Routing to: {query_type.upper()}")
        
        result = {
            'question': question,
            'query_type': query_type,
            'engines_used': [],
            'sources': [],  # Initialize empty sources list
            'num_sources': 0,  # Track number of sources
            'total_time': 0.0
        }
        
        # Route to appropriate engine(s)
        if query_type in ['pdf', 'both']:
            if verbose:
                print("📄 Querying Engine A (PDF RAG)...")
            
            engine_a_result = self.query_engine_a(question)
            result['engine_a'] = engine_a_result
            result['engines_used'].append('PDF RAG')
            
            # Add sources from Engine A
            if 'sources' in engine_a_result:
                result['sources'] = engine_a_result['sources']
                result['num_sources'] = len(engine_a_result['sources'])
            
            # If only PDF, use its answer
            if query_type == 'pdf':
                result['answer'] = engine_a_result.get('answer', 'No answer available.')
        
        if query_type in ['sql', 'both']:
            if verbose:
                print("📊 Querying Engine B (SQL)...")
            
            engine_b_result = self.query_engine_b(question)
            result['engine_b'] = engine_b_result
            result['engines_used'].append('SQL Database')
            
            # Add SQL source information ONLY if query returned actual data
            if ('sql_query' in engine_b_result and 
                engine_b_result.get('answer') and 
                'No data found' not in engine_b_result.get('answer', '') and
                'error' not in engine_b_result.get('answer', '').lower()):
                # Only add sources if SQL actually returned results
                # Check if raw_result exists and is not empty
                raw_result = engine_b_result.get('raw_result', '[]')
                if raw_result and str(raw_result).strip() not in ['[]', '', 'None']:
                    # CRITICAL: Use sources from engine_b if available
                    sql_sources = engine_b_result.get('sources', [])
                    
                    # If engine_b didn't provide sources, fall back to keyword-based detection
                    if not sql_sources:
                        # Try to determine which SDG goal this query relates to
                        relevant_goals = []
                        query_lower = question.lower()
                        goal_keywords = {
                            1: ['poverty', 'poor', 'income'],
                            2: ['hunger', 'food', 'agriculture', 'nutrition', 'livestock', 'cattle', 'animal', 'farming'],
                            3: ['health', 'mortality', 'disease', 'medical', 'immunization'],
                            4: ['education', 'school', 'literacy', 'enrollment'],
                            5: ['gender', 'women', 'female'],
                            6: ['water', 'sanitation', 'hygiene'],
                            7: ['energy', 'electricity', 'power'],
                            8: ['employment', 'job', 'economic growth', 'gdp'],
                            9: ['infrastructure', 'industry', 'innovation'],
                            10: ['inequality', 'disparity'],
                            11: ['cities', 'urban', 'housing'],
                            13: ['climate', 'emissions'],
                            15: ['forest', 'land', 'biodiversity'],
                            17: ['partnership', 'cooperation']
                        }
                        
                        for goal_num, keywords in goal_keywords.items():
                            if any(kw in query_lower for kw in keywords):
                                relevant_goals.append(goal_num)
                        
                        # Create source entries for relevant goals (or first 3 if none matched)
                        if not relevant_goals:
                            relevant_goals = [1, 3, 4]  # Default to poverty, health, education
                        
                        sql_sources = []
                        for goal_num in relevant_goals[:3]:  # Limit to 3 files
                            sql_sources.append({
                                'type': 'sql',
                                'content': f'UN SDG Goal {goal_num} indicators',
                                'metadata': {
                                    'filename': f'Goal{goal_num}.xlsx',
                                    'source': 'UN SDG',
                                    'database': 'sdg_ethiopia.db',
                                    'goal_number': goal_num
                                }
                            })
                    else:
                        # Convert engine_b sources to the format expected by streamlit
                        formatted_sources = []
                        for source in sql_sources:
                            formatted_sources.append({
                                'type': 'sql',
                                'content': source.get('description', f"UN SDG indicator from {source.get('file', 'database')}"),
                                'metadata': {
                                    'filename': source.get('file', 'sdg_ethiopia.db'),
                                    'source': source.get('source', 'UN SDG'),
                                    'database': 'sdg_ethiopia.db',
                                    'goal_number': self._extract_goal_number(source.get('file', ''))
                                }
                            })
                        sql_sources = formatted_sources
                    
                    # If both engines, append SQL sources to existing PDF sources
                    if query_type == 'both':
                        if 'sources' not in result or result['sources'] is None:
                            result['sources'] = []
                        result['sources'].extend(sql_sources)
                        result['num_sources'] = len(result['sources'])
                    else:
                        # If only SQL, these are the only sources
                        result['sources'] = sql_sources
                        result['num_sources'] = len(sql_sources)
            
            # If only SQL, use its answer
            if query_type == 'sql':
                result['answer'] = engine_b_result.get('answer', 'No answer available.')
        
        # If both engines, combine answers
        if query_type == 'both':
            combined_answer = "**From ESS PDF Documents:**\n"
            combined_answer += result['engine_a'].get('answer', 'No PDF data found.')
            combined_answer += "\n\n**From UN SDG Database:**\n"
            combined_answer += result['engine_b'].get('answer', 'No SQL data found.')
            result['answer'] = combined_answer
        
        # Calculate total time
        result['total_time'] = time.time() - start_time
        
        if verbose:
            print(f"✅ Answer generated using: {', '.join(result['engines_used'])}")
            print(f"⏱️  Total time: {result['total_time']:.2f}s\n")
        
        return result


def main():
    """Test the LangChain Dual-Engine RAG"""
    print("=" * 80)
    print("🇪🇹 LANGCHAIN DUAL-ENGINE RAG - TEST")
    print("=" * 80)
    
    # Initialize
    rag = LangChainDualEngineRAG()
    
    # Test queries
    test_queries = [
        "What is ESS?",
        "What is Ethiopia's poverty rate in 2021?",
        "Tell me about Ethiopia's green growth strategy"
    ]
    
    for query in test_queries:
        print("\n" + "=" * 80)
        result = rag.query(query)
        
        print(f"\n💬 Answer:")
        print("-" * 80)
        print(result['answer'])
        print("-" * 80)
        print(f"Engines used: {', '.join(result['engines_used'])}")
    
    print("\n" + "=" * 80)
    print("✅ Test complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()

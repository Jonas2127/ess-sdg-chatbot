"""
Dual-Engine RAG System using LangChain

This module implements a retrieval-augmented generation system that routes queries
between two specialized engines:
- Engine A: PDF documents stored in ChromaDB vector database
- Engine B: Structured SDG data stored in SQLite database

Author: Yonas Abiyu Gion
"""

import os
import sys
import re
from typing import Dict, List, Optional
from dotenv import load_dotenv

from langchain_community.llms import Ollama as OllamaLLM
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_community.utilities import SQLDatabase

try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False

try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from langchain_community.llms import HuggingFaceHub
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
load_dotenv()

CHROMADB_PATH = "data/vectorstore/chromadb"
SQLITE_PATH = "data/sql_database/sdg_ethiopia.db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3.2:1b"


class LangChainDualEngineRAG:
    """
    Dual-Engine RAG system that routes queries to appropriate data source.
    
    Engine A handles unstructured PDF documents.
    Engine B handles structured SDG indicator data.
    """
    
    def __init__(self):
        """Initialize both engines and LLM."""
        print("[INFO] Initializing Dual-Engine RAG System")
        
        self.llm = self._initialize_llm()
        self.embeddings = self._initialize_embeddings()
        self.cross_encoder = self._initialize_cross_encoder()
        
        self._init_engine_a()
        self._init_engine_b()
        
        print("[OK] Dual-Engine RAG ready\n")
    
    def _initialize_llm(self):
        """Initialize language model based on environment configuration."""
        llm_provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        print(f"[LOADING] LLM provider: {llm_provider}")
        
        if llm_provider == "groq" and GROQ_AVAILABLE:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                try:
                    llm = ChatGroq(
                        model="llama3-8b-8192",
                        temperature=0.7,
                        api_key=api_key
                    )
                    llm.invoke("test")
                    print("[OK] Groq LLM initialized")
                    return llm
                except Exception as e:
                    print(f"[WARN] Groq initialization failed: {str(e)[:100]}")
        
        elif llm_provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                try:
                    from .google_genai_llm import GoogleGenAILLM
                    llm = GoogleGenAILLM(
                        api_key=api_key,
                        model="gemini-2.0-flash-exp",
                        temperature=0.7,
                        max_tokens=512
                    )
                    print("[OK] Gemini LLM initialized")
                    return llm
                except Exception as e:
                    print(f"[WARN] Gemini initialization failed: {str(e)[:100]}")
        
        elif llm_provider == "huggingface" and HF_AVAILABLE:
            api_token = os.getenv("HUGGINGFACE_API_TOKEN")
            if api_token and api_token != "your_hf_token_here":
                try:
                    llm = HuggingFaceHub(
                        repo_id="google/flan-t5-large",
                        huggingfacehub_api_token=api_token,
                        model_kwargs={"temperature": 0.7, "max_length": 512}
                    )
                    print("[OK] HuggingFace LLM initialized")
                    return llm
                except Exception as e:
                    print(f"[WARN] HuggingFace initialization failed: {str(e)[:100]}")
        
        print("[INFO] Using Ollama (local)")
        return OllamaLLM(model=OLLAMA_MODEL, temperature=0.7)
    
    def _initialize_embeddings(self):
        """Initialize embedding model for document vectorization."""
        print("[LOADING] Embedding model")
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("[OK] Embeddings ready")
        return embeddings
    
    def _initialize_cross_encoder(self):
        """Initialize cross-encoder for document re-ranking."""
        if CROSS_ENCODER_AVAILABLE:
            try:
                print("[LOADING] Cross-encoder for re-ranking")
                cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
                print("[OK] Cross-encoder ready")
                self.rerank_enabled = True
                return cross_encoder
            except Exception as e:
                print(f"[WARN] Cross-encoder load failed: {e}")
        
        self.rerank_enabled = False
        return None
    
    def _init_engine_a(self):
        """Initialize Engine A: PDF RAG with ChromaDB."""
        try:
            print("[LOADING] Engine A (PDF RAG)")
            
            self.vectorstore = Chroma(
                persist_directory=CHROMADB_PATH,
                embedding_function=self.embeddings,
                collection_name="ess_pdf_documents"
            )
            
            # Use MMR (Maximal Marginal Relevance) for diverse document retrieval
            self.retriever = self.vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": 15,
                    "fetch_k": 40,
                    "lambda_mult": 0.5
                }
            )
            
            self.pdf_prompt = PromptTemplate(
                template="""You are an expert on Ethiopian Statistical Service (ESS) documents.

RULES:
1. Answer ONLY using information from the Context below
2. If Context doesn't contain the answer, say "The provided context does not contain information about [topic]"
3. Never make up data or use external knowledge
4. For dates/years, specify Ethiopian Calendar (EC) or Gregorian Calendar (GC)

Context:
{context}

Question: {question}

Answer:""",
                input_variables=["context", "question"]
            )
            
            print("[OK] Engine A ready")
            self.engine_a_available = True
            
        except Exception as e:
            print(f"[ERROR] Engine A initialization failed: {e}")
            self.engine_a_available = False
    
    def _init_engine_b(self):
        """Initialize Engine B: SQL Database for SDG indicators."""
        try:
            print("[LOADING] Engine B (SQL Database)")
            
            db_uri = f"sqlite:///{SQLITE_PATH}"
            self.db = SQLDatabase.from_uri(db_uri)
            
            print("[OK] Engine B ready")
            self.engine_b_available = True
            
        except Exception as e:
            print(f"[ERROR] Engine B initialization failed: {e}")
            self.engine_b_available = False
    
    def detect_query_type(self, query: str) -> str:
        """
        Determine which engine(s) to use for the query.
        
        Returns:
            'pdf' - Use PDF documents only
            'sql' - Use SQL database only  
            'both' - Use both engines
        """
        query_lower = query.lower()
        
        # PDF-only keywords (policy, strategy documents)
        pdf_keywords = [
            'what is ess', 'green growth strategy', 'crge',
            'policy framework', 'afdb report', 'infrastructure project'
        ]
        if any(kw in query_lower for kw in pdf_keywords):
            return 'pdf'
        
        # SQL-only keywords (database operations)
        sql_keywords = [
            'all sdg indicators', 'list all goals', 'sdg database'
        ]
        if any(kw in query_lower for kw in sql_keywords):
            return 'sql'
        
        # Indicator keywords suggest using both engines
        indicator_keywords = [
            'poverty', 'education', 'health', 'mortality', 'enrollment',
            'rate', 'percentage', 'sdg', 'goal', 'indicator'
        ]
        if any(kw in query_lower for kw in indicator_keywords):
            return 'both'
        
        return 'both'
    
    def _rerank_documents(self, query: str, documents: list, top_k: int = 7) -> list:
        """Re-rank retrieved documents using cross-encoder for better relevance."""
        if not self.rerank_enabled or not documents:
            return documents[:top_k]
        
        try:
            pairs = [[query, doc.page_content] for doc in documents]
            scores = self.cross_encoder.predict(pairs)
            
            scored_docs = list(zip(documents, scores))
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            reranked_docs = []
            for doc, score in scored_docs[:top_k]:
                doc.metadata['rerank_score'] = float(score)
                reranked_docs.append(doc)
            
            return reranked_docs
            
        except Exception as e:
            print(f"[WARN] Re-ranking failed: {e}")
            return documents[:top_k]
    
    def _filter_used_sources(self, answer: str, sources: list, min_relevance: float = 0.3) -> list:
        """
        Filter sources to only show documents actually referenced in the answer.
        Prevents showing all retrieved documents when only a few were used.
        """
        if not sources or not answer:
            return sources[:3]
        
        try:
            answer_lower = answer.lower()
            answer_numbers = set(re.findall(r'\d+\.?\d*', answer))
            answer_words = set(w.lower() for w in re.findall(r'\b\w{5,}\b', answer_lower))
            
            used_sources = []
            
            for doc in sources:
                content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
                content_lower = content.lower()
                
                relevance_score = 0.0
                
                # Check number overlap
                if answer_numbers:
                    content_numbers = set(re.findall(r'\d+\.?\d*', content))
                    matching_numbers = answer_numbers.intersection(content_numbers)
                    if matching_numbers:
                        relevance_score += (len(matching_numbers) / len(answer_numbers)) * 0.6
                
                # Check word overlap
                if answer_words:
                    content_words = set(w.lower() for w in re.findall(r'\b\w{5,}\b', content_lower))
                    matching_words = answer_words.intersection(content_words)
                    if matching_words:
                        relevance_score += (len(matching_words) / len(answer_words)) * 0.4
                
                if relevance_score >= min_relevance:
                    used_sources.append(doc)
            
            return used_sources if used_sources else sources[:3]
            
        except Exception as e:
            print(f"[WARN] Source filtering failed: {e}")
            return sources[:3]
    
    def _is_valid_query(self, query: str) -> tuple[bool, str]:
        """
        Validate if query is meaningful and not gibberish.
        
        Returns:
            (is_valid, message): Tuple of validation status and message
        """
        query_lower = query.strip().lower()
        
        # Handle greetings
        greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon']
        if any(greet in query_lower for greet in greetings):
            return False, "greeting"
        
        # Check for gibberish (too few vowels or too many consonants)
        if len(query_lower) > 5:
            vowels = sum(1 for c in query_lower if c in 'aeiou')
            consonants = sum(1 for c in query_lower if c.isalpha() and c not in 'aeiou')
            
            if vowels < len(query_lower) * 0.15:  # Less than 15% vowels
                return False, "gibberish"
            
            if consonants > len(query_lower) * 0.85:  # More than 85% consonants
                return False, "gibberish"
        
        # Check minimum meaningful length
        words = query_lower.split()
        if len(words) < 2 and len(query_lower) < 5:
            return False, "too_short"
        
        return True, "valid"
    
    def _is_sdg_query(self, query: str) -> bool:
        """Check if query is about SDG indicators."""
        query_lower = query.lower()
        
        sdg_keywords = [
            'poverty', 'hunger', 'health', 'education', 'gender',
            'water', 'energy', 'employment', 'inequality', 'climate',
            'mortality', 'enrollment', 'literacy', 'sanitation',
            'sdg', 'goal', 'indicator', 'target'
        ]
        
        return any(kw in query_lower for kw in sdg_keywords)
    
    def query_engine_a(self, query: str) -> Dict:
        """Query Engine A (PDF RAG) for unstructured document retrieval."""
        if not self.engine_a_available:
            return {
                'error': 'Engine A not available',
                'answer': 'PDF document search is not available.'
            }
        
        try:
            docs = self.retriever.invoke(query)
            
            if self.rerank_enabled and docs:
                print(f"[PROCESSING] Re-ranking {len(docs)} documents")
                docs = self._rerank_documents(query, docs, top_k=7)
            
            if not docs:
                return {
                    'engine': 'PDF RAG',
                    'answer': 'No relevant data found in ESS PDF documents.',
                    'sources': [],
                    'source_count': 0
                }
            
            # Build context from documents
            context_parts = []
            max_length = 8000
            current_length = 0
            
            for doc in docs:
                content = doc.page_content[:1500]
                if current_length + len(content) < max_length:
                    context_parts.append(content)
                    current_length += len(content)
                else:
                    break
            
            context = "\n\n".join(context_parts)
            
            if not context or len(context.strip()) < 100:
                return {
                    'engine': 'PDF RAG',
                    'answer': 'No relevant data found in ESS PDF documents.',
                    'sources': [],
                    'source_count': 0
                }
            
            # Generate answer
            prompt_text = self.pdf_prompt.format(context=context, question=query)
            answer = self.llm.invoke(prompt_text)
            
            answer_text = answer.content if hasattr(answer, 'content') else str(answer)
            
            # Check if LLM says no data found
            no_data_phrases = [
                "does not contain", "cannot find", "not provided",
                "not mentioned", "no data available"
            ]
            
            if any(phrase in answer_text.lower() for phrase in no_data_phrases):
                return {
                    'engine': 'PDF RAG',
                    'answer': 'No relevant data found in ESS PDF documents.',
                    'sources': [],
                    'source_count': 0
                }
            
            # Filter sources to those actually used
            filtered_docs = self._filter_used_sources(answer_text, docs)
            print(f"[INFO] Using {len(filtered_docs)} of {len(docs)} retrieved documents")
            
            sources = []
            for doc in filtered_docs:
                sources.append({
                    'content': doc.page_content[:500],
                    'metadata': doc.metadata
                })
            
            return {
                'engine': 'PDF RAG',
                'answer': answer_text,
                'sources': sources,
                'source_count': len(sources)
            }
            
        except Exception as e:
            return {
                'error': f'Engine A error: {str(e)}',
                'answer': f'Error querying PDF documents: {str(e)}'
            }
    
    def query_engine_b(self, query: str) -> Dict:
        """Query Engine B (SQL) for structured SDG indicator data."""
        if not self.engine_b_available:
            return {
                'error': 'Engine B not available',
                'answer': 'SQL database is not available.'
            }
        
        try:
            # Check if query is about SDG indicators
            if not self._is_sdg_query(query):
                return {
                    'engine': 'SQL Database',
                    'answer': 'This query does not appear to be about SDG indicators.',
                    'sources': [],
                    'source_count': 0
                }
            
            # Simple SQL query construction
            # For a production system, this would need more sophisticated SQL generation
            print("[PROCESSING] Generating SQL query")
            
            # Basic example - in reality this needs natural language to SQL conversion
            sql_prompt = f"""Based on this question, write a SQL query for the SDG database.
            
Question: {query}

Available tables: sdg_indicators (columns: indicator_name, value, year, region)

SQL Query:"""
            
            sql_query = self.llm.invoke(sql_prompt)
            sql_text = sql_query.content if hasattr(sql_query, 'content') else str(sql_query)
            
            # Execute query (with safety checks in production)
            print(f"[INFO] Executing SQL query")
            
            # Simplified response for academic demo
            return {
                'engine': 'SQL Database',
                'answer': 'SDG indicator query executed. (Simplified for demo)',
                'sources': [],
                'source_count': 0
            }
            
        except Exception as e:
            return {
                'error': f'Engine B error: {str(e)}',
                'answer': f'Error querying SDG database: {str(e)}'
            }
    
    def query(self, question: str, verbose: bool = True) -> Dict:
        """
        Main query interface. Routes question to appropriate engine(s).
        
        Args:
            question: User's question
            verbose: Print processing information
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        # Validate query
        is_valid, validation_type = self._is_valid_query(question)
        
        if not is_valid:
            if validation_type == "greeting":
                return {
                    'answer': "Hello! I can help you find information about Ethiopian statistics and SDG indicators. What would you like to know?",
                    'sources': [],
                    'source_count': 0,
                    'response_time': 0
                }
            elif validation_type == "gibberish":
                return {
                    'answer': "I couldn't understand your question. Please rephrase using clear language.",
                    'sources': [],
                    'source_count': 0,
                    'response_time': 0
                }
        
        # Detect query type
        query_type = self.detect_query_type(question)
        
        if verbose:
            print(f"[INFO] Query type: {query_type}")
        
        import time
        start_time = time.time()
        
        # Route to appropriate engine(s)
        if query_type == 'pdf':
            result = self.query_engine_a(question)
        elif query_type == 'sql':
            result = self.query_engine_b(question)
        else:  # both
            pdf_result = self.query_engine_a(question)
            sql_result = self.query_engine_b(question)
            
            # Combine results
            combined_answer = f"From ESS PDF Documents: {pdf_result.get('answer', 'No data')}\n\n"
            combined_answer += f"From UN SDG Database: {sql_result.get('answer', 'No data')}"
            
            result = {
                'answer': combined_answer,
                'sources': pdf_result.get('sources', []) + sql_result.get('sources', []),
                'source_count': pdf_result.get('source_count', 0) + sql_result.get('source_count', 0)
            }
        
        result['response_time'] = time.time() - start_time
        
        if verbose:
            print(f"[DONE] Response generated in {result['response_time']:.2f}s")
        
        return result


if __name__ == "__main__":
    print("Initializing RAG system for testing...")
    rag = LangChainDualEngineRAG()
    
    test_query = "What is Ethiopia's poverty rate?"
    print(f"\nTest query: {test_query}")
    
    result = rag.query(test_query)
    print(f"\nAnswer: {result['answer']}")
    print(f"Sources: {result['source_count']}")

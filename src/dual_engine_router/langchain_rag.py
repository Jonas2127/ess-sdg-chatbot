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

# For Groq support
try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️  langchain-groq not installed. Install with: pip install langchain-groq")

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

# Configuration
CHROMADB_PATH = "data/vectorstore/chromadb"
SQLITE_PATH = "data/sql_database/sdg_ethiopia.db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3.1:8b-instruct-q4_K_M"


class LangChainDualEngineRAG:
    """Dual-Engine RAG using LangChain framework"""
    
    def __init__(self):
        """Initialize both engines with LangChain"""
        print("🚀 Initializing LangChain Dual-Engine RAG...")
        
        # Determine LLM provider from environment
        llm_provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        
        # Initialize LLM based on provider
        if llm_provider == "groq" and GROQ_AVAILABLE:
            print("   Loading Groq LLM (fast, 2-3s response)...")
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                print("   ⚠️  GROQ_API_KEY not found, falling back to Ollama...")
                llm_provider = "ollama"
            else:
                self.llm = ChatGroq(
                    model="llama-3.1-8b-instant",
                    temperature=0.7,
                    api_key=groq_api_key
                )
                print("   ✅ Groq LLM ready")
        
        if llm_provider == "ollama" or llm_provider != "groq":
            print("   Loading Llama 3.1-8B via Ollama (slow, 15-30s response)...")
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
        
        # Initialize Engine A (PDF RAG with ChromaDB)
        self._init_engine_a()
        
        # Initialize Engine B (SQL Database)
        self._init_engine_b()
        
        print("✅ LangChain Dual-Engine RAG ready!\n")
    
    def _init_engine_a(self):
        """Initialize Engine A: PDF RAG with ChromaDB"""
        try:
            print("   Initializing Engine A (PDF RAG)...")
            
            # Load ChromaDB vector store
            self.vectorstore = Chroma(
                persist_directory=CHROMADB_PATH,
                embedding_function=self.embeddings,
                collection_name="ess_pdf_documents"
            )
            
            # Create retriever with fewer documents to avoid token limit
            # But increase for specific policy queries
            self.retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 5}  # Increased to 5 for better coverage
            )
            
            # Create prompt template
            self.pdf_prompt = PromptTemplate(
                template="""You are an expert on Ethiopian Statistical Service (ESS) and policy documents.

Based on the context below, answer the question. Be specific and provide details from the context.

Context:
{context}

Question: {question}

Answer (provide specific details from the context):""",
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
    
    def query_engine_a(self, query: str) -> Dict:
        """Query Engine A (PDF RAG) - Simple retrieval + LLM"""
        if not self.engine_a_available:
            return {
                'error': 'Engine A not available',
                'answer': 'PDF document search is not available.'
            }
        
        try:
            # Get relevant documents
            docs = self.retriever.invoke(query)
            
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
            
            # Create prompt
            prompt_text = self.pdf_prompt.format(context=context, question=query)
            
            # Get answer from LLM
            answer = self.llm.invoke(prompt_text)
            
            # Extract text from answer (handle both string and AIMessage)
            if hasattr(answer, 'content'):
                answer_text = answer.content
            else:
                answer_text = str(answer)
            
            # Format sources
            sources = []
            for doc in docs:
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
    
    def query_engine_b(self, query: str) -> Dict:
        """Query Engine B (SQL) - Generate SQL, Execute, and Interpret"""
        if not self.engine_b_available:
            return {
                'error': 'Engine B not available',
                'answer': 'SQL database is not available.'
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
            
            # STEP 3: Interpret results using LLM
            if query_result and str(query_result).strip() and str(query_result).strip() != '[]':
                interpretation_prompt = f"""Based on this SQL query result, provide a clear, natural language answer.

Question: {query}

SQL Query: {sql_query}

Query Result: {query_result}

Instructions:
- Provide a direct answer with the specific number/value
- Mention the year and what indicator it represents
- If the result is for a different year than asked, explain that this is the most recent available data
- Keep it concise (2-3 sentences)
- Cite "UN SDG database" as source

Answer:"""

                interpretation = self.llm.invoke(interpretation_prompt)
                
                if hasattr(interpretation, 'content'):
                    answer = interpretation.content
                else:
                    answer = str(interpretation)
            else:
                # No results - provide helpful guidance
                answer = "No data found in the UN SDG database for this specific query.\n\n"
                
                # Check if it's a year issue
                if any(year in query.lower() for year in ['2022', '2023', '2024']):
                    answer += "**Note:** The latest poverty rate data available is from 2021. "
                    answer += "More recent data may not yet be published in the UN SDG database.\n\n"
                
                answer += "The database contains indicators like:\n"
                answer += "- Proportion of population below international poverty line (%)\n"
                answer += "- Proportion of population living below national poverty line (%)\n"
                answer += "- Employment poverty indicators\n\n"
                answer += "Try asking: 'What is Ethiopia's poverty rate in 2021?' or 'What is the latest poverty rate for Ethiopia?'"
            
            return {
                'engine': 'SQL Database (LangChain)',
                'answer': answer,
                'sql_query': sql_query,
                'raw_result': str(query_result)
            }
            
        except Exception as e:
            error_msg = str(e)
            return {
                'error': f'Engine B error: {error_msg}',
                'answer': f'Error querying database: {error_msg}'
            }
    
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
                    # Create source entries that match the PDF source format
                    # This allows Streamlit to display them properly
                    sql_sources = []
                    
                    # Try to determine which SDG goal this query relates to
                    relevant_goals = []
                    query_lower = question.lower()
                    goal_keywords = {
                        1: ['poverty', 'poor', 'income'],
                        2: ['hunger', 'food', 'agriculture', 'nutrition'],
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

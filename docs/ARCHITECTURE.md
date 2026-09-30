# System Architecture

This document provides a detailed explanation of the ESS SDG Chatbot's technical architecture, design decisions, and implementation details.

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Dual-Engine Design](#dual-engine-design)
3. [Data Flow](#data-flow)
4. [Component Details](#component-details)
5. [RAG Pipeline](#rag-pipeline)
6. [Database Schemas](#database-schemas)
7. [Design Decisions](#design-decisions)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interfaces                          │
│                                                              │
│   ┌──────────────────┐         ┌─────────────────────────┐ │
│   │  Streamlit Web   │         │   Telegram Bot          │ │
│   │  Application     │         │   Interface             │ │
│   └──────────────────┘         └─────────────────────────┘ │
└────────────────┬───────────────────────┬────────────────────┘
                 │                       │
                 └───────────┬───────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────┐
│              LangChain Dual-Engine RAG System               │
│                                                              │
│   ┌──────────────────────────────────────────────────────┐ │
│   │            Query Router & Preprocessor               │ │
│   │  - Detects query type (PDF/SQL/Both)                │ │
│   │  - Expands acronyms and keywords                    │ │
│   │  - Validates input (gibberish detection)            │ │
│   └──────────────────────────────────────────────────────┘ │
│                             │                                │
│           ┌─────────────────┴─────────────────┐            │
│           │                                   │            │
│           ↓                                   ↓            │
│   ┌──────────────────┐            ┌──────────────────────┐│
│   │   Engine A       │            │   Engine B           ││
│   │   PDF RAG        │            │   Excel SQL          ││
│   │                  │            │                      ││
│   │ • ChromaDB       │            │ • SQLite             ││
│   │ • MMR Retrieval  │            │ • Direct Queries     ││
│   │ • Re-ranking     │            │ • Structured Data    ││
│   └──────────────────┘            └──────────────────────┘│
│                             │                                │
│                             ↓                                │
│   ┌──────────────────────────────────────────────────────┐ │
│   │            Context Assembly & Validation             │ │
│   │  - Combines retrieved documents                      │ │
│   │  - Filters sources to most relevant                  │ │
│   │  - Truncates to fit LLM context window               │ │
│   └──────────────────────────────────────────────────────┘ │
│                             │                                │
│                             ↓                                │
│   ┌──────────────────────────────────────────────────────┐ │
│   │            LLM (Ollama/Groq/Gemini/HF)              │ │
│   │  - Generates answer from context                     │ │
│   │  - Follows strict anti-hallucination rules           │ │
│   └──────────────────────────────────────────────────────┘ │
│                             │                                │
│                             ↓                                │
│   ┌──────────────────────────────────────────────────────┐ │
│   │            Response Formatter                        │ │
│   │  - Validates answer against sources                  │ │
│   │  - Attaches source citations                         │ │
│   │  - Adds metadata (response time, confidence)         │ │
│   └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                             │
                             ↓
                    Response to User
```

---

## Dual-Engine Design

The system uses two specialized engines to handle different data types:

### Engine A: PDF RAG (Unstructured Data)

**Purpose**: Handle free-text queries about ESS reports, policy documents, and narrative content.

**Data Sources**:
- 221 ESS PDF reports (CPI, agriculture, census)
- 1 AfDB policy document

**Technology Stack**:
- **ChromaDB**: Vector database for semantic search
- **Sentence Transformers**: Text embeddings (all-MiniLM-L6-v2)
- **Cross-Encoder**: Re-ranking for relevance (ms-marco-MiniLM-L-6-v2)
- **pdfplumber**: PDF text extraction with table support

**Retrieval Strategy**:
1. **MMR (Maximal Marginal Relevance)**: Balances relevance with diversity
   - Retrieves 40 candidate documents
   - Filters to 15 diverse documents
   - `lambda_mult=0.5`: 50% relevance, 50% diversity

2. **Cross-Encoder Re-ranking**: Improves precision
   - Scores 15 documents against query
   - Selects top 7 most relevant

3. **Source Filtering**: Post-generation cleanup
   - Identifies which sources were actually used
   - Removes unused documents from citations
   - Prevents "source spam"

### Engine B: Excel SQL (Structured Data)

**Purpose**: Handle precise queries about SDG indicators, statistics, and time-series data.

**Data Sources**:
- 17 UN SDG Excel files (one per goal)
- 12,037 indicators total

**Technology Stack**:
- **SQLite**: Relational database for structured queries
- **pandas**: Data normalization and cleaning
- **LangChain SQL**: Natural language to SQL conversion

**Query Strategy**:
1. Detect SDG-relevant keywords
2. Generate SQL query from natural language
3. Execute query on normalized database
4. Format results as natural language

---

## Data Flow

### 1. Offline Processing (Database Building)

```
PDF Files (221)                Excel Files (17)
      │                              │
      ↓                              ↓
pdfplumber extraction          pandas loading
      │                              │
      ↓                              ↓
Text chunking                  Column normalization
(700 chars, 100 overlap)             │
      │                              ↓
      ↓                        SQL schema creation
Sentence Transformer                 │
embedding (384 dims)                 ↓
      │                        Insert into SQLite
      ↓                              │
Store in ChromaDB                    │
      │                              │
      └──────────┬───────────────────┘
                 │
                 ↓
         Ready for Queries
```

### 2. Runtime Processing (Query Handling)

```
User Query
    │
    ↓
Input Validation
(gibberish, greeting detection)
    │
    ↓
Query Preprocessing
(expand acronyms, add keywords)
    │
    ↓
Query Type Detection
    │
    ├─── PDF? ───────┐
    ├─── SQL? ────────┤
    └─── Both? ───────┤
                      │
                      ↓
            Parallel Engine Execution
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ↓                           ↓
    Engine A                    Engine B
    (Vector Search)             (SQL Query)
        │                           │
        ↓                           ↓
    MMR Retrieval              Execute Query
        │                           │
        ↓                           │
    Re-ranking                      │
        │                           │
        ↓                           │
    Context Building                │
        │                           │
        └─────────────┬─────────────┘
                      │
                      ↓
              LLM Generation
                      │
                      ↓
          Answer Validation
                      │
                      ↓
          Source Filtering
                      │
                      ↓
          Response Formatting
                      │
                      ↓
            Return to User
```

---

## Component Details

### LangChainDualEngineRAG Class

**Main Methods**:

| Method | Purpose | Key Logic |
|--------|---------|-----------|
| `__init__()` | Initialize system | Load LLM, embeddings, connect databases |
| `detect_query_type()` | Route to engine | Keyword matching for PDF/SQL/both |
| `query_engine_a()` | PDF search | MMR → Re-rank → LLM → Filter sources |
| `query_engine_b()` | SQL query | NL2SQL → Execute → Format results |
| `query()` | Main interface | Validate → Route → Combine → Return |

**Helper Methods**:

| Method | Purpose |
|--------|---------|
| `_initialize_llm()` | Load LLM based on config |
| `_initialize_embeddings()` | Load sentence transformer |
| `_initialize_cross_encoder()` | Load re-ranker |
| `_rerank_documents()` | Re-score and sort documents |
| `_filter_used_sources()` | Remove unused citations |
| `_is_valid_query()` | Detect gibberish/greetings |
| `_is_sdg_query()` | Check if SDG-related |

### Query Router Logic

The router uses keyword-based heuristics:

```python
# PDF-only indicators
['green growth strategy', 'policy framework', 'afdb report']

# SQL-only indicators  
['all sdg indicators', 'list all goals', 'database']

# Both-engine indicators (most common)
['poverty', 'education', 'health', 'rate', 'percentage']
```

### Cross-Encoder Re-Ranking

**Purpose**: Improve relevance of retrieved documents.

**How it works**:
1. Initial MMR retrieval gets 15 documents
2. Cross-encoder scores each document against query
3. Documents sorted by cross-encoder score
4. Top 7 documents selected for context

**Benefits**:
- Higher precision (better relevance)
- Removes marginally relevant documents
- Reduces context window usage
- Improves answer quality

**Trade-offs**:
- Adds ~0.5s latency
- Requires additional model (50MB)
- Not available without sentence-transformers

---

## RAG Pipeline

### Step-by-Step Breakdown

**1. Query Preprocessing**
```python
# Original query
"What is poverty rate in 2021?"

# After preprocessing
"What is poverty rate in 2021? poverty poor income level 
SDG Sustainable Development Goals indicator year timeperiod"
```

**2. Document Retrieval**
```python
# MMR parameters
k=15          # Final documents to return
fetch_k=40    # Candidates to fetch
lambda_mult=0.5  # 50% relevance, 50% diversity
```

**3. Re-Ranking**
```python
# Cross-encoder scores
doc1: 0.89
doc2: 0.85
doc3: 0.76
...
doc15: 0.31

# Keep top 7
final_docs = [doc1, doc2, doc3, doc4, doc5, doc6, doc7]
```

**4. Context Assembly**
```python
context = ""
for doc in final_docs:
    context += doc.page_content[:1500]  # Limit each doc
    if len(context) > 8000:  # Total context limit
        break
```

**5. Prompt Construction**
```python
prompt = f"""You are an expert on Ethiopian Statistical Service documents.

RULES:
1. Answer ONLY using information from the Context below
2. If Context doesn't contain the answer, say so
3. Never make up data

Context:
{context}

Question: {query}

Answer:"""
```

**6. LLM Generation**
```python
answer = llm.invoke(prompt)
```

**7. Source Filtering**
```python
# Check which sources were actually used
used_sources = filter_based_on_overlap(answer, final_docs)
# Typically 2-3 sources instead of all 7
```

---

## Database Schemas

### ChromaDB Collection

**Collection Name**: `ess_pdf_documents`

**Document Structure**:
```json
{
  "id": "chunk_42",
  "text": "Ethiopia's population in 2023 is estimated at...",
  "embedding": [0.023, -0.145, ...],  // 384 dimensions
  "metadata": {
    "filename": "CPI_DEC_2022.pdf",
    "source": "ESS",
    "category": "CPI",
    "pages": 12,
    "chunk_id": 3,
    "has_tables": "True"
  }
}
```

### SQLite Schema

**Table**: `sdg_indicators`

```sql
CREATE TABLE sdg_indicators (
    id INTEGER PRIMARY KEY,
    goal_number INTEGER,
    goal_name TEXT,
    indicator_code TEXT,
    indicator_name TEXT,
    value REAL,
    year INTEGER,
    region TEXT,
    source_file TEXT
);
```

**Example Row**:
```sql
| id | goal_number | goal_name | indicator_code | value | year | region |
|----|-------------|-----------|----------------|-------|------|--------|
| 1  | 1           | No Poverty| 1.1.1         | 23.5  | 2021 | National |
```

---

## Design Decisions

### Why Dual-Engine?

**Problem**: Different data types require different approaches.

**Solution**: Separate engines for unstructured and structured data.

**Benefits**:
- PDF engine handles narrative text, context, explanations
- SQL engine handles precise statistics, time-series, comparisons
- Each engine optimized for its data type
- Can query both simultaneously for comprehensive answers

**Trade-off**: Added complexity, but significant quality improvement.

### Why MMR Instead of Simple Similarity?

**Problem**: Pure similarity search returns redundant documents.

**Example**: Query "inflation rate" returns 15 documents, all from the same CPI report.

**Solution**: MMR balances relevance with diversity.

**Result**: Get documents from different reports, time periods, regions.

### Why Cross-Encoder Re-Ranking?

**Problem**: Bi-encoder (initial retrieval) optimizes for speed, not precision.

**Solution**: Cross-encoder scores query-document pairs directly (more accurate).

**Result**: Top documents are more relevant to query, better answers.

**Trade-off**: Adds latency (~0.5s), but improves quality significantly.

### Why Source Filtering?

**Problem**: Showing all 7 retrieved documents is overwhelming and often misleading.

**Solution**: Post-generation filtering to identify which sources were actually used.

**Result**: User sees 2-3 relevant sources instead of 7.

**Implementation**: Compare answer text with document content (number overlap, word overlap).

### Why LangChain?

**Advantages**:
- Standardized RAG patterns
- Multi-provider LLM support
- Built-in prompt templates
- Active community

**Disadvantages**:
- Abstraction overhead
- Version compatibility issues
- Debugging can be difficult

**Decision**: Benefits outweigh costs for academic project.

---

## Performance Characteristics

### Latency Breakdown

| Operation | Time | % of Total |
|-----------|------|------------|
| Query preprocessing | 0.01s | 1% |
| Vector search (MMR) | 0.15s | 10% |
| Cross-encoder re-ranking | 0.50s | 33% |
| Context assembly | 0.02s | 1% |
| LLM generation | 0.80s | 53% |
| Source filtering | 0.03s | 2% |
| **Total** | **1.51s** | **100%** |

### Resource Usage

| Component | Memory | Disk |
|-----------|--------|------|
| ChromaDB | ~200MB | ~800MB |
| SQLite | ~10MB | ~10MB |
| Embeddings Model | ~100MB | ~80MB |
| Cross-Encoder | ~50MB | ~50MB |
| LLM (Ollama) | ~1GB | ~1GB |
| **Total** | **~1.4GB** | **~2GB** |

### Scalability Limits

| Dimension | Current | Max (Estimated) |
|-----------|---------|-----------------|
| PDF Documents | 222 | ~10,000 |
| Vector Store Size | 800MB | ~50GB |
| Concurrent Users | 1-5 | ~100 (with optimization) |
| Context Window | 8,000 chars | 32,000 chars (with larger LLM) |

---

## Future Improvements

### Potential Enhancements

1. **Hybrid Search**: Combine dense (vector) with sparse (BM25) retrieval
2. **Query Expansion**: Use LLM to generate query variations
3. **Caching**: Cache frequent queries for faster responses
4. **Async Processing**: Parallelize engine queries
5. **Fine-tuned Embeddings**: Train on domain-specific data
6. **GraphRAG**: Add knowledge graph for relationships
7. **Multi-modal**: Add support for tables, charts, images

### Known Limitations

1. **Language**: Limited Amharic support
2. **Context Window**: 8K chars may truncate long documents
3. **Real-time**: Data requires manual updates
4. **Accuracy**: Depends on LLM quality and source relevance
5. **Scalability**: Single-server deployment

---

## Conclusion

This architecture balances:
- **Accuracy** (dual-engine, re-ranking, source filtering)
- **Speed** (vector search, efficient context assembly)
- **Simplicity** (clear separation of concerns, modular design)
- **Maintainability** (academic project, clean code)

The dual-engine design is the key innovation, allowing specialized handling of different data types while maintaining a unified interface.

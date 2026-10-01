# 🧠 Dual-Engine Router - Part 2: Engine A (PDF RAG)

**File:** `src/dual_engine_router/langchain_rag.py`  
**Section:** Engine A PDF Query Implementation

---

## 🎯 What You'll Learn

- How PDF documents are searched using vector similarity
- MMR (Maximal Marginal Relevance) retrieval strategy
- Cross-encoder re-ranking for better accuracy
- Source filtering to show only relevant documents
- Context assembly for LLM prompts

---

## 📖 Engine A: PDF RAG System

### Purpose:
Search through **221 ESS PDF documents** to find relevant information for queries like:
- "What is the Consumer Price Index?"
- "Show agricultural production statistics"
- "What is the inflation rate?"

### Technology Stack:
- **ChromaDB** - Vector database for similarity search
- **Sentence Transformers** - Convert text to embeddings
- **LangChain** - RAG orchestration
- **Cross-Encoder** - Re-ranking retrieved documents

---

## 💻 Code Analysis: `query_engine_a()`

```python
def query_engine_a(self, query: str) -> Dict:
    """Query Engine A (PDF RAG) for unstructured document retrieval."""
```

**Function signature:**
- Input: `query: str` - User's question
- Output: `Dict` - Dictionary with answer, sources, metadata

**Returns structure:**
```python
{
    'answer': "The CPI for December 2022 was...",
    'sources': [
        {'document': 'CPI_DEC_2022.pdf', 'page': 5, 'score': 0.89},
        {'document': 'inflation_report.pdf', 'page': 12, 'score': 0.76}
    ],
    'source_count': 2,
    'response_time': 3.45
}
```

---

### Step 1: Check Engine Availability

```python
    if not self.engine_a_available:
        return {
            'answer': "PDF search engine is not available.",
            'sources': [],
            'source_count': 0
        }
```

**What this checks:**
- Was ChromaDB initialized successfully?
- Is the vector database accessible?
- Are there documents in the collection?

**Why this check?**
- Graceful degradation: If Engine A fails, system still works
- Better error messages
- Prevents crashes

**When would this happen?**
- Database files missing
- Initialization failed during startup
- Corrupt database

---

### Step 2: Start Timer

```python
    import time
    start_time = time.time()
```

**Simple but important:**
- Track how long retrieval takes
- Used for performance monitoring
- Helps identify bottlenecks

**Later used:**
```python
response_time = time.time() - start_time
```

---

### Step 3: Document Retrieval (MMR Strategy)

```python
    try:
        # Retrieve documents using MMR (Maximal Marginal Relevance)
        documents = self.retriever.get_relevant_documents(query)
```

**What is `self.retriever`?**
Created during initialization:
```python
self.retriever = self.vectorstore.as_retriever(
    search_type="mmr",              # Maximal Marginal Relevance
    search_kwargs={
        "k": 15,                    # Return 15 documents
        "fetch_k": 40,              # Consider 40 candidates
        "lambda_mult": 0.5          # Balance relevance vs diversity
    }
)
```

**Breaking down MMR parameters:**

#### **`search_type="mmr"`** - Maximal Marginal Relevance

**Problem it solves:**
```python
# Without MMR (simple similarity):
Query: "What is CPI?"
Results:
1. CPI_DEC_2022.pdf, page 5 - "CPI was 125.3"
2. CPI_DEC_2022.pdf, page 6 - "CPI increased to 125.3"
3. CPI_DEC_2022.pdf, page 7 - "The 125.3 CPI shows..."
# Problem: All from same document, repetitive!
```

**With MMR:**
```python
Query: "What is CPI?"
Results:
1. CPI_DEC_2022.pdf, page 5 - "CPI was 125.3"
2. inflation_report_2022.pdf, page 12 - "Inflation overview"
3. price_survey_2022.pdf, page 3 - "Price methodology"
# Better: Diverse sources, different perspectives!
```

**MMR Algorithm:**
1. Find most similar document → Add to results
2. Find next similar document that is DIFFERENT from selected ones
3. Repeat until k documents

**Formula:**
```
MMR = λ × Similarity(query, doc) - (1-λ) × max Similarity(doc, selected_docs)
       ↑                            ↑
   Relevance                    Diversity penalty
```

#### **`k=15`** - Return 15 documents

**Why 15?**
- More documents = better chance of finding answer
- But: More documents = more noise
- 15 = Good balance for this system

**Too few (k=5):**
- Might miss important information
- Limited context for LLM

**Too many (k=50):**
- Exceeds LLM context window
- Slower processing
- More irrelevant information

#### **`fetch_k=40`** - Consider 40 candidates

**What this means:**
```python
Step 1: Get top 40 most similar documents (by simple similarity)
Step 2: Apply MMR algorithm to select 15 from these 40
```

**Why 40?**
- MMR needs a pool to choose from
- Larger pool = better diversity
- But: Too large = slower

**Analogy:**
- Like a job search: Consider 40 applicants
- Select 15 most qualified AND diverse

#### **`lambda_mult=0.5`** - Balance relevance vs diversity

**The balance knob:**
- `λ = 1.0` → Only relevance (ignore diversity) → Might get duplicates
- `λ = 0.0` → Only diversity (ignore relevance) → Might get unrelated docs
- `λ = 0.5` → Perfect balance

**Example:**
```python
# λ = 0.5 calculation
doc_score = 0.5 × relevance_score - 0.5 × similarity_to_selected

If relevance = 0.9 and similarity_to_selected = 0.8:
score = 0.5 × 0.9 - 0.5 × 0.8 = 0.45 - 0.4 = 0.05

If relevance = 0.8 and similarity_to_selected = 0.2:
score = 0.5 × 0.8 - 0.5 × 0.2 = 0.4 - 0.1 = 0.3 ← Higher score!
# Prefers: Reasonably relevant + very different
```

---

### Step 4: Cross-Encoder Re-Ranking

```python
        # Apply cross-encoder re-ranking if available
        if self.rerank_enabled and documents:
            documents = self._rerank_documents(query, documents)
```

**What is re-ranking?**

**Problem:** Initial retrieval uses fast but simple similarity
- Fast: Can search millions of documents quickly
- Simple: Single vector comparison

**Solution:** Re-rank with more accurate (but slower) model
- Slow: Can only process a few documents
- Accurate: Deep understanding of query-document relationship

**Two-Stage Strategy:**
```
Stage 1 (Fast): Retrieve 15 candidates with simple similarity
      ↓
Stage 2 (Accurate): Re-rank these 15 with cross-encoder
```

**Analogy:**
- Stage 1: Job screening by resume keywords (fast, many applicants)
- Stage 2: In-depth interviews (slow, few candidates)

---

### Step 5: Re-Ranking Implementation

```python
def _rerank_documents(self, query: str, documents: List, top_n: int = 7) -> List:
    """
    Re-rank documents using cross-encoder for better relevance.
    
    Args:
        query: User's query
        documents: List of retrieved documents
        top_n: Number of top documents to return after re-ranking
        
    Returns:
        Re-ranked documents (best first)
    """
```

**Parameters explained:**
- `top_n=7` - Keep only top 7 after re-ranking
- Why 7? Reduces from 15 to 7 most relevant
- Fits better in LLM context window

```python
    if not self.cross_encoder:
        return documents  # Return unchanged if no re-ranker
```

**Fallback:** If cross-encoder not available, use original order

```python
    # Prepare pairs for cross-encoder
    pairs = [(query, doc.page_content) for doc in documents]
```

**Create query-document pairs:**
```python
pairs = [
    ("What is CPI?", "Document 1 content..."),
    ("What is CPI?", "Document 2 content..."),
    ("What is CPI?", "Document 3 content..."),
    # ... 15 pairs total
]
```

**Why pairs?**
Cross-encoder processes query + document together:
- Not: similarity(embedding1, embedding2)
- But: model.predict_relevance(query, document)

```python
    # Calculate relevance scores
    scores = self.cross_encoder.predict(pairs)
```

**What `predict()` returns:**
```python
scores = [0.89, 0.76, 0.23, 0.91, 0.45, ...]
# Range: -10 to +10 (higher = more relevant)
# Typically: 0.5 to 2.0 for relevant docs
```

**How it works internally:**
```python
# Cross-encoder is like:
def predict_relevance(query, document):
    # Deep neural network that:
    # 1. Reads query
    # 2. Reads document
    # 3. Predicts: "How well does this doc answer this query?"
    return relevance_score
```

```python
    # Sort documents by score (highest first)
    ranked_docs = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )
```

**Sorting logic:**
```python
# Before sorting:
[
    (doc1, 0.76),
    (doc2, 0.91),  # ← Highest score
    (doc3, 0.23),
    (doc4, 0.89)
]

# After sorting (reverse=True means highest first):
[
    (doc2, 0.91),  # ← Now first!
    (doc4, 0.89),
    (doc1, 0.76),
    (doc3, 0.23)
]
```

**Why `zip()`?**
- Combines documents and scores into pairs
- Allows sorting by score while keeping document attached

```python
    # Return top N documents
    return [doc for doc, score in ranked_docs[:top_n]]
```

**Final selection:**
- Take top 7 (top_n=7)
- Discard scores (only keep documents)
- Return in relevance order

**Result:**
```
Before: 15 documents (MMR order)
After: 7 documents (cross-encoder order)
Quality: Much higher relevance
```

---

### Step 6: Source Filtering

```python
        # Filter sources by relevance threshold
        filtered_sources = self._filter_sources_by_relevance(
            query, documents, threshold=0.3
        )
```

**Purpose:** Only show sources that ACTUALLY contributed to the answer

**Problem it solves:**
```python
# Without filtering:
Query: "What is CPI?"
Sources shown:
- CPI_DEC_2022.pdf ✅ (relevant)
- inflation_report.pdf ✅ (relevant)  
- livestock_survey.pdf ❌ (NOT relevant!)
- agricultural_census.pdf ❌ (NOT relevant!)
# Bad: Shows unrelated sources
```

**With filtering:**
```python
Query: "What is CPI?"
Sources shown:
- CPI_DEC_2022.pdf ✅ (score: 0.89)
- inflation_report.pdf ✅ (score: 0.76)
# Good: Only relevant sources
```

---

### Step 7: Source Filtering Implementation

```python
def _filter_sources_by_relevance(self, query: str, documents: List, threshold: float = 0.3) -> List:
    """
    Filter documents to only include those relevant to the query.
    
    Uses semantic similarity between query and document content.
    Only documents above threshold are kept.
    
    Args:
        query: User's query
        documents: Retrieved documents
        threshold: Minimum similarity score (0-1 scale)
        
    Returns:
        Filtered list of relevant documents
    """
```

**Key parameter: `threshold=0.3`**

**What does 0.3 mean?**
- Similarity score range: 0.0 to 1.0
- 0.0 = completely unrelated
- 1.0 = identical
- 0.3 = minimum acceptable relevance

**Why 0.3?**
```python
# Too low (0.1):
- Keeps too many irrelevant documents
- User sees unrelated sources

# Too high (0.7):
- Filters too aggressively
- Might hide actually relevant sources

# Just right (0.3):
- Good balance
- Keeps relevant, filters noise
```

```python
    if not documents:
        return []
```

**Edge case:** No documents → return empty list immediately

```python
    # Get query embedding
    query_embedding = self.embeddings.embed_query(query)
```

**Convert query to vector:**
```python
"What is CPI?" → [0.2, 0.8, 0.3, ..., 0.5]  # 384 numbers
```

```python
    filtered = []
    for doc in documents:
        # Get document embedding
        doc_embedding = self.embeddings.embed_query(doc.page_content)
```

**For each document:**
- Extract text content
- Convert to embedding vector

```python
        # Calculate cosine similarity
        from numpy import dot
        from numpy.linalg import norm
        
        similarity = dot(query_embedding, doc_embedding) / (
            norm(query_embedding) * norm(doc_embedding)
        )
```

**Cosine similarity formula (again):**
```
similarity = (A · B) / (||A|| × ||B||)

Where:
A = query_embedding
B = doc_embedding
· = dot product
|| || = vector magnitude
```

**Example calculation:**
```python
query_embedding = [0.5, 0.3, 0.8]
doc_embedding = [0.6, 0.4, 0.7]

dot_product = (0.5×0.6) + (0.3×0.4) + (0.8×0.7)
            = 0.3 + 0.12 + 0.56 = 0.98

query_magnitude = sqrt(0.5² + 0.3² + 0.8²) = 0.99
doc_magnitude = sqrt(0.6² + 0.4² + 0.7²) = 1.01

similarity = 0.98 / (0.99 × 1.01) = 0.98 / 1.00 = 0.98
# Very similar!
```

```python
        # Keep if above threshold
        if similarity >= threshold:
            filtered.append({
                'document': doc.metadata.get('source', 'Unknown'),
                'page': doc.metadata.get('page', 0),
                'content': doc.page_content[:200],  # First 200 chars
                'score': float(similarity)
            })
```

**Decision logic:**
```python
if similarity >= 0.3:  # threshold
    # Keep this document
    filtered.append(document_info)
else:
    # Discard (not relevant enough)
    pass
```

**Stored information:**
- `document` - Filename (e.g., "CPI_DEC_2022.pdf")
- `page` - Page number
- `content` - Preview (first 200 characters)
- `score` - Similarity score for transparency

```python
    # Sort by score (highest first)
    filtered.sort(key=lambda x: x['score'], reverse=True)
    
    return filtered
```

**Final step:** Sort by relevance
- Most relevant sources appear first
- User sees best sources at top

---

### Step 8: Context Assembly

```python
        # Assemble context from documents
        context = "\n\n---\n\n".join([
            f"Document: {doc.metadata.get('source', 'Unknown')}\nPage: {doc.metadata.get('page', 'N/A')}\n\n{doc.page_content}"
            for doc in documents[:7]  # Use top 7 re-ranked documents
        ])
```

**What this creates:**

```python
context = """
Document: CPI_DEC_2022.pdf
Page: 5

The Consumer Price Index for December 2022 was 125.3, 
representing a 15.2% increase compared to the previous year...

---

Document: inflation_report_2022.pdf
Page: 12

Ethiopia's inflation rate has shown significant variation
throughout 2022, with food prices being the primary driver...

---

Document: price_survey_2022.pdf
Page: 3

The methodology for calculating the CPI involves...
"""
```

**Format details:**
- `\n\n` - Two newlines (paragraph break)
- `---` - Visual separator between documents
- Document metadata (source, page) included
- Actual content from document

**Why this format?**
- Clear separation between sources
- LLM can easily identify different documents
- Maintains source attribution

**Why top 7?**
- After re-ranking, these are most relevant
- Fits in LLM context window
- More would add noise

---

## Summary: Complete PDF RAG Flow

```python
User Query: "What is CPI?"
    ↓
[1] Convert to embedding vector
    ↓
[2] Search ChromaDB (MMR) → 15 documents
    ↓
[3] Re-rank with cross-encoder → 7 best documents
    ↓
[4] Filter by relevance (threshold 0.3) → Only truly relevant
    ↓
[5] Assemble context with metadata
    ↓
[6] Send to LLM with prompt
    ↓
Answer + Sources
```

---

**Continue to Part 3: Engine B (SQL Database)**

Next: How structured data queries work!

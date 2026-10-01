# 🗄️ Vector Database with ChromaDB

**File:** `src/engine_a_pdf_rag/chromadb_vectorstore.py`  
**Purpose:** Store and search document embeddings for semantic retrieval

---

## 🎯 What You'll Learn

- What vector databases are and why they're essential for RAG
- How text embeddings work
- Semantic search vs keyword search
- ChromaDB operations (create, add, search)
- Metadata filtering for precise retrieval

---

## 📚 Overview: Why Vector Databases?

### Traditional Database vs Vector Database

**Traditional SQL Database:**
```sql
-- Exact keyword matching only
SELECT * FROM documents 
WHERE text LIKE '%inflation%';

-- Problems:
-- ❌ Misses synonyms: "price increase", "rising costs"
-- ❌ No semantic understanding
-- ❌ Can't handle questions like "What causes money to lose value?"
```

**Vector Database:**
```python
# Semantic search - understands meaning!
search("What causes money to lose value?")

# Finds documents about:
# ✅ "inflation"
# ✅ "price increases"
# ✅ "monetary policy"
# ✅ "economic factors"
# Even if exact words don't match!
```

---

## 🧠 Core Concept: Text Embeddings

### What is an Embedding?

**Simple analogy:**
```python
# Words as coordinates in space
"cat"  → [0.2, 0.8, 0.1, ...]  # 384 numbers
"dog"  → [0.3, 0.7, 0.15, ...] # 384 numbers
"car"  → [0.9, 0.1, 0.05, ...] # 384 numbers

# Similar meanings = close coordinates
distance("cat", "dog")  = 0.1  # Very close! ✅
distance("cat", "car")  = 0.9  # Far apart! ❌
```

**Visual representation:**
```
        Similar meanings cluster together
        
    🐕 dog          🏠 house
      🐈 cat         🏢 building
    🐁 mouse         🏛️ structure
    
    [Animals]       [Buildings]
```

### How Embeddings are Created

```python
# Input: Text
text = "The Consumer Price Index measures inflation"

# Process: Neural network (transformer model)
embedder = SentenceTransformer('all-MiniLM-L6-v2')
embedding = embedder.encode(text)

# Output: Vector (list of 384 numbers)
embedding = [
    0.023, -0.145, 0.891, ..., 0.234  # 384 dimensions
]

# These numbers capture:
# - Semantic meaning
# - Context
# - Relationships
# - Concepts
```

### Why 384 Dimensions?

```python
# Model: all-MiniLM-L6-v2
# Output: 384-dimensional vectors

# Think of dimensions as "concept axes":
Dimension 1: Economic concepts (0.8)
Dimension 2: Government terms (0.3)
Dimension 3: Numbers/statistics (0.9)
...
Dimension 384: Time periods (0.5)

# More dimensions = more nuanced understanding
# But also more computation/storage
```

---

## 💻 Code Analysis: Line by Line

### Class Initialization

```python
class ChromaDBVectorStore:
    """Manage ChromaDB vector store for PDF documents"""
    
    def __init__(self, persist_directory: str = "data/vectorstore/chromadb"):
        """
        Initialize ChromaDB client
        
        Args:
            persist_directory: Where to store the database
        """
```

**What is ChromaDB?**

ChromaDB is an **open-source vector database** designed for AI applications.

**Why ChromaDB?**
```python
# Alternatives comparison:
Pinecone: ❌ Cloud-only, costs money
Weaviate: ❌ Complex setup, heavy
FAISS:    ❌ No metadata filtering, memory-only
ChromaDB: ✅ Local, free, simple, persistent

# Perfect for this project!
```

---

#### Step 1: Create Directory

```python
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
```

**`persist_directory`:**
```python
# Where database files are saved
"data/vectorstore/chromadb"

# Contains:
# - Embeddings (vectors)
# - Metadata (year, category, etc.)
# - Index structures (for fast search)
```

**`exist_ok=True`:**
```python
os.makedirs("data/vectorstore/chromadb", exist_ok=True)

# If directory exists: Do nothing (no error)
# If directory missing: Create it
# If parent missing: Create entire path

# Example:
# Creates: data/ → vectorstore/ → chromadb/
```

---

#### Step 2: Initialize ChromaDB Client

```python
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
```

**`PersistentClient` vs `Client`:**

```python
# PersistentClient: Saves to disk ✅
client = chromadb.PersistentClient(path="data/vectorstore/chromadb")
# Data persists after program closes
# Can reload later

# Client: In-memory only ❌
client = chromadb.Client()
# Data lost when program closes
# Have to rebuild every time
```

**Why persistent?**
```python
# Building vectorstore takes time:
# - 221 PDFs
# - 15,000+ chunks
# - Generate embeddings: ~10 minutes
# - Upload to ChromaDB: ~2 minutes

# With PersistentClient:
# Build once → Use forever ✅

# Without:
# Rebuild every time you run app ❌
```

---

#### Step 3: Load Embedding Model

```python
        # Load embedding model (multilingual - supports Amharic & English)
        print("📥 Loading embedding model...")
        self.embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("✅ Embedding model loaded")
```

**What is `SentenceTransformer`?**

A library for creating sentence embeddings using pre-trained models.

**Model: `all-MiniLM-L6-v2`**

```python
# Specs:
Name: all-MiniLM-L6-v2
Size: 80 MB
Speed: ~3,000 sentences/second
Dimensions: 384
Quality: Good balance

# Performance:
Embedding 1 sentence:   ~5 ms
Embedding 100 sentences: ~300 ms
Embedding 15,000 chunks: ~5 minutes
```

**Why this model?**

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| **all-MiniLM-L6-v2** ✅ | 80 MB | Fast | Good |
| all-mpnet-base-v2 | 420 MB | Slow | Better |
| multilingual-e5-large | 2 GB | Very slow | Best |

```python
# Chosen because:
✅ Small enough to run on any computer
✅ Fast enough for real-time
✅ Good enough for English + some Amharic
✅ No GPU required
```

**Loading process:**
```python
# First run: Downloads from internet
SentenceTransformer('all-MiniLM-L6-v2')
# → Downloads 80 MB
# → Saves to ~/.cache/torch/sentence_transformers/

# Subsequent runs: Loads from cache
# → Much faster (2-3 seconds)
```

---

#### Step 4: Set Collection Name

```python
        # Collection name
        self.collection_name = "ess_pdf_documents"
```

**What is a collection?**

```python
# ChromaDB organizes data into collections
# Like tables in SQL database

# This project structure:
ChromaDB Database
  └── Collection: "ess_pdf_documents"
       ├── Chunk 1: {embedding, text, metadata}
       ├── Chunk 2: {embedding, text, metadata}
       ├── Chunk 3: {embedding, text, metadata}
       └── ... (15,000+ chunks)
```

**Why name it `ess_pdf_documents`?**
- Descriptive (ESS PDF documents)
- Unique (won't conflict with other collections)
- Clear purpose

---

### Creating Collection

```python
def create_collection(self, reset: bool = False):
    """
    Create or get collection
    
    Args:
        reset: If True, delete existing collection and create new
    """
```

**`reset` parameter:**

```python
# reset=False (default):
# → Keep existing data
# → Add new documents to existing collection

# reset=True:
# → Delete everything
# → Start fresh
# → Use when rebuilding database
```

---

#### Delete Existing Collection (if reset)

```python
    if reset:
        try:
            self.client.delete_collection(self.collection_name)
            print(f"🗑️  Deleted existing collection: {self.collection_name}")
        except:
            pass
```

**Why `try/except`?**

```python
# If collection doesn't exist:
delete_collection("ess_pdf_documents")
# → Raises error!

# With try/except:
try:
    delete_collection("ess_pdf_documents")
except:
    pass  # Collection didn't exist, that's fine
```

**When to use `reset=True`:**
```python
# Scenarios:
1. Changed chunking parameters (size, overlap)
2. Updated PDF files
3. Fixed bug in processing
4. Testing different embedding models
5. Corrupted database

# Example:
vectorstore.create_collection(reset=True)
# → Deletes old data
# → Creates fresh collection
```

---

#### Create or Get Collection

```python
    self.collection = self.client.get_or_create_collection(
        name=self.collection_name,
        metadata={"description": "ESS PDF documents with AfDB policy papers"}
    )
    
    print(f"✅ Collection ready: {self.collection_name}")
```

**`get_or_create_collection`:**

```python
# If collection exists:
# → Returns existing collection
# → No data lost ✅

# If collection doesn't exist:
# → Creates new collection
# → Returns it

# Smart function - always safe to call!
```

**Collection metadata:**
```python
metadata = {
    "description": "ESS PDF documents with AfDB policy papers"
}

# Purpose:
# - Document what collection contains
# - Help future developers understand
# - Not used for search (just documentation)
```

---

### Adding Documents

This is where **embeddings are generated**!

```python
def add_documents(self, chunks: List[Dict], batch_size: int = 100):
    """
    Add document chunks to vector store
    
    Args:
        chunks: List of chunks with text and metadata
        batch_size: Number of chunks to process at once
    """
```

**Why batch processing?**

```python
# Without batching:
for chunk in chunks:  # 15,000 iterations
    embed(chunk)      # 15,000 separate operations
    add_to_db(chunk)  # Slow!

# With batching:
for batch in batches:  # 150 iterations (15,000 / 100)
    embed(batch)       # Process 100 at once
    add_to_db(batch)   # Much faster! ✅

# Batching efficiency:
1 chunk:     5 ms
100 chunks:  300 ms (not 500ms!)
# → 40% faster due to GPU/CPU parallelization
```

---

#### Validate Input

```python
    if not chunks:
        print("⚠️  No chunks to add")
        return
```

**Defensive programming:**
```python
# Prevent errors:
chunks = []
add_documents(chunks)
# Without check: Would crash later
# With check: Returns gracefully ✅
```

---

#### Process in Batches

```python
    print(f"\n🔄 Adding {len(chunks)} chunks to ChromaDB...")
    
    for i in tqdm(range(0, len(chunks), batch_size), desc="Vectorizing chunks"):
        batch = chunks[i:i + batch_size]
```

**Loop logic:**

```python
# Example: 250 chunks, batch_size=100

# Iteration 1:
i = 0
batch = chunks[0:100]    # First 100 chunks

# Iteration 2:
i = 100
batch = chunks[100:200]  # Next 100 chunks

# Iteration 3:
i = 200
batch = chunks[200:250]  # Last 50 chunks (smaller)
```

**`tqdm` progress bar:**
```python
tqdm(range(...), desc="Vectorizing chunks")

# Output in terminal:
Vectorizing chunks: 67%|███████▋    | 100/150 [02:15<01:07, 1.35s/it]

# Shows:
# - Progress percentage (67%)
# - Visual bar
# - Completed/Total (100/150)
# - Time elapsed (02:15)
# - Time remaining (01:07)
# - Speed (1.35 seconds per batch)
```

---

#### Prepare Data

```python
        # Prepare data
        ids = []
        texts = []
        metadatas = []
        
        for idx, chunk in enumerate(batch):
            chunk_id = f"chunk_{i + idx}"
            ids.append(chunk_id)
            texts.append(chunk['text'])
```

**Why separate lists?**

```python
# ChromaDB expects parallel lists:
ids =       ['chunk_0', 'chunk_1', 'chunk_2']
texts =     ['text 1',  'text 2',  'text 3']
metadatas = [meta1,     meta2,     meta3]

# Not:
chunks = [
    {'id': 'chunk_0', 'text': 'text 1', 'metadata': meta1},
    {'id': 'chunk_1', 'text': 'text 2', 'metadata': meta2}
]
```

**Chunk ID generation:**
```python
# Batch 0 (i=0):
chunk_0, chunk_1, chunk_2, ..., chunk_99

# Batch 1 (i=100):
chunk_100, chunk_101, chunk_102, ..., chunk_199

# Batch 2 (i=200):
chunk_200, chunk_201, chunk_202, ..., chunk_250

# Ensures unique IDs across all batches!
```

---

#### Prepare Metadata

```python
            # Prepare metadata (ChromaDB requires string/int/float values)
            metadata = {
                'source': chunk.get('source', 'Unknown'),
                'filename': chunk.get('filename', 'Unknown'),
                'category': chunk.get('category', 'General'),
                'report_type': chunk.get('report_type', 'General Report'),
                'pages': chunk.get('pages', 0),
                'chunk_id': chunk.get('chunk_id', 0),
                'has_tables': str(chunk.get('has_tables', False))
            }
```

**`.get(key, default)`:**
```python
chunk.get('source', 'Unknown')

# If key exists:
chunk = {'source': 'ESS'}
chunk.get('source', 'Unknown')  # → 'ESS'

# If key missing:
chunk = {}
chunk.get('source', 'Unknown')  # → 'Unknown' (default)

# Prevents KeyError!
```

**ChromaDB metadata restrictions:**

```python
# Allowed types:
✅ str:   'ESS', 'Price Index'
✅ int:   2022, 25
✅ float: 3.14

# Not allowed:
❌ bool:  True, False
❌ None:  None
❌ list:  [1, 2, 3]
❌ dict:  {'key': 'value'}

# Solution: Convert bool to string
has_tables = True  # ❌ Not allowed
has_tables = str(True)  # ✅ 'True'
```

---

#### Add Optional Metadata

```python
            # Add year if available
            if 'year' in chunk:
                metadata['year'] = chunk['year']
            
            # Add quarter if available
            if 'quarter' in chunk:
                metadata['quarter'] = chunk['quarter']
            
            metadatas.append(metadata)
```

**Why check before adding?**

```python
# Not all documents have year/quarter:
'CPI_2022_Q4.pdf'    → year: 2022, quarter: Q4 ✅
'General_Report.pdf' → No year, no quarter

# If we don't check:
metadata['year'] = chunk['year']  # KeyError! ❌

# With check:
if 'year' in chunk:
    metadata['year'] = chunk['year']  # Only add if exists ✅
```

---

#### Generate Embeddings

This is the **magic step**!

```python
        # Generate embeddings
        embeddings = self.embedder.encode(texts, show_progress_bar=False).tolist()
```

**What happens here:**

```python
# Input: List of texts
texts = [
    "The Consumer Price Index increased...",
    "Agricultural production rose by 3.2%...",
    ... # 100 texts in batch
]

# Process: Neural network transforms text → numbers
embeddings = embedder.encode(texts)

# Output: List of vectors
embeddings = [
    [0.023, -0.145, 0.891, ..., 0.234],  # 384 numbers for text 1
    [0.156, 0.023, -0.456, ..., 0.123],  # 384 numbers for text 2
    ... # 100 vectors
]

# Each text → 384-dimensional vector
# Similar meanings → similar vectors
```

**`.tolist()` conversion:**
```python
# embedder.encode returns numpy array:
embeddings = array([[0.023, -0.145, ...], [...]])  # NumPy

# ChromaDB expects Python list:
embeddings = embeddings.tolist()
# → [[0.023, -0.145, ...], [...]]  # Python list
```

**Performance:**
```python
# Batch of 100 texts:
encode(100 texts) = ~300ms

# Total for 15,000 chunks:
150 batches × 300ms = 45,000ms = 45 seconds
# Pretty fast! ✅
```

---

#### Add to ChromaDB

```python
        # Add to collection
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
```

**What gets stored:**

```python
# For each chunk:
{
    'id': 'chunk_0',
    'document': 'The Consumer Price Index...',  # Original text
    'metadata': {
        'source': 'ESS',
        'filename': 'CPI_2022.pdf',
        'category': 'Economic Statistics',
        'year': 2022
    },
    'embedding': [0.023, -0.145, ..., 0.234]  # 384 numbers
}

# Stored on disk in ChromaDB format
# Can query by text, metadata, or embedding
```

---

### Searching

This is where **semantic search** happens!

```python
def search(self, query: str, n_results: int = 5, filter_dict: Dict = None):
    """
    Search for relevant chunks
    
    Args:
        query: Search query
        n_results: Number of results to return
        filter_dict: Metadata filters (e.g., {'category': 'Price Index'})
        
    Returns:
        Search results
    """
```

---

#### Generate Query Embedding

```python
    # Generate query embedding
    query_embedding = self.embedder.encode([query])[0].tolist()
```

**Why embed the query?**

```python
# To search, we need:
# Query vector ≈ Document vectors

# Step 1: Convert query to vector
query = "What is inflation rate?"
query_embedding = [0.145, 0.234, ...]  # 384 numbers

# Step 2: Find similar vectors in database
# (Happens in next step)
```

**Index `[0]`:**
```python
embedder.encode([query])
# Returns: [[0.145, 0.234, ...]]  # List of lists

[0]
# Extracts: [0.145, 0.234, ...]   # Single list

# Needed because encode() expects list input
# But returns list of vectors
# We want single vector
```

---

#### Perform Search

```python
    # Search
    results = self.collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=filter_dict if filter_dict else None
    )
    
    return results
```

**How ChromaDB search works:**

```python
# 1. Compare query vector to all document vectors
query_vector = [0.145, 0.234, ...]

# 2. Calculate similarity (cosine similarity)
similarity(query, doc1) = 0.92  # Very similar!
similarity(query, doc2) = 0.45  # Less similar
similarity(query, doc3) = 0.88  # Very similar!

# 3. Rank by similarity
# 4. Return top N results

# Fast because ChromaDB uses HNSW index
# Can search 15,000 chunks in ~10ms!
```

**Metadata filtering:**

```python
# Without filter:
search("What is CPI?")
# → Searches ALL 15,000 chunks

# With filter:
search("What is CPI?", filter_dict={'year': 2022})
# → Only searches chunks from 2022
# → Faster + more relevant

# Example filters:
{'year': 2022}
{'category': 'Price Index'}
{'source': 'ESS', 'year': 2023}
{'has_tables': 'True'}
```

**Result structure:**
```python
results = {
    'ids': [['chunk_45', 'chunk_102', 'chunk_234', ...]],
    'documents': [[
        'The Consumer Price Index increased...',
        'Inflation rate was 15.2%...',
        'Price levels rose significantly...',
        ...
    ]],
    'metadatas': [[
        {'source': 'ESS', 'filename': 'CPI_2022.pdf', 'year': 2022},
        {'source': 'ESS', 'filename': 'CPI_2023.pdf', 'year': 2023},
        ...
    ]],
    'distances': [[0.35, 0.42, 0.48, ...]]  # Lower = more similar
}
```

---

## 🔍 Search Quality: Semantic vs Keyword

### Example 1: Synonyms

```python
# Query: "price increases"

# Keyword search: ❌ Misses these:
# - "inflation rate"
# - "CPI growth"
# - "cost escalation"

# Semantic search: ✅ Finds all of these!
# Because embeddings understand meaning
```

### Example 2: Context

```python
# Query: "What causes inflation?"

# Keyword search: ❌ 
# - Looks for exact word "causes"
# - Misses "factors leading to", "drivers of"

# Semantic search: ✅
# - Understands question intent
# - Finds explanatory text about inflation factors
```

### Example 3: Multilingual

```python
# Query: "የዋጋ ግሽበት" (inflation in Amharic)

# Keyword search: ❌ Can't match English docs

# Semantic search: ✅
# - all-MiniLM-L6-v2 has some multilingual capability
# - Can find related English documents
# - Not perfect but helpful!
```

---

## 📊 Statistics

```python
def get_stats(self) -> Dict:
    """Get collection statistics"""
    count = self.collection.count()
    
    return {
        'total_chunks': count,
        'collection_name': self.collection_name,
        'persist_directory': self.persist_directory
    }
```

**Usage:**
```python
stats = vectorstore.get_stats()
print(stats)

# Output:
{
    'total_chunks': 15234,
    'collection_name': 'ess_pdf_documents',
    'persist_directory': 'data/vectorstore/chromadb'
}
```

---

## 🎓 Key Takeaways

### 1. **Embeddings are the foundation**
```python
# Text → Numbers → Semantic search possible
"inflation" → [0.145, 0.234, ...] → Find similar concepts
```

### 2. **Batching improves performance**
```python
# Process 100 chunks at once
# 40% faster than one-by-one
```

### 3. **Metadata enables filtering**
```python
# Narrow search by year, category, source
# More relevant + faster results
```

### 4. **Persistent storage saves time**
```python
# Build once, use forever
# No need to rebuild every run
```

### 5. **Vector search > Keyword search**
```python
# Understands meaning, not just words
# Finds synonyms, related concepts
# Better user experience
```

---

## 🔄 Complete Flow

```
1. Input: Text chunks from PDFs
    ↓
2. Generate embeddings (384-dim vectors)
    ↓
3. Store in ChromaDB with metadata
    ↓
4. User asks question
    ↓
5. Convert question to embedding
    ↓
6. Find similar embeddings (cosine similarity)
    ↓
7. Apply metadata filters
    ↓
8. Return top N most relevant chunks
    ↓
9. Send to LLM for answer generation
```

---

**Continue to next document: Excel & SQL processing...**

This comprehensive guide covers vector databases in depth. Ready for Engine B (SQL) next!

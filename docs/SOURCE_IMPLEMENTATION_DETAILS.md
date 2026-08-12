# Source Attribution Implementation - Technical Details

## 🎯 Overview

This document explains the complete implementation of source attribution and PDF download functionality in the ESS RAG Chatbot.

## 📊 Data Flow

```
User Query
    ↓
LangChainDualEngineRAG.query()
    ↓
Query Routing (PDF, SQL, or Both)
    ↓
[For PDF queries]
query_engine_a()
    ↓
ChromaDB Retrieval (Top-5 semantic similarity)
    ↓
Documents with Metadata
    ↓
Format Response with Sources
    ↓
Streamlit Display
    ↓
Group by PDF & Show Download Buttons
```

## 🔧 Implementation Components

### 1. PDF Processing (Data Ingestion)

**File:** `src/engine_a_pdf_rag/pdf_processor.py`

**Key Method:** `process_folder(folder_path, source_name)`

```python
def process_folder(self, folder_path: str, source_name: str) -> List[Dict]:
    """
    Process all PDFs in a folder
    
    Args:
        folder_path: Path to folder containing PDFs
        source_name: Source identifier (e.g., 'ESS', 'AfDB')
    """
    for pdf_path in pdf_files:
        # Extract text and basic metadata
        text, file_metadata = self.extract_text_from_pdf(str(pdf_path))
        
        # Extract additional metadata from filename
        filename_metadata = self.extract_metadata_from_filename(
            file_metadata['filename']
        )
        
        # Combine all metadata
        combined_metadata = {
            'source': source_name,  # 'ESS' or 'AfDB'
            'file_path': str(pdf_path),
            **file_metadata,        # filename, pages, has_tables
            **filename_metadata     # year, quarter, report_type, category
        }
        
        # Create chunks with metadata
        chunks = self.chunk_text(text, combined_metadata)
        all_chunks.extend(chunks)
```

**Metadata Structure:**
```python
{
    'source': 'AfDB',  # or 'ESS'
    'filename': 'ETHIOPIA_CSP_BPPS_EN.pdf',
    'file_path': 'data/raw/afdb_reports/ETHIOPIA_CSP_BPPS_EN.pdf',
    'pages': 156,
    'has_tables': True,
    'report_type': 'Policy Document',
    'category': 'Strategic Planning',
    'chunk_id': 0,
    # Optional fields from filename:
    'year': 2023,
    'quarter': 'Q4'
}
```

### 2. Vector Storage (ChromaDB)

**File:** `src/dual_engine_router/langchain_rag.py`

**Initialization:**
```python
self.vectorstore = Chroma(
    persist_directory="data/vectorstore/chromadb",
    embedding_function=self.embeddings,
    collection_name="ess_documents"
)

self.retriever = self.vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={'k': 5}  # Top-5 results
)
```

**Storage:**
- 36,524 total chunks
- Each chunk stored with:
  - Text content (page_content)
  - 384-dimensional embedding vector
  - Full metadata dictionary

### 3. Query & Retrieval

**File:** `src/dual_engine_router/langchain_rag.py`

**Query Method:**
```python
def query_engine_a(self, query: str) -> Dict:
    """Query Engine A (PDF RAG)"""
    
    # Get relevant documents via semantic search
    docs = self.retriever.invoke(query)  # Returns top-5 docs
    
    # Format context (with truncation for token limits)
    context_parts = []
    max_context_length = 8000
    for doc in docs:
        content = doc.page_content[:1500]  # Limit per doc
        context_parts.append(content)
    
    context = "\n\n".join(context_parts)
    
    # Get answer from LLM
    answer = self.llm.invoke(prompt_text)
    
    # Format sources with metadata
    sources = []
    for doc in docs:
        sources.append({
            'content': doc.page_content[:500],  # Preview
            'metadata': doc.metadata  # Full metadata dict
        })
    
    return {
        'engine': 'PDF RAG (LangChain)',
        'answer': answer_text,
        'sources': sources,  # ← Passed to Streamlit
        'source_count': len(sources)
    }
```

**Return Structure:**
```python
{
    'question': 'What is CRGE?',
    'query_type': 'pdf',
    'engines_used': ['PDF RAG'],
    'sources': [  # ← Array of source objects
        {
            'content': '...',
            'metadata': {
                'source': 'AfDB',
                'filename': 'ETHIOPIA_CSP_BPPS_EN.pdf',
                ...
            }
        },
        ...
    ],
    'num_sources': 5,
    'answer': '...',
    'total_time': 1.23
}
```

### 4. Streamlit Display

**File:** `streamlit_app.py` (lines 1333-1385)

**Step 1: Extract Sources from Result**
```python
# When query completes (line ~1491)
metadata = {
    "query_type": result['query_type'],
    "engines": result['engines_used'],
    "time": result['total_time'],
    "sources_data": result['sources']  # ← Store sources
}
```

**Step 2: Group Sources by PDF**
```python
# When Sources button clicked (line ~1334)
sources_data = message['metadata'].get('sources_data', [])

# Group by filename
sources_by_pdf = {}
for source in sources_data[:5]:
    # Extract metadata
    if isinstance(source, dict):
        metadata = source.get('metadata', {})
    else:
        metadata = source.metadata if hasattr(source, 'metadata') else {}
    
    source_type = metadata.get('source', 'Unknown')  # 'AfDB' or 'ESS'
    filename = metadata.get('filename', 'Unknown')
    
    # Group by filename
    if filename not in sources_by_pdf:
        sources_by_pdf[filename] = {
            'source_type': source_type,
            'chunks': []
        }
    sources_by_pdf[filename]['chunks'].append(source)
```

**Step 3: Display with Download Buttons**
```python
for i, (filename, data) in enumerate(sources_by_pdf.items(), 1):
    source_type = data['source_type']  # 'AfDB' or 'ESS'
    chunk_count = len(data['chunks'])
    
    # Determine PDF path
    if source_type == 'AfDB':
        pdf_path = os.path.join("data", "raw", "afdb_reports", filename)
    else:
        pdf_path = os.path.join("data", "raw", "ess_reports", "pdfs", filename)
    
    # Display in expander
    with st.expander(f"📄 Source {i}: {source_type} - {filename[:80]} ({chunk_count} chunk(s))"):
        # Content preview
        first_chunk = data['chunks'][0]
        content = get_content(first_chunk)[:400]
        st.text(content + "...")
        
        # Download button
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                st.download_button(
                    label=f"📥 Download {source_type} PDF",
                    data=f,
                    file_name=filename,
                    mime="application/pdf",
                    key=f"download_pdf_{sources_key}_{i}",
                    use_container_width=True
                )
        else:
            st.caption(f"⚠️ PDF file not found at: {pdf_path}")
```

## 🎨 UI Components

### Source Display Structure
```
📚 Sources (Toggle Button)
  ↓ (When expanded)
  
  📄 Source 1: AfDB - ETHIOPIA_CSP_BPPS_EN.pdf (2 chunks)
    ▼ (Expandable)
      [Content Preview - 400 chars]
      📥 Download AfDB PDF (Button)
  
  📄 Source 2: ESS - national-area-production.pdf (1 chunk)
    ▼ (Expandable)
      [Content Preview - 400 chars]
      📥 Download ESS PDF (Button)
```

### Key Features
1. **Grouping** - Sources grouped by PDF filename (not individual chunks)
2. **Type Badge** - "AfDB" or "ESS" shown prominently
3. **Chunk Count** - Shows how many chunks came from each PDF
4. **Preview** - First 400 characters of content
5. **Download** - Direct PDF download button
6. **Error Handling** - Shows warning if PDF file not found

## 🔍 Path Resolution Logic

```python
# AfDB PDFs
if source_type == 'AfDB':
    pdf_path = os.path.join("data", "raw", "afdb_reports", filename)
    # Example: data\raw\afdb_reports\ETHIOPIA_CSP_BPPS_EN.pdf

# ESS PDFs
else:
    pdf_path = os.path.join("data", "raw", "ess_reports", "pdfs", filename)
    # Example: data\raw\ess_reports\pdfs\1.inflation-report-june-efy-2018-final.pdf
```

**Why `os.path.join()`?**
- Cross-platform compatibility (Windows uses `\`, Unix uses `/`)
- Automatically handles path separators
- Prevents path construction errors

## 🧪 Testing

### Unit Test (test_sources.py)

```python
def test_source_attribution():
    # Initialize RAG
    rag = LangChainDualEngineRAG()
    
    # Query
    result = rag.query("Tell me about Ethiopia's green growth strategy")
    
    # Check sources
    sources = result.get('sources', [])
    
    for source in sources:
        metadata = source.get('metadata', {})
        source_type = metadata.get('source')
        filename = metadata.get('filename')
        
        print(f"Type: {source_type}, File: {filename}")
    
    # Expected output:
    # Type: AfDB, File: ETHIOPIA_CSP_BPPS_EN.pdf
    # Type: ESS, File: national-area-production.pdf
    # ...
```

### Integration Test (Streamlit)

1. Start app: `streamlit run streamlit_app.py`
2. Ask: "Tell me about Ethiopia's green growth strategy"
3. Click "📚 Sources" button
4. Verify:
   - ✅ Shows "AfDB" source type
   - ✅ Shows "ETHIOPIA_CSP_BPPS_EN.pdf"
   - ✅ Download button appears
   - ✅ Download works

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| Total Chunks | 36,524 |
| AfDB Chunks | ~165 |
| ESS Chunks | ~36,359 |
| Retrieval Count | 5 (top-5) |
| Retrieval Time | ~0.1-0.2s |
| LLM Response Time | ~0.5-1.5s |
| Total Query Time | ~0.7-2.0s |

## 🔒 Error Handling

### Missing Metadata
```python
metadata = source.get('metadata', {})  # Default to empty dict
source_type = metadata.get('source', 'Unknown')  # Default to 'Unknown'
filename = metadata.get('filename', 'Unknown')  # Default to 'Unknown'
```

### Missing PDF File
```python
if os.path.exists(pdf_path):
    # Show download button
else:
    st.caption(f"⚠️ PDF file not found at: {pdf_path}")
```

### Type Checking
```python
if isinstance(source, dict):
    metadata = source.get('metadata', {})
else:
    metadata = source.metadata if hasattr(source, 'metadata') else {}
```

## 🚀 Future Enhancements

Possible improvements:
1. Add page number highlighting for specific chunks
2. Show relevance score for each source
3. Add "View in PDF" button that opens PDF at specific page
4. Cache PDF files in memory for faster downloads
5. Add source filtering (show only AfDB or only ESS)
6. Add source timeline visualization
7. Show metadata badges (year, category, report type)

## 📝 Code Locations

| Feature | File | Lines |
|---------|------|-------|
| Metadata Creation | `src/engine_a_pdf_rag/pdf_processor.py` | 136-225 |
| Vector Storage | `src/dual_engine_router/langchain_rag.py` | 98-106 |
| Query & Retrieval | `src/dual_engine_router/langchain_rag.py` | 227-280 |
| Source Formatting | `src/dual_engine_router/langchain_rag.py` | 264-273 |
| Streamlit Display | `streamlit_app.py` | 1333-1385 |
| Source Data Storage | `streamlit_app.py` | 1491, 1612 |

---

**Version:** 1.0  
**Last Updated:** 2026-08-10  
**Status:** ✅ Production Ready

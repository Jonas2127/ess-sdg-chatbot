# 📄 PDF Processing & Text Extraction

**File:** `src/engine_a_pdf_rag/pdf_processor.py`  
**Purpose:** Extract text from PDFs and prepare for vector database

---

## 🎯 What You'll Learn

- How to extract text from PDF files
- Document chunking strategies and why they matter
- Metadata extraction and enrichment
- Table handling in PDFs
- Production-ready PDF processing

---

## 📚 Overview

### What This Module Does:

```
221 ESS PDFs + 1 AfDB PDF
    ↓
[Extract Text] - Get text from each page
    ↓
[Extract Tables] - Convert tables to text
    ↓
[Extract Metadata] - Year, category, type
    ↓
[Chunk Text] - Split into 700-word pieces
    ↓
15,000+ text chunks ready for embedding
```

### Why PDF Processing Matters:

**Bad Processing:**
```python
# Just dump all text
text = pdf.extract_all_text()
# Problems:
# - Too large for LLM context
# - Loses structure
# - Can't cite specific pages
# - Poor retrieval accuracy
```

**Good Processing (This System):**
```python
# Smart chunking with metadata
chunks = [
    {'text': chunk1, 'page': 5, 'category': 'CPI', 'year': 2022},
    {'text': chunk2, 'page': 6, 'category': 'CPI', 'year': 2022},
    ...
]
# Benefits:
# ✅ Fits in LLM context
# ✅ Preserves structure
# ✅ Can cite pages
# ✅ Better retrieval
```

---

## 💻 Code Analysis: Line by Line

### Class Initialization

```python
class PDFProcessor:
    """Extract and process text from PDF documents"""
    
    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
```

**Parameters explained:**

#### **`chunk_size=700`** - Words per chunk

**Why 700 words?**

```python
# Average calculation:
1 word ≈ 1.3 tokens (English)
700 words ≈ 910 tokens

# LLM context limits:
GPT-3.5: 4,096 tokens
GPT-4: 8,192 tokens
Llama-3.2: 128,000 tokens

# With 700-word chunks:
- Can fit 4-8 chunks in prompt
- Leaves room for question + instructions
- Not too small (loses context)
- Not too large (irrelevant info)
```

**Chunk size trade-offs:**

| Size | Pros | Cons |
|------|------|------|
| **Small (200)** | Precise retrieval | Loses context |
| **Medium (700)** ✅ | Good balance | Balanced |
| **Large (2000)** | Full context | Too much noise |

#### **`chunk_overlap=100`** - Overlap between chunks

**Why overlap?**

**Without overlap:**
```python
Chunk 1: "The Consumer Price Index measures inflation by..."
Chunk 2: "...tracking prices. The CPI was 125.3 in December."

# Problem: Sentence split across chunks!
# Loses meaning at boundaries
```

**With overlap (100 words):**
```python
Chunk 1: "...measures inflation by tracking prices. The CPI was..."
Chunk 2: "...tracking prices. The CPI was 125.3 in December..."

# ✅ Context preserved at boundaries
# ✅ Complete sentences in each chunk
# ✅ Better retrieval accuracy
```

**Overlap visualization:**
```
Chunk 1: [====================] (700 words)
Chunk 2:          [====================] (700 words)
         ^^^^^^^^^^
         100-word overlap
```

---

### Text Extraction from PDF

```python
def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, Dict]:
    """
    Extract text from a single PDF file
    
    Returns:
        text: Extracted text
        metadata: File metadata (pages, size, etc.)
    """
```

**Return type explained:**
```python
Tuple[str, Dict]
# ↓
(text: str, metadata: Dict)
# ↓
("Full document text...", {'filename': 'CPI.pdf', 'pages': 25})
```

**Why return both?**
- Text: For processing and embedding
- Metadata: For source attribution and filtering

---

#### Step 1: Open PDF

```python
    try:
        with pdfplumber.open(pdf_path) as pdf:
```

**What is `pdfplumber`?**

A Python library for extracting text, tables, and metadata from PDFs.

**Why `pdfplumber`?**
- Handles tables better than PyPDF2
- Preserves layout
- Works with both digital and scanned PDFs
- Extracts structured data

**Context manager (`with`):**
```python
with pdfplumber.open(pdf_path) as pdf:
    # pdf is automatically closed when done
    # Even if error occurs
    # Prevents memory leaks
```

**Alternatives and why not used:**
```python
# PyPDF2: Basic, misses tables
# PDFMiner: Complex, slower
# pdfplumber: Best balance ✅
```

---

#### Step 2: Extract Text from Each Page

```python
            full_text = ""
            tables = []
            
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract text
                text = page.extract_text()
                if text:
                    full_text += f"\n--- Page {page_num} ---\n{text}\n"
```

**Loop explained:**
```python
enumerate(pdf.pages, 1)
# ↓
# page_num starts at 1 (not 0)
# page is the actual page object

# Example iterations:
# page_num=1, page=Page1
# page_num=2, page=Page2
# page_num=3, page=Page3
```

**Why add page numbers?**
```python
full_text = """
--- Page 5 ---
The Consumer Price Index for December 2022...

--- Page 6 ---
The inflation rate increased to 15.2%...
"""

# Benefits:
# ✅ Can cite specific pages
# ✅ Track where information came from
# ✅ Help users find original source
```

**Why check `if text:`?**
```python
# Some pages might be:
# - Blank pages
# - Image-only pages
# - Corrupted pages

if text:  # Only add non-empty pages
    full_text += ...
```

---

#### Step 3: Extract Tables

```python
                # Extract tables
                page_tables = page.extract_tables()
                if page_tables:
                    for table_idx, table in enumerate(page_tables):
                        tables.append({
                            'page': page_num,
                            'table_index': table_idx,
                            'data': table
                        })
```

**What are tables in PDFs?**

Tables are structured data like:
```
| Year | CPI  | Inflation |
|------|------|-----------|
| 2020 | 115  | 12.3%     |
| 2021 | 120  | 13.5%     |
| 2022 | 125  | 15.2%     |
```

**`extract_tables()` returns:**
```python
[
    # Table 1
    [
        ['Year', 'CPI', 'Inflation'],    # Header row
        ['2020', '115', '12.3%'],        # Data row
        ['2021', '120', '13.5%'],        # Data row
        ['2022', '125', '15.2%']         # Data row
    ],
    # Table 2 (if exists)
    [...]
]
```

**Why store table metadata?**
```python
{
    'page': 5,           # Which page
    'table_index': 0,    # First table on page
    'data': [[...]]      # Actual table data
}

# Benefits:
# - Can reference "Table 1 on Page 5"
# - Multiple tables per page tracked
# - Preserves source information
```

---

#### Step 4: Format Tables as Text

```python
            # Convert tables to text format
            table_text = self._format_tables(tables)
            if table_text:
                full_text += "\n\n=== TABLES ===\n" + table_text
```

**Why convert to text?**

```python
# LLMs work with TEXT, not structured data
# Must convert table → readable text

# Table:
[['Year', 'CPI'], ['2022', '125']]

# ↓ Convert to text ↓

"--- Table on Page 5 ---
Year | CPI
2022 | 125"
```

**Why separate section?**
```python
full_text = """
[Regular text content]

=== TABLES ===
[All tables here]
"""

# Benefits:
# - Clear separation
# - LLM knows it's structured data
# - Can extract tables separately if needed
```

---

#### Step 5: Create Metadata

```python
            metadata = {
                'filename': os.path.basename(pdf_path),
                'pages': len(pdf.pages),
                'has_tables': len(tables) > 0,
                'table_count': len(tables)
            }
            
            return full_text, metadata
```

**`os.path.basename()`:**
```python
pdf_path = "/data/pdfs/CPI_DEC_2022.pdf"
basename = os.path.basename(pdf_path)
# Result: "CPI_DEC_2022.pdf"

# Removes directory path, keeps filename only
```

**Metadata structure:**
```python
{
    'filename': 'CPI_DEC_2022.pdf',
    'pages': 25,
    'has_tables': True,
    'table_count': 5
}

# Used for:
# - Source attribution
# - Filtering (e.g., "only docs with tables")
# - Quality assessment
```

---

### Table Formatting

```python
def _format_tables(self, tables: List[Dict]) -> str:
    """Convert extracted tables to readable text format"""
    formatted = []
    
    for table_info in tables:
        table_data = table_info['data']
        page = table_info['page']
        
        formatted.append(f"\n--- Table on Page {page} ---")
        
        # Format table as text
        for row in table_data:
            if row:
                row_text = " | ".join([str(cell) if cell else "" for cell in row])
                formatted.append(row_text)
    
    return "\n".join(formatted)
```

**How it works:**

**Input:**
```python
tables = [{
    'page': 5,
    'data': [
        ['Year', 'CPI', 'Rate'],
        ['2022', '125', '15.2%'],
        ['2021', '120', '13.5%']
    ]
}]
```

**Processing:**
```python
# For each row:
row = ['2022', '125', '15.2%']

# Join with " | ":
row_text = " | ".join(row)
# Result: "2022 | 125 | 15.2%"
```

**Output:**
```
--- Table on Page 5 ---
Year | CPI | Rate
2022 | 125 | 15.2%
2021 | 120 | 13.5%
```

**Why " | " separator?**
- Clear column boundaries
- Human-readable
- LLM can understand structure
- Easy to parse if needed

**Handle empty cells:**
```python
str(cell) if cell else ""
# If cell is None or empty → ""
# If cell has value → convert to string
```

---

### Text Chunking

This is **critical** for RAG performance!

```python
def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
    """
    Split text into chunks with overlap
    
    Args:
        text: Full document text
        metadata: Document metadata
        
    Returns:
        List of chunks with metadata
    """
```

**Why chunk?**

```python
# Problem: 25-page PDF
full_text = "..." # 10,000 words = 13,000 tokens

# LLM context limit: 4,096 tokens
# Can't fit entire document!

# Solution: Split into chunks
chunk1 = words[0:700]      # 910 tokens ✅
chunk2 = words[600:1300]   # 910 tokens ✅
chunk3 = words[1200:1900]  # 910 tokens ✅
# Each chunk fits in context!
```

---

#### Step 1: Split into Words

```python
    # Split into words
    words = text.split()
    chunks = []
    
    start_idx = 0
    chunk_id = 0
```

**Why split by words?**

```python
# Could split by characters:
text[:700]  # ❌ Cuts mid-word: "...inflat"

# Could split by sentences:
sentences[:10]  # ❌ Uneven sizes: 50-500 words

# Split by words: ✅
words = text.split()  # ["The", "Consumer", "Price", ...]
# Even chunks, respect word boundaries
```

**Initialize tracking:**
```python
start_idx = 0   # Start at first word
chunk_id = 0    # Number chunks for tracking
```

---

#### Step 2: Create Chunks with Overlap

```python
    while start_idx < len(words):
        # Get chunk
        end_idx = min(start_idx + self.chunk_size, len(words))
        chunk_words = words[start_idx:end_idx]
        chunk_text = " ".join(chunk_words)
```

**Loop logic:**

**Iteration 1:**
```python
start_idx = 0
end_idx = min(0 + 700, 10000) = 700
chunk_words = words[0:700]     # First 700 words
chunk_text = "The Consumer Price..." # Join words
```

**Iteration 2:**
```python
start_idx = 600  # 700 - 100 (overlap)
end_idx = min(600 + 700, 10000) = 1300
chunk_words = words[600:1300]  # Next 700 words (100 overlap)
```

**Why `min()`?**
```python
# Last chunk might be shorter
words = [...] # 9,850 words total

start_idx = 9,800
end_idx = min(9,800 + 700, 9,850) = 9,850  # Not 10,500!
# Prevents index out of range
```

---

#### Step 3: Create Chunk with Metadata

```python
        # Create chunk with metadata
        chunk = {
            'text': chunk_text,
            'chunk_id': chunk_id,
            'chunk_size': len(chunk_words),
            'start_word': start_idx,
            'end_word': end_idx,
            **metadata  # Include all document metadata
        }
        
        chunks.append(chunk)
```

**Complete chunk structure:**
```python
{
    # Chunk-specific
    'text': "The Consumer Price Index...",
    'chunk_id': 0,
    'chunk_size': 700,
    'start_word': 0,
    'end_word': 700,
    
    # Document metadata (from **metadata)
    'filename': 'CPI_DEC_2022.pdf',
    'pages': 25,
    'source': 'ESS',
    'category': 'Economic Statistics',
    'year': 2022
}
```

**`**metadata` unpacking:**
```python
metadata = {'filename': 'CPI.pdf', 'pages': 25}

chunk = {
    'text': '...',
    **metadata  # Unpacks dict into chunk
}

# Result:
chunk = {
    'text': '...',
    'filename': 'CPI.pdf',  # ← Added
    'pages': 25             # ← Added
}
```

---

#### Step 4: Move to Next Chunk

```python
        # Move to next chunk with overlap
        start_idx += self.chunk_size - self.chunk_overlap
        chunk_id += 1
```

**Overlap calculation:**
```python
# Current chunk: words[0:700]
# Next start: 0 + (700 - 100) = 600
# Next chunk: words[600:1300]
#             ^^^ 100-word overlap with previous

# Visual:
Chunk 0: [0.........................700]
Chunk 1:      [600.....................1300]
              ^^^
              100-word overlap
```

**Why this formula?**
```python
start_idx += (chunk_size - overlap)
#            (700 - 100) = 600

# Means: Move forward 600 words
# But chunk is 700 words
# So 100 words overlap with previous
```

---

### Metadata Extraction from Filename

This is **smart** - extracting meaning from filenames!

```python
def extract_metadata_from_filename(self, filename: str) -> Dict:
    """
    Extract metadata from PDF filename
    
    Examples:
        ESS_CPI_Bulletin_2023_Q4.pdf -> year: 2023, quarter: Q4, type: CPI
        Agricultural_Survey_2022.pdf -> year: 2022, type: Survey
    """
```

**Why filename parsing?**

```python
# Filenames contain valuable information!
"CPI_DEC_2022.pdf"
# → year: 2022, category: CPI

# Better retrieval:
Query: "What was CPI in 2022?"
# Can filter: year=2022, category=CPI
# More accurate results!
```

---

#### Extract Year

```python
    # Extract year (4 digits)
    year_match = re.search(r'\b(20\d{2})\b', filename)
    if year_match:
        metadata['year'] = int(year_match.group(1))
```

**Regex explained:**
```python
r'\b(20\d{2})\b'

\b        # Word boundary
(...)     # Capture group
20        # Literal "20"
\d{2}     # Two digits
\b        # Word boundary

# Matches: 2020, 2021, 2022, 2023, ..., 2099
# Won't match: 1999, 3000, 20 (too short)
```

**Examples:**
```python
"CPI_2022.pdf"        → year_match = "2022"
"Report_2023_Q4.pdf"  → year_match = "2023"
"Old_1999.pdf"        → year_match = None (19xx not matched)
```

---

#### Extract Quarter

```python
    # Extract quarter (Q1, Q2, Q3, Q4)
    quarter_match = re.search(r'\b(Q[1-4])\b', filename, re.IGNORECASE)
    if quarter_match:
        metadata['quarter'] = quarter_match.group(1).upper()
```

**Regex explained:**
```python
r'\b(Q[1-4])\b'

\b        # Word boundary
(Q[1-4])  # Q followed by 1, 2, 3, or 4
\b        # Word boundary

re.IGNORECASE  # Match Q1, q1, Q1

# Matches: Q1, Q2, Q3, Q4, q1, q2, q3, q4
# Won't match: Q5, Q0, QQ, Q
```

**`.upper()` normalization:**
```python
"q1" → "Q1"
"Q1" → "Q1"
# Consistent format
```

---

#### Detect Report Type

```python
    # Detect report type from filename
    filename_lower = filename.lower()
    if 'cpi' in filename_lower or 'price' in filename_lower:
        metadata['report_type'] = 'Price Index'
        metadata['category'] = 'Economic Statistics'
```

**Keyword matching:**
```python
filename = "CPI_Bulletin_2022.pdf"
filename_lower = "cpi_bulletin_2022.pdf"

if 'cpi' in filename_lower:  # True!
    report_type = 'Price Index'
```

**Multiple categories:**
```python
# Economic Statistics
'cpi', 'price' → Price Index

# Agriculture
'agricult', 'farm' → Agricultural Survey

# Demographics
'population', 'census' → Population & Census

# Social
'household', 'income' → Household Survey

# Business
'business', 'enterprise' → Business Statistics

# Policy
'afdb', 'strategy' → Policy Document
```

**Why categorize?**
- Better routing (know what database has)
- Filtering (only show CPI docs)
- Organization (group similar docs)
- User understanding (show category)

---

## 🔄 Complete Processing Flow

```
1. Input: "CPI_DEC_2022.pdf"
    ↓
2. Open with pdfplumber
    ↓
3. For each page:
   - Extract text
   - Extract tables
    ↓
4. Format tables as text
    ↓
5. Create metadata:
   - Filename, pages, tables
   - Year (2022)
   - Category (Economic)
   - Type (Price Index)
    ↓
6. Chunk text (700 words, 100 overlap)
    ↓
7. Output: [
     {'text': chunk1, 'year': 2022, 'category': 'Economic', ...},
     {'text': chunk2, 'year': 2022, 'category': 'Economic', ...},
     ...
   ]
    ↓
8. Ready for embedding & vector database!
```

---

**Continue to next document...**

This comprehensive guide covers PDF processing in depth. Ready for Vector Database next!

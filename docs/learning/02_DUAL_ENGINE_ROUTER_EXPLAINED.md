# 🧠 Dual-Engine Router - Part 2: Query Validation & Routing

**Continuation of:** `02_DUAL_ENGINE_ROUTER_EXPLAINED.md`

---

## Part 4: Query Validation (`_is_valid_query`)

This is **critical** - prevents wasting time on bad queries:

```python
def _is_valid_query(self, query: str) -> tuple[bool, str]:
    """
    Validate if query is meaningful and not gibberish.
    
    Returns:
        (is_valid, message): Tuple of validation status and message
    """
```

**Function signature explained:**
- `self` - Instance method (access to class attributes)
- `query: str` - Input parameter with type hint (must be string)
- `-> tuple[bool, str]` - Returns tuple: (True/False, reason)

**Why tuple return?**
- Need TWO pieces of information
- Boolean: is it valid?
- String: what type (greeting, gibberish, valid, etc.)

```python
    query_lower = query.strip().lower()
```

**What this does:**
- `.strip()` - Remove leading/trailing spaces
- `.lower()` - Convert to lowercase
- **Why?** "Hello", "HELLO", " hello " should all be treated same

**Before:** `"  How Are You?  "`  
**After:** `"how are you?"`

```python
    # Remove punctuation for greeting detection
    import string
    query_clean = query_lower.translate(str.maketrans('', '', string.punctuation))
```

**Advanced Python here!**

- `string.punctuation` - All punctuation: `!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~`
- `str.maketrans('', '', string.punctuation)` - Create translation table
- `.translate()` - Apply translation (remove punctuation)

**Example:**
- **Input:** `"how are you?"`
- **Output:** `"how are you"`

**Why remove punctuation?**
- "how are you?" should match "how are you"
- Makes detection more robust
- Users add punctuation randomly

```python
    # Handle greetings
    greetings = [
        'hi', 'hello', 'hey', 'greetings', 'good morning', 
        'good afternoon', 'good evening', 'howdy',
        'how are you', 'how r u', 'how are u',
        'how do you do', 'whats up', "what's up", 'whatsup'
    ]
```

**Comprehensive greeting list:**
- Common greetings: hi, hello, hey
- Time-based: good morning, good afternoon
- Informal: how r u, whats up
- **Why so many?** Users phrase greetings many ways!

```python
    if any(greet == query_clean or query_clean.startswith(greet + ' ') or 
           greet == query_lower or query_lower.startswith(greet + ' ') for greet in greetings):
        return False, "greeting"
```

**Complex condition broken down:**

```python
any(                           # True if ANY condition matches
    greet == query_clean       # Exact match (no punctuation)
    or                         # OR
    query_clean.startswith(greet + ' ')  # Starts with greeting + space
    or                         # OR
    greet == query_lower       # Exact match (with punctuation)
    or                         # OR  
    query_lower.startswith(greet + ' ')  # Starts with greeting + space
    for greet in greetings     # Check each greeting in list
)
```

**Examples that match:**
- `"hi"` - exact match
- `"hello there"` - starts with hello
- `"how are you?"` - exact after punctuation removal
- `"hey buddy"` - starts with hey

**If matched:** Return `(False, "greeting")`
- `False` - Not a valid data query
- `"greeting"` - Reason: it's a greeting

```python
    # Handle meta questions about the chatbot itself
    meta_questions = [
        'who are you', 'what are you', 'who r u', 'what r u',
        'what is your name', 'tell me about yourself',
        'what can you do', 'what do you do', 'how do you work',
        'who made you', 'who created you', 'who built you',
        'what is this', 'what is this chatbot', 'explain yourself'
    ]
```

**Meta questions = Questions about the bot itself**

Not about data, about the chatbot:
- Who are you?
- What can you do?
- How do you work?

**Why separate handling?**
- Don't need to search database
- Can answer immediately
- Saves time and resources

```python
    if any(meta in query_clean or meta in query_lower for meta in meta_questions):
        return False, "meta_question"
```

**Simpler check:**
- Just check if meta question appears anywhere
- Don't need exact match
- "Hey, who are you?" contains "who are you"

```python
    # Improved gibberish detection - LESS STRICT
    if len(query_lower) >= 4:
        # Remove spaces and special chars for analysis
        letters_only = ''.join(c for c in query_lower if c.isalpha())
```

**Gibberish detection algorithm:**

**Step 1:** Get only letters
- `"hello world!"` → `"helloworld"`
- `"hhj xzq"` → `"hhjxzq"`

```python
        if len(letters_only) >= 4:
            vowels = sum(1 for c in letters_only if c in 'aeiou')
            vowel_ratio = vowels / len(letters_only)
```

**Step 2:** Count vowels
- English words have ~40% vowels
- Random typing has fewer vowels
- "hello" → 2 vowels / 5 letters = 0.4 (40%)
- "hhj" → 0 vowels / 3 letters = 0.0 (0%)

```python
            # RELAXED: Only flag as gibberish if VERY few vowels
            if vowel_ratio < 0.10 and len(letters_only) >= 5:
                return False, "gibberish"
```

**Threshold:** Less than 10% vowels AND at least 5 letters

**Examples:**
- "hello" → 40% vowels → ✅ VALID
- "what" → 25% vowels → ✅ VALID  
- "hhhjjjkkk" → 0% vowels → ❌ GIBBERISH
- "xzqrt" → 0% vowels → ❌ GIBBERISH

**Why 10% threshold?**
- Too strict: flags real questions
- Too loose: allows gibberish
- 10% = good balance

```python
            # Check for completely random characters
            if vowels == 0 and len(letters_only) <= 4:
                return False, "gibberish"
```

**Short queries with NO vowels:**
- "hhj" → gibberish
- "xyz" → gibberish  
- But: "hi" → has 'i', valid
- And: "ok" → has 'o', valid

```python
    # Very short queries without meaning
    if len(query_lower) < 2:
        return False, "too_short"
```

**Single character queries:**
- "a" → too short
- "?" → too short
- "hi" → length 2, OK

```python
    # Everything else is valid
    return True, "valid"
```

**If passed all checks:** It's a valid query!

---

## Part 5: Query Type Detection (`detect_query_type`)

This determines: PDF? SQL? or Both?

```python
def detect_query_type(self, query: str) -> str:
    """
    Determine which engine(s) should handle the query.
    
    Uses semantic similarity + keyword matching.
    
    Returns:
        'pdf', 'sql', or 'both'
    """
```

**Three possible outcomes:**
1. **'pdf'** - Search PDFs only
2. **'sql'** - Query SQL database only
3. **'both'** - Use both engines

```python
    query_lower = query.lower()
    
    # Calculate semantic similarity scores
    pdf_text = "Ethiopian Statistical Service reports CPI inflation prices agriculture census population"
    sql_text = "SDG sustainable development goals indicators poverty mortality education health"
```

**Domain descriptions:**
- **PDF domain:** Keywords that represent ESS documents
- **SQL domain:** Keywords that represent SDG data

**Why these specific words?**
- Represent the **core content** of each database
- Used for similarity comparison

```python
    # Encode query and domain texts
    query_embedding = self.embeddings.embed_query(query_lower)
    pdf_embedding = self.embeddings.embed_query(pdf_text)
    sql_embedding = self.embeddings.embed_query(sql_text)
```

**What `.embed_query()` does:**
- Converts text → vector (list of numbers)
- Example: "What is CPI?" → [0.2, 0.8, 0.3, ..., 0.5] (384 numbers)

**All use same embedding model:**
- Query, PDF domain, SQL domain
- Must use same model for fair comparison!

```python
    # Calculate cosine similarity
    from numpy import dot
    from numpy.linalg import norm
    
    pdf_similarity = dot(query_embedding, pdf_embedding) / (norm(query_embedding) * norm(pdf_embedding))
    sql_similarity = dot(query_embedding, sql_embedding) / (norm(query_embedding) * norm(sql_embedding))
```

**Cosine Similarity Formula:**

```
similarity = (A · B) / (||A|| × ||B||)

Where:
A · B = dot product (sum of element-wise multiplication)
||A|| = magnitude/length of vector A
||B|| = magnitude/length of vector B
```

**Result range:** -1 to 1
- 1.0 = identical vectors
- 0.0 = orthogonal (unrelated)
- -1.0 = opposite directions

**Example:**
- Query: "What is CPI?"
- PDF domain similarity: 0.85 (high - CPI in PDFs)
- SQL domain similarity: 0.32 (low - CPI not in SDG)

```python
    # Keyword-based scoring
    pdf_keywords = [
        'cpi', 'consumer price', 'inflation', 'price index',
        'agricultural', 'census', 'livestock', 'survey',
        'amhara', 'oromia', 'tigray', 'region'
    ]
```

**PDF-specific keywords:**
- CPI, inflation → Economic reports
- Agricultural, livestock → Survey data
- Amhara, Oromia → Ethiopian regions (not in SDG data)

```python
    sql_keywords = [
        'sdg', 'goal', 'poverty', 'target', 'indicator',
        'mortality', 'enrollment', 'sanitation', 'health',
        'education', 'gender', 'inequality'
    ]
```

**SQL-specific keywords:**
- SDG terminology
- Specific indicators
- Global development terms

```python
    # Count keyword matches (weighted)
    pdf_keyword_score = sum(2.0 if kw in query_lower else 0 for kw in pdf_keywords)
    sql_keyword_score = sum(2.0 if kw in query_lower else 0 for kw in sql_keywords)
```

**Keyword scoring:**
- Each keyword match = +2.0 points
- More keywords = higher score
- Example: "What is the poverty rate?" 
  - Contains "poverty" → SQL +2.0

```python
    # Normalize keyword scores (0-10 scale)
    max_possible = len(pdf_keywords) * 2.0
    pdf_keyword_score = (pdf_keyword_score / max_possible) * 10
    sql_keyword_score = (sql_keyword_score / len(sql_keywords) * 2.0) * 10
```

**Normalization:**
- Convert to 0-10 scale
- Makes scores comparable
- PDF has 12 keywords, SQL has 11
- Normalization makes them fair to compare

```python
    # Combined score: 60% semantic + 40% keywords
    pdf_score = (pdf_similarity * 10) * 0.6 + pdf_keyword_score * 0.4
    sql_score = (sql_similarity * 10) * 0.6 + sql_keyword_score * 0.4
```

**Weighted combination:**
- **60% semantic similarity** (meaning-based)
- **40% keyword matching** (exact-word-based)

**Why this split?**
- Semantic: Catches synonyms, related concepts
- Keywords: Catches specific terms
- 60/40: Balance between flexibility and precision

**Example calculation:**
```
Query: "What is Ethiopia's poverty rate?"

Semantic:
- PDF similarity: 0.45 × 10 = 4.5
- SQL similarity: 0.82 × 10 = 8.2

Keywords:
- PDF: 0 matches = 0
- SQL: 1 match (poverty) = 1.8 (normalized)

Combined:
- PDF: (4.5 × 0.6) + (0 × 0.4) = 2.7
- SQL: (8.2 × 0.6) + (1.8 × 0.4) = 5.64

Winner: SQL (higher score)
```

```python
    if self.verbose:
        print(f"[SEMANTIC] PDF similarity: {pdf_similarity * 10:.2f}, SQL similarity: {sql_similarity * 10:.2f}")
        print(f"[ROUTING] PDF score: {pdf_score:.2f}, SQL score: {sql_score:.2f}")
```

**Debug output** (if verbose mode enabled):
- Shows similarity scores
- Shows final combined scores
- Helps understand routing decisions

```python
    # Decision logic
    if pdf_score > sql_score * 1.5:  # PDF significantly higher
        return 'pdf'
    elif sql_score > pdf_score * 1.5:  # SQL significantly higher
        return 'sql'
    else:  # Scores close - use both
        return 'both'
```

**Decision thresholds:**

1. **PDF wins if:** PDF score > SQL score × 1.5
   - Must be **50% higher** to choose PDF only

2. **SQL wins if:** SQL score > PDF score × 1.5
   - Must be **50% higher** to choose SQL only

3. **Both if:** Scores within 50% of each other
   - Ambiguous → use both engines
   - Better to have redundancy than miss data

**Why 1.5× threshold?**
- Not too aggressive (would always use both)
- Not too conservative (would never use both)
- 50% difference = clear preference

**Examples:**
```
Case 1: PDF=8.0, SQL=3.0
8.0 > 3.0 × 1.5 = 4.5? YES → PDF only

Case 2: PDF=4.0, SQL=7.0
7.0 > 4.0 × 1.5 = 6.0? YES → SQL only

Case 3: PDF=5.0, SQL=6.0
6.0 > 5.0 × 1.5 = 7.5? NO → BOTH

5.0 > 6.0 × 1.5 = 9.0? NO → BOTH
```

---

##  Summary So Far

You've learned:

1. ✅ **Validation** - How to detect greetings, gibberish, meta questions
2. ✅ **Semantic Similarity** - Convert text to vectors and compare
3. ✅ **Keyword Matching** - Count specific terms
4. ✅ **Weighted Scoring** - Combine semantic + keywords intelligently
5. ✅ **Decision Logic** - Route to PDF, SQL, or both

**Next:** Engine-specific query methods (how PDFs and SQL are actually searched)

Continue to Part 3...

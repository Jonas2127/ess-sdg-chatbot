# 🧠 Dual-Engine Router - Part 4: Main Query Interface

**File:** `src/dual_engine_router/langchain_rag.py`  
**Section:** Main Query Method - Orchestrating Everything

---

## 🎯 What You'll Learn

- How the main `query()` method coordinates both engines
- Smart engine combination logic
- Response assembly
- Complete request/response flow
- Error handling and edge cases

---

## 🎭 The Orchestrator: `query()` Method

This is the **public interface** - what the Streamlit app calls:

```python
def query(self, question: str, verbose: bool = True) -> Dict:
    """
    Main query interface. Routes question to appropriate engine(s).
    
    Args:
        question: User's question
        verbose: Print processing information
        
    Returns:
        Dictionary with answer, sources, and metadata
    """
```

**This method is the conductor of the orchestra:**
- Validates the question
- Routes to correct engine(s)
- Combines results intelligently
- Returns unified response

---

## 💻 Complete Code Analysis

### Step 1: Query Validation

```python
    # Validate query
    is_valid, validation_type = self._is_valid_query(question)
```

**Calls validation function** (explained in Part 1):
- Returns: `(True, "valid")` or `(False, "greeting")`
- Catches greetings, gibberish, meta questions

**Example outputs:**
```python
"how are you?" → (False, "greeting")
"hhhjjj"      → (False, "gibberish")
"What is CPI?" → (True, "valid")
```

---

### Step 2: Handle Invalid Queries

```python
    if not is_valid:
        if validation_type == "greeting":
            return {
                'answer': "Hello! 👋 I'm doing great, thank you for asking!...",
                'sources': [],
                'source_count': 0,
                'response_time': 0
            }
```

**Instant responses for non-data queries:**

#### **Greeting Response:**
```python
{
    'answer': "Hello! 👋 I'm doing great, thank you for asking! 
               I'm here to help you find information about Ethiopian 
               statistics and SDG indicators...",
    'sources': [],
    'source_count': 0,
    'response_time': 0
}
```

**Why response_time = 0?**
- No database search needed
- Instant response
- Pre-programmed answer

#### **Meta Question Response:**
```python
        elif validation_type == "meta_question":
            return {
                'answer': "I am the ET ESS RAG Bot - an AI assistant...",
                'sources': [],
                'source_count': 0,
                'response_time': 0
            }
```

**Explains the bot itself:**
- What it is
- What it can do
- What data it has access to

#### **Gibberish Response:**
```python
        elif validation_type == "gibberish":
            return {
                'answer': "I couldn't understand your question. Please rephrase using clear language.",
                'sources': [],
                'source_count': 0,
                'response_time': 0
            }
```

**Polite rejection:**
- Clear message
- Suggests solution
- No wasted processing

---

### Step 3: Detect Query Type (Routing Decision)

```python
    # Detect query type
    query_type = self.detect_query_type(question)
    
    if verbose:
        print(f"[INFO] Query type: {query_type}")
```

**Calls routing logic** (explained in Part 1):
- Returns: `"pdf"`, `"sql"`, or `"both"`
- Based on semantic + keyword scores

**Example routing:**
```python
"What is CPI?"                    → "pdf"  (PDF documents)
"What is the poverty rate?"       → "sql"  (SDG database)
"Population and economic trends"  → "both" (Both sources)
```

**Debug output (if verbose):**
```
[INFO] Query type: pdf
```

---

### Step 4: Start Timer

```python
    import time
    start_time = time.time()
```

**Performance tracking:**
- Measures total query time
- Includes routing + retrieval + generation
- Used for optimization

---

### Step 5: Route to Appropriate Engine(s)

#### **Case 1: PDF Engine Only**

```python
    # Route to appropriate engine(s)
    if query_type == 'pdf':
        result = self.query_engine_a(question)
```

**Simple delegation:**
- Calls `query_engine_a()` (explained in Part 2)
- Returns complete result
- No combination needed

**Flow:**
```
Question → Detect: PDF → Engine A → Return Result
```

**Example:**
```python
Question: "What is the Consumer Price Index?"
Route: PDF
Result: {
    'answer': "The CPI for December 2022 was 125.3...",
    'sources': [{'document': 'CPI_DEC_2022.pdf', ...}],
    'source_count': 2
}
```

---

#### **Case 2: SQL Engine Only**

```python
    elif query_type == 'sql':
        result = self.query_engine_b(question)
```

**Simple delegation:**
- Calls `query_engine_b()` (explained in Part 3)
- Returns complete result
- No combination needed

**Flow:**
```
Question → Detect: SQL → Engine B → Return Result
```

**Example:**
```python
Question: "What is the poverty rate in 2021?"
Route: SQL
Result: {
    'answer': "The poverty rate in 2021 was 23.5%...",
    'sources': [{'table': 'sdg_data', ...}],
    'source_count': 1
}
```

---

#### **Case 3: Both Engines (Smart Combination)**

```python
    else:  # both
        pdf_result = self.query_engine_a(question)
        sql_result = self.query_engine_b(question)
```

**Parallel execution conceptually:**
- Query Engine A (PDF)
- Query Engine B (SQL)
- Both work with same question

**Note:** Actually sequential in this implementation
- Could be parallelized for speed
- But adds complexity

---

### Step 6: Smart Result Combination Logic

This is the **intelligent part** - don't blindly combine!

```python
        # Check if either engine has actual data
        pdf_has_data = (
            pdf_result.get('source_count', 0) > 0 and
            'no relevant data' not in pdf_result.get('answer', '').lower()
        )
```

**What is "has data"?**

**Two conditions must BOTH be true:**

1. **`source_count > 0`** - Found sources
   ```python
   pdf_result = {'source_count': 3, ...}  # ✅ Has sources
   pdf_result = {'source_count': 0, ...}  # ❌ No sources
   ```

2. **No "no relevant data" in answer** - Meaningful answer
   ```python
   answer = "The CPI was 125.3"           # ✅ Has data
   answer = "No relevant data found"      # ❌ No data
   ```

**Why both checks?**
- Sometimes retrieval returns documents but they're not relevant
- Sometimes SQL query runs but returns no rows
- Need to verify ACTUAL useful data

```python
        sql_has_data = (
            sql_result.get('source_count', 0) > 0 and
            'does not appear to be' not in sql_result.get('answer', '').lower()
        )
```

**SQL "has data" check:**
- Same logic as PDF
- Different phrase: "does not appear to be"
- SQL often says "data does not appear to be available"

---

### Step 7: Smart Combining - Four Scenarios

#### **Scenario 1: Both Have Data** ✅✅

```python
        if pdf_has_data and sql_has_data:
            # Both have data - combine them
            combined_answer = f"From ESS PDF Documents:\n{pdf_result.get('answer', 'No data')}\n\n"
            combined_answer += f"From UN SDG Database:\n{sql_result.get('answer', 'No data')}"
```

**Create combined answer:**
```
From ESS PDF Documents:
[Answer from PDFs]

From UN SDG Database:
[Answer from SQL]
```

**Why this format?**
- Clear separation
- User knows where each part comes from
- Both perspectives provided

**Example:**
```python
Question: "Tell me about poverty in Ethiopia"

Combined Answer:
"From ESS PDF Documents:
Ethiopia has made significant progress in reducing poverty 
over the past decade, with targeted interventions in rural areas...

From UN SDG Database:
The poverty rate in Ethiopia decreased from 29.6% in 2016 
to 23.5% in 2021, showing a downward trend..."
```

```python
            result = {
                'answer': combined_answer,
                'sources': pdf_result.get('sources', []) + sql_result.get('sources', []),
                'source_count': pdf_result.get('source_count', 0) + sql_result.get('source_count', 0)
            }
```

**Combine everything:**
- **Answer:** Both answers with labels
- **Sources:** PDF sources + SQL sources (concatenate lists)
- **Count:** Sum of both counts

**Example result:**
```python
{
    'answer': "From ESS PDF Documents:\n...\n\nFrom UN SDG Database:\n...",
    'sources': [
        {'document': 'poverty_report.pdf', 'page': 5},
        {'document': 'census_2022.pdf', 'page': 12},
        {'table': 'sdg_data', 'indicator': '1.1.1'}
    ],
    'source_count': 3
}
```

---

#### **Scenario 2: Only PDF Has Data** ✅❌

```python
        elif pdf_has_data:
            # Only PDF has data - use it
            result = pdf_result
```

**Simple case:**
- SQL found nothing
- PDF found answer
- Use PDF result as-is

**Why not mention SQL failure?**
- User doesn't care about what didn't work
- Just show what did work
- Clean user experience

**Example:**
```python
Question: "What is Ethiopia's agricultural policy?"

Result: Uses PDF result
# SQL has no agricultural policy data
# PDF has policy documents
# → Show PDF answer only
```

---

#### **Scenario 3: Only SQL Has Data** ❌✅

```python
        elif sql_has_data:
            # Only SQL has data - use it
            result = sql_result
```

**Mirror of scenario 2:**
- PDF found nothing
- SQL found answer
- Use SQL result as-is

**Example:**
```python
Question: "What is the exact mortality rate in 2021?"

Result: Uses SQL result
# PDF has narratives, not exact numbers
# SQL has precise statistics
# → Show SQL answer only
```

---

#### **Scenario 4: Neither Has Data** ❌❌

```python
        else:
            # Neither has data
            result = {
                'answer': "I couldn't find relevant information in either the ESS PDF documents or the UN SDG database for this query.",
                'sources': [],
                'source_count': 0
            }
```

**Honest response:**
- Searched everywhere
- Found nothing
- Tell user clearly

**Why honest?**
- Better than making things up (hallucination)
- User can rephrase question
- Builds trust

**Example:**
```python
Question: "What is the quantum physics theory in Ethiopia?"

Result:
# Not in ESS documents
# Not in SDG database
# → Tell user we don't have this
```

---

### Step 8: Add Response Time

```python
    result['response_time'] = time.time() - start_time
```

**Calculate elapsed time:**
```python
start_time = 1234567890.123
end_time = 1234567893.456
response_time = 893.456 - 890.123 = 3.333 seconds
```

**Add to result:**
```python
result['response_time'] = 3.333
```

**Why include this?**
- Performance monitoring
- User feedback (show loading time)
- Identify slow queries

---

### Step 9: Debug Output

```python
    if verbose:
        print(f"[DONE] Response generated in {result['response_time']:.2f}s")
```

**Console output:**
```
[DONE] Response generated in 3.33s
```

**Format string explained:**
- `{result['response_time']:.2f}` 
- `.2f` = Format as float with 2 decimal places
- `3.333333` becomes `3.33`

---

### Step 10: Return Final Result

```python
    return result
```

**Complete response dictionary:**
```python
{
    'answer': "The Consumer Price Index...",
    'sources': [
        {'document': 'CPI_DEC_2022.pdf', 'page': 5, 'score': 0.89},
        {'document': 'inflation_report.pdf', 'page': 12, 'score': 0.76}
    ],
    'source_count': 2,
    'response_time': 3.33
}
```

**This is what Streamlit app receives!**

---

## 🔄 Complete Query Flow Diagram

```
User Question: "What is the poverty rate?"
    ↓
[1] Validate Query
    ├─ Greeting? → Return instant response
    ├─ Gibberish? → Return error message
    ├─ Meta question? → Return bot info
    └─ Valid? → Continue ✅
    ↓
[2] Detect Query Type (Routing)
    ├─ Semantic similarity: 60%
    └─ Keyword matching: 40%
    ↓
[3] Route Decision
    ├─ PDF only? → Query Engine A → Return
    ├─ SQL only? → Query Engine B → Return
    └─ Both? → Query both engines ↓
    ↓
[4] Check Data Quality
    ├─ Both have data? → Combine ✅
    ├─ Only PDF? → Use PDF ✅
    ├─ Only SQL? → Use SQL ✅
    └─ Neither? → "Not found" message
    ↓
[5] Add Metadata
    ├─ Response time
    └─ Source count
    ↓
[6] Return Result
    └─ {'answer', 'sources', 'source_count', 'response_time'}
```

---

## 🎯 Key Design Decisions

### **1. Why Validate First?**
```python
# Bad approach:
Query anything → Always search databases → Waste resources

# Good approach (ours):
"hi" → Detect greeting → Return instantly → Save 5 seconds
```

### **2. Why Smart Combination?**
```python
# Bad approach:
Always combine both → Show "No data" from one engine

# Good approach (ours):
Check data quality → Only show what's relevant
```

### **3. Why Three Query Types?**
```python
# Could be just one:
Always query both → Slow, wasteful

# Better (ours):
Route smartly → Faster, more accurate
```

### **4. Why Transparent Errors?**
```python
# Bad:
No data found → Make up answer (hallucination)

# Good (ours):
No data found → Tell user honestly
```

---

## 🧪 Example Query Flows

### **Example 1: Simple PDF Query**

```python
query("What is the Consumer Price Index?")

[1] Validate: Valid ✅
[2] Route: PDF (score 8.5 vs 2.1)
[3] Query Engine A
    - MMR retrieval: 15 docs
    - Re-rank: 7 docs
    - Filter: 3 relevant
    - Generate answer
[4] Return: {
    'answer': "The CPI for December 2022...",
    'sources': [...],
    'response_time': 3.2
}
```

### **Example 2: Simple SQL Query**

```python
query("What is the poverty rate in 2021?")

[1] Validate: Valid ✅
[2] Route: SQL (score 9.1 vs 3.2)
[3] Query Engine B
    - Generate SQL
    - Execute query
    - Format results
    - Generate answer
[4] Return: {
    'answer': "The poverty rate in 2021 was 23.5%",
    'sources': [...],
    'response_time': 1.5
}
```

### **Example 3: Both Engines**

```python
query("Tell me about poverty in Ethiopia")

[1] Validate: Valid ✅
[2] Route: Both (scores: PDF=6.2, SQL=7.1, ratio < 1.5)
[3] Query Both Engines
    Engine A: Policy documents, narratives
    Engine B: Statistics, indicators
[4] Check Data: Both have data ✅
[5] Combine:
    "From ESS PDF Documents:\n[qualitative]\n\nFrom UN SDG Database:\n[quantitative]"
[6] Return: {
    'answer': "Combined answer",
    'sources': [PDF sources + SQL sources],
    'response_time': 4.8
}
```

### **Example 4: Greeting (Fast Path)**

```python
query("how are you?")

[1] Validate: Greeting ❌
[2] Return instantly: {
    'answer': "Hello! 👋 I'm doing great...",
    'sources': [],
    'response_time': 0
}
# No database search!
# Total time: <0.01s
```

---

## 🎓 Key Takeaways

1. **Validation First** - Filter out non-data queries early
2. **Smart Routing** - Don't search everywhere for every query
3. **Quality Checks** - Verify data before combining
4. **Transparent Errors** - Honest "not found" beats hallucination
5. **Performance Tracking** - Measure everything
6. **User Experience** - Clean, clear responses

---

## 📝 Common Modifications

### Want to change routing threshold?

```python
# Current: 50% difference needed
if pdf_score > sql_score * 1.5:  # Change 1.5 to 1.3 or 2.0

# More aggressive (use single engine more often):
if pdf_score > sql_score * 1.3:  # Lower threshold

# More conservative (use both engines more often):
if pdf_score > sql_score * 2.0:  # Higher threshold
```

### Want to always use both engines?

```python
# Change routing logic:
query_type = "both"  # Force both engines
```

### Want to add caching?

```python
# Add before routing:
if question in self.cache:
    return self.cache[question]

# Add before return:
self.cache[question] = result
return result
```

---

**Continue to Part 5: Response Assembly & Source Display**

Next: How responses are formatted for the UI!

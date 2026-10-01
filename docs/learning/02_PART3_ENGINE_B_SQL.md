# 🧠 Dual-Engine Router - Part 3: Engine B (SQL Database)

**File:** `src/dual_engine_router/langchain_rag.py`  
**Section:** Engine B SQL Query Implementation

---

## 🎯 What You'll Learn

- How to query structured SQL databases with natural language
- LangChain SQL database integration
- Prompt engineering for SQL generation
- Query validation and safety
- Result formatting for natural responses

---

## 📊 Engine B: SQL Database System

### Purpose:
Query **12,037 SDG indicators** from structured SQLite database for questions like:
- "What is the poverty rate in 2021?"
- "Show mortality statistics for Ethiopia"
- "What is the education enrollment rate?"

### Technology Stack:
- **SQLite** - Lightweight SQL database
- **LangChain SQLDatabase** - SQL query wrapper
- **LLM** - Generates SQL from natural language
- **Pandas** - Data formatting (if needed)

### Database Structure:
```sql
-- Table: sdg_data
CREATE TABLE sdg_data (
    id INTEGER PRIMARY KEY,
    goal_number INTEGER,
    indicator_code TEXT,
    indicator_name TEXT,
    country TEXT,
    year INTEGER,
    value REAL,
    unit TEXT
);

-- Example rows:
goal_number | indicator_code | indicator_name        | year | value
1           | 1.1.1         | Poverty rate          | 2021 | 23.5
3           | 3.2.1         | Under-5 mortality     | 2021 | 52.3
4           | 4.1.1         | Education enrollment  | 2021 | 87.2
```

---

## 💻 Code Analysis: `query_engine_b()`

```python
def query_engine_b(self, query: str) -> Dict:
    """Query Engine B (SQL) for structured SDG indicator data."""
```

**Function signature:**
- Input: `query: str` - User's question
- Output: `Dict` - Dictionary with answer, sources, metadata

**Returns structure:**
```python
{
    'answer': "The poverty rate in 2021 was 23.5%",
    'sources': [
        {'table': 'sdg_data', 'indicator': '1.1.1', 'year': 2021}
    ],
    'source_count': 1,
    'response_time': 1.23
}
```

---

### Step 1: Check Engine Availability

```python
    if not self.engine_b_available:
        return {
            'answer': "SQL database is not available.",
            'sources': [],
            'source_count': 0
        }
```

**What this checks:**
- Was SQLite database initialized?
- Is database file accessible?
- Can we connect to it?

**Why this check?**
- Prevents crashes if database missing
- Graceful degradation
- Clear error messages

---

### Step 2: Start Timer

```python
    import time
    start_time = time.time()
```

**Same as Engine A:**
- Track query execution time
- Performance monitoring
- Helps identify slow queries

---

### Step 3: SQL Database Integration

During initialization, this was set up:

```python
# In __init__():
from langchain_community.utilities import SQLDatabase

self.sql_db = SQLDatabase.from_uri(f"sqlite:///{SQLITE_PATH}")
```

**What is SQLDatabase?**
LangChain wrapper that:
- Connects to SQL database
- Provides safe query execution
- Handles different SQL dialects
- Prevents SQL injection

**Connection string explained:**
```python
f"sqlite:///{SQLITE_PATH}"
# ↓
"sqlite:///data/sql_database/sdg_ethiopia.db"

# Format: protocol://path
# sqlite:// - SQLite protocol
# / - Absolute path follows
# data/sql_database/sdg_ethiopia.db - Database file
```

---

### Step 4: Create SQL Query Chain

```python
    try:
        # Create SQL query chain
        from langchain.chains import create_sql_query_chain
        
        sql_chain = create_sql_query_chain(
            llm=self.llm,
            db=self.sql_db
        )
```

**What is `create_sql_query_chain`?**

A LangChain helper that creates this flow:
```
User Question
    ↓
[Understand question]
    ↓
[Generate SQL query]
    ↓
[Execute query safely]
    ↓
[Format results]
    ↓
Natural language answer
```

**Parameters:**
- `llm=self.llm` - Language model (Ollama/Groq/Gemini)
- `db=self.sql_db` - Database connection

**What it does internally:**
1. Analyzes database schema
2. Understands table structure
3. Generates appropriate SQL
4. Validates query safety
5. Executes query
6. Returns results

---

### Step 5: The SQL Prompt Template

Behind the scenes, LangChain uses a prompt like this:

```python
sql_prompt = """
Given an input question, create a syntactically correct SQLite query.

Database Schema:
{schema}

Question: {question}

Return only the SQL query, nothing else.
Do not include explanations or markdown.

SQL Query:
"""
```

**Why this format?**
- Clear instructions
- Schema included (table structure)
- Specific output format
- No ambiguity

**Example interaction:**

**Schema provided to LLM:**
```sql
CREATE TABLE sdg_data (
    goal_number INTEGER,
    indicator_code TEXT,
    indicator_name TEXT,
    year INTEGER,
    value REAL
)
```

**Question:** "What is the poverty rate in 2021?"

**LLM generates:**
```sql
SELECT value, indicator_name 
FROM sdg_data 
WHERE indicator_code = '1.1.1' 
  AND year = 2021
  AND country = 'Ethiopia'
LIMIT 1;
```

**Why good SQL?**
- Specific indicator code (1.1.1 = poverty rate)
- Filters by year
- Limits results (performance)
- Safe query (no DROP, DELETE, etc.)

---

### Step 6: Generate SQL Query

```python
        # Generate SQL query from natural language
        sql_query = sql_chain.invoke({"question": query})
```

**What `.invoke()` does:**
1. Takes user question
2. Sends to LLM with schema
3. Gets SQL query back
4. Returns as string

**Example:**
```python
query = "What is the poverty rate in 2021?"

sql_query = sql_chain.invoke({"question": query})
# Returns: "SELECT value FROM sdg_data WHERE indicator_code = '1.1.1' AND year = 2021"
```

---

### Step 7: SQL Query Safety

**Important security consideration:**

LangChain has built-in safety:
```python
# Blocked queries:
"DROP TABLE sdg_data"  # ❌ Blocked
"DELETE FROM sdg_data" # ❌ Blocked
"UPDATE sdg_data SET..." # ❌ Blocked

# Allowed queries:
"SELECT * FROM sdg_data WHERE..." # ✅ Allowed
"SELECT COUNT(*) FROM..." # ✅ Allowed
```

**How it works:**
```python
# Simplified safety check:
dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER']

if any(keyword in sql_query.upper() for keyword in dangerous_keywords):
    raise SecurityError("Dangerous SQL operation detected!")
```

**Why this matters:**
- Prevents database destruction
- Protects data integrity
- Blocks malicious queries
- Read-only operations only

---

### Step 8: Execute SQL Query

```python
        # Execute the SQL query
        result = self.sql_db.run(sql_query)
```

**What `.run()` does:**
```python
# Behind the scenes:
def run(sql_query):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(sql_query)
    result = cursor.fetchall()
    conn.close()
    return result
```

**Result format:**
```python
# Query: "SELECT value FROM sdg_data WHERE indicator_code = '1.1.1'"
result = [(23.5,)]  # Tuple of tuples

# Query: "SELECT indicator_name, value FROM sdg_data"
result = [
    ('Poverty rate', 23.5),
    ('Extreme poverty', 18.2),
    ('Food insecurity', 31.4)
]
```

---

### Step 9: Check if Data Found

```python
        # Check if we got results
        if not result or result == "[]" or "no rows" in str(result).lower():
            return {
                'answer': "No data found in the SDG database for this query.",
                'sources': [],
                'source_count': 0,
                'response_time': time.time() - start_time
            }
```

**Multiple checks:**

1. **`not result`** - Empty result (None or [])
2. **`result == "[]"`** - String representation of empty list
3. **`"no rows" in str(result)`** - SQL message

**Why multiple checks?**
Different scenarios return different "empty":
- Query runs but no matches
- Table empty
- Connection issues

**Early return:**
If no data, don't waste time generating answer
- Clear message to user
- No sources to cite
- Fast response

---

### Step 10: Format SQL Results for LLM

```python
        # Format the SQL result for better presentation
        formatted_result = self._format_sql_result(result)
```

**What is formatting?**

**Before formatting:**
```python
result = [
    ('Poverty rate', 23.5, 2021),
    ('Poverty rate', 22.1, 2020),
    ('Poverty rate', 24.3, 2019)
]
```

**After formatting:**
```python
formatted_result = """
Indicator: Poverty rate
Year 2021: 23.5%
Year 2020: 22.1%
Year 2019: 24.3%
"""
```

**Why format?**
- LLM understands structured text better
- Easier to generate natural answer
- Clear presentation of data

---

### Step 11: Format SQL Result Implementation

```python
def _format_sql_result(self, result: str) -> str:
    """
    Format SQL query result for better LLM understanding.
    
    Converts raw SQL output into readable text format.
    """
```

```python
    # If result is already a string, return as-is
    if isinstance(result, str):
        return result
```

**Type check:**
Sometimes `.run()` returns string directly
- If already formatted, use it
- Avoid double-processing

```python
    # Convert to string if it's a list/tuple
    if isinstance(result, (list, tuple)):
        if len(result) == 0:
            return "No data found"
```

**Handle empty results:**
Even after earlier check, double-check
- Better safe than sorry
- Defensive programming

```python
        # Format as readable text
        formatted = []
        for row in result:
            # Convert row to string, join with commas
            row_str = ", ".join(str(item) for item in row)
            formatted.append(row_str)
        
        return "\n".join(formatted)
```

**Formatting logic:**

**Input:**
```python
result = [
    ('Poverty rate', 23.5, 2021),
    ('Mortality rate', 52.3, 2021)
]
```

**Step 1 - Process each row:**
```python
row = ('Poverty rate', 23.5, 2021)
row_str = ", ".join(str(item) for item in row)
# Result: "Poverty rate, 23.5, 2021"
```

**Step 2 - Join rows with newlines:**
```python
formatted = [
    "Poverty rate, 23.5, 2021",
    "Mortality rate, 52.3, 2021"
]
result = "\n".join(formatted)
```

**Final output:**
```
Poverty rate, 23.5, 2021
Mortality rate, 52.3, 2021
```

---

### Step 12: Generate Natural Language Answer

```python
        # Create prompt for LLM to generate natural language answer
        answer_prompt = f"""
Based on the following data from the SDG database, answer the question in a clear and concise way.

Question: {query}

Data: {formatted_result}

Provide a direct answer with relevant statistics. If the data shows trends, mention them.

Answer:"""
```

**Prompt structure:**

1. **Instruction:** "Based on the following data..."
2. **Question:** Original user query
3. **Data:** Formatted SQL results
4. **Guidance:** "Provide a direct answer..."

**Why this format?**
- Clear context for LLM
- Specific data to work with
- Instructions for tone and style
- Reduces hallucination

**Example:**

**Prompt sent to LLM:**
```
Based on the following data from the SDG database, answer the question in a clear and concise way.

Question: What is the poverty rate in 2021?

Data: Poverty rate, 23.5, 2021

Provide a direct answer with relevant statistics.

Answer:
```

**LLM generates:**
```
The poverty rate in Ethiopia in 2021 was 23.5%. This indicator, 
tracked under SDG Goal 1, represents the proportion of the population 
living below the national poverty line.
```

---

### Step 13: Invoke LLM

```python
        # Generate natural language answer
        answer = self.llm.invoke(answer_prompt)
```

**What `.invoke()` does:**
- Sends prompt to LLM
- Waits for response
- Returns generated text

**Different LLMs behave differently:**

**Ollama (local):**
```python
# Sends to localhost:11434
response = requests.post('http://localhost:11434/api/generate', {
    'model': 'llama3.2:1b',
    'prompt': answer_prompt
})
answer = response.json()['response']
```

**Groq (cloud):**
```python
# Sends to Groq API
response = groq_client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": answer_prompt}]
)
answer = response.choices[0].message.content
```

---

### Step 14: Extract Answer Text

```python
        # Extract text from LLM response
        if hasattr(answer, 'content'):
            answer_text = answer.content
        else:
            answer_text = str(answer)
```

**Handle different response formats:**

**ChatGPT/Groq format:**
```python
answer = {
    'content': "The poverty rate in 2021 was 23.5%",
    'role': 'assistant'
}
answer_text = answer.content  # Use .content attribute
```

**Ollama format:**
```python
answer = "The poverty rate in 2021 was 23.5%"
answer_text = str(answer)  # Convert to string
```

**Why check?**
- Different LLM libraries return different formats
- Need consistent string output
- Avoid crashes from unexpected formats

---

### Step 15: Create Sources

```python
        # Create source information
        sources = [{
            'type': 'sql_database',
            'table': 'sdg_data',
            'query': sql_query,
            'result_count': len(result) if isinstance(result, (list, tuple)) else 1
        }]
```

**Source metadata:**

```python
{
    'type': 'sql_database',          # Engine type
    'table': 'sdg_data',             # Table queried
    'query': 'SELECT value FROM...', # Actual SQL
    'result_count': 3                # How many rows returned
}
```

**Why include SQL query?**
- Transparency: Show what was queried
- Debugging: Verify correct SQL generated
- Reproducibility: Can run query manually

---

### Step 16: Return Complete Response

```python
        return {
            'answer': answer_text,
            'sources': sources,
            'source_count': len(sources),
            'response_time': time.time() - start_time
        }
```

**Complete response structure:**

```python
{
    'answer': "The poverty rate in Ethiopia for 2021 was 23.5%...",
    'sources': [{
        'type': 'sql_database',
        'table': 'sdg_data',
        'query': 'SELECT value FROM sdg_data WHERE...',
        'result_count': 1
    }],
    'source_count': 1,
    'response_time': 1.23
}
```

---

### Step 17: Error Handling

```python
    except Exception as e:
        print(f"[ERROR] Engine B failed: {e}")
        return {
            'answer': f"Error querying SDG database: {str(e)}",
            'sources': [],
            'source_count': 0,
            'response_time': time.time() - start_time
        }
```

**Catches all errors:**
- SQL syntax errors
- Database connection issues
- LLM generation failures
- Unexpected exceptions

**Why broad try-except?**
- System should never crash
- Always return something to user
- Log error for debugging

**Error response:**
```python
{
    'answer': "Error querying SDG database: table not found",
    'sources': [],
    'source_count': 0,
    'response_time': 0.05
}
```

---

## 🔄 Complete SQL Engine Flow

```
User Query: "What is the poverty rate in 2021?"
    ↓
[1] Create SQL chain (LLM + Database)
    ↓
[2] LLM generates SQL query:
    "SELECT value FROM sdg_data WHERE indicator_code = '1.1.1' AND year = 2021"
    ↓
[3] Execute SQL safely
    ↓
[4] Get result: [(23.5,)]
    ↓
[5] Format result: "Poverty rate, 23.5, 2021"
    ↓
[6] Create prompt for LLM with data
    ↓
[7] LLM generates natural answer
    ↓
[8] Return answer + sources
```

---

## 🆚 Engine A vs Engine B Comparison

| Aspect | Engine A (PDF) | Engine B (SQL) |
|--------|----------------|----------------|
| **Data Type** | Unstructured text | Structured tables |
| **Search Method** | Vector similarity | SQL queries |
| **Speed** | Slower (~3-5s) | Faster (~1-2s) |
| **Precision** | Context-dependent | High (exact matches) |
| **Use Case** | Qualitative, narratives | Quantitative, statistics |
| **Example** | "Explain policy" | "What is rate X?" |

---

## 🎓 Key Takeaways

1. **Natural Language to SQL** - LLMs can generate SQL from questions
2. **Safety First** - Always validate and restrict SQL operations
3. **Format Matters** - Structured results help LLM generate better answers
4. **Error Handling** - Graceful failures keep system running
5. **Source Attribution** - Include SQL query for transparency

---

**Continue to Part 4: Main Query Interface**

Next: How the two engines are coordinated!

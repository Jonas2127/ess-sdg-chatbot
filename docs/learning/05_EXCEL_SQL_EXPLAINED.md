# 📊 Excel to SQL Database Conversion

**File:** `src/engine_b_excel_sql/excel_processor.py`  
**Purpose:** Convert 17 UN SDG Excel files into queryable SQL database

---

## 🎯 What You'll Learn

- Why Excel data needs SQL databases
- How to load and process multiple Excel files
- Data normalization and cleaning
- Creating SQL schemas
- Query execution and optimization
- Database indexing strategies

---

## 📚 Overview: Why Convert Excel to SQL?

### The Problem with Excel Files

```python
# User asks: "What was Ethiopia's poverty rate in 2020?"

# With Excel files only:
1. Search through 17 Excel files manually ❌
2. Open each file, look through sheets ❌
3. Find the right indicator, right year ❌
4. Extract the data point ❌
# Time: Minutes, Error-prone

# With SQL database:
query = "SELECT value FROM sdg_indicators WHERE indicator='poverty_rate' AND year=2020"
result = execute(query)
# Time: Milliseconds, Accurate ✅
```

### Excel vs SQL Comparison

| Feature | Excel | SQL Database |
|---------|-------|--------------|
| **Query Speed** | Slow (manual search) | Fast (indexed) |
| **Multiple Files** | Must open each | Single query |
| **Filtering** | Manual | WHERE clause |
| **Aggregation** | Formulas | SQL functions |
| **Relationships** | None | Foreign keys |
| **Concurrent Access** | Limited | Many users |
| **Data Validation** | Manual | Constraints |

---

## 🔄 Processing Flow

```
17 Excel Files (Goal1.xlsx ... Goal17.xlsx)
    ↓
[Load each file] - Read with pandas
    ↓
[Add metadata] - Goal number, goal name
    ↓
[Normalize columns] - Standardize naming
    ↓
[Combine data] - Merge into single DataFrame
    ↓
[Create SQL tables] - Write to SQLite
    ↓
[Add indexes] - Speed up queries
    ↓
SQLite Database: sdg_ethiopia.db
    ↓
[Query with SQL] - Fast, structured retrieval
```

---

## 💻 Code Analysis: Line by Line

### Class Initialization

```python
class ExcelProcessor:
    """Process UN SDG Excel files into SQL database"""
    
    def __init__(self, db_path: str = "data/sql_database/sdg_ethiopia.db"):
        """
        Initialize Excel processor
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
```

**Database path:**
```python
"data/sql_database/sdg_ethiopia.db"

# SQLite database:
# - Single file contains entire database
# - No server required
# - Portable (can copy file)
# - Perfect for local applications
```

**`self.conn = None`:**
```python
# Connection object will be created later
# None = not connected yet
# Prevents errors if methods called before connection
```

---

#### SDG Goal Descriptions

```python
        # SDG Goal descriptions
        self.sdg_goals = {
            1: "No Poverty",
            2: "Zero Hunger",
            3: "Good Health and Well-being",
            ...
            17: "Partnerships for the Goals"
        }
```

**Why store this?**

```python
# When loading Goal5.xlsx, we add:
goal_number = 5
goal_name = self.sdg_goals[5]  # "Gender Equality"

# Benefits:
# ✅ Consistent naming
# ✅ Human-readable
# ✅ Can join in SQL queries
# ✅ Single source of truth
```

**Data structure:**
```python
# Dictionary mapping:
{goal_number: goal_description}

# Access:
self.sdg_goals[5]   # → "Gender Equality"
self.sdg_goals[13]  # → "Climate Action"
```

---

### Database Connection

```python
def connect_db(self):
    """Create connection to SQLite database"""
    Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    self.conn = sqlite3.connect(self.db_path)
    print(f"✅ Connected to database: {self.db_path}")
```

---

#### Create Directory Structure

```python
    Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
```

**Breaking it down:**

```python
db_path = "data/sql_database/sdg_ethiopia.db"

# Step 1: Path object
Path(db_path)  # → WindowsPath('data/sql_database/sdg_ethiopia.db')

# Step 2: Get parent directory
.parent  # → WindowsPath('data/sql_database')

# Step 3: Create directory
.mkdir(parents=True, exist_ok=True)
```

**`mkdir` parameters:**

```python
parents=True
# If 'data' doesn't exist, create it
# If 'sql_database' doesn't exist, create it
# Creates entire path

exist_ok=True
# If directory already exists, don't error
# Safe to call multiple times
```

**Why create directory first?**
```python
# Without mkdir:
sqlite3.connect("data/sql_database/sdg_ethiopia.db")
# → Error! Directory doesn't exist ❌

# With mkdir:
mkdir("data/sql_database")
sqlite3.connect("data/sql_database/sdg_ethiopia.db")
# → Success! ✅
```

---

#### Connect to SQLite

```python
    self.conn = sqlite3.connect(self.db_path)
```

**What is `sqlite3.connect()`?**

```python
# Opens/creates SQLite database file
conn = sqlite3.connect("sdg_ethiopia.db")

# If file exists: Opens it ✅
# If file doesn't exist: Creates new database ✅

# Returns: Connection object
# Used for all database operations
```

**Connection object:**
```python
conn = sqlite3.connect("sdg_ethiopia.db")

# Can do:
conn.execute("SELECT ...")  # Run queries
conn.commit()               # Save changes
conn.close()                # Close connection
```

---

### Loading Excel Files

```python
def load_excel_file(self, file_path: str, goal_number: int) -> pd.DataFrame:
    """
    Load a single Excel file
    
    Args:
        file_path: Path to Excel file
        goal_number: SDG Goal number (1-17)
        
    Returns:
        DataFrame with SDG data
    """
```

**What is `pd.DataFrame`?**

Pandas DataFrame = spreadsheet in Python

```python
# Excel table:
| Year | Indicator      | Value |
|------|----------------|-------|
| 2020 | Poverty Rate   | 23.5  |
| 2021 | Poverty Rate   | 22.1  |

# DataFrame (same data):
df = pd.DataFrame({
    'Year': [2020, 2021],
    'Indicator': ['Poverty Rate', 'Poverty Rate'],
    'Value': [23.5, 22.1]
})

# Can filter, aggregate, transform!
```

---

#### Read Excel File

```python
    try:
        df = pd.read_excel(file_path)
```

**`pd.read_excel()`:**

```python
# Reads Excel file into DataFrame
df = pd.read_excel("Goal1.xlsx")

# Automatically:
# ✅ Detects column names (first row)
# ✅ Infers data types (number, text, date)
# ✅ Handles multiple sheets (default: first sheet)
# ✅ Parses dates

# Returns DataFrame ready for processing
```

**Error handling:**
```python
try:
    df = pd.read_excel(file_path)
except Exception as e:
    print(f"⚠️  Error loading {file_path}: {str(e)}")
    return pd.DataFrame()  # Return empty DataFrame

# Prevents one bad file from crashing entire process
```

---

#### Add Metadata Columns

```python
        # Add metadata columns
        df['goal_number'] = goal_number
        df['goal_name'] = self.sdg_goals[goal_number]
        df['source_file'] = Path(file_path).name
        
        return df
```

**Adding columns to DataFrame:**

```python
# Original data from Goal1.xlsx:
df = 
| Year | Indicator    | Value |
|------|--------------|-------|
| 2020 | Poverty Rate | 23.5  |

# After adding metadata:
df['goal_number'] = 1
df['goal_name'] = "No Poverty"
df['source_file'] = "Goal1.xlsx"

# Result:
| Year | Indicator    | Value | goal_number | goal_name   | source_file |
|------|--------------|-------|-------------|-------------|-------------|
| 2020 | Poverty Rate | 23.5  | 1           | No Poverty  | Goal1.xlsx  |
```

**Why add metadata?**

```python
# When all 17 files are combined:

# Without metadata:
# Which goal does this indicator belong to? ❌
# Can't filter by goal ❌

# With metadata:
SELECT * FROM sdg_indicators WHERE goal_number = 1
# ✅ Get only Goal 1 (No Poverty) indicators
SELECT * FROM sdg_indicators WHERE goal_name LIKE '%Health%'
# ✅ Get all health-related indicators
```

**`Path(file_path).name`:**
```python
file_path = "data/raw/un_sdg_excel/Goal1.xlsx"

Path(file_path).name
# → "Goal1.xlsx"

# Extracts just filename (removes directory path)
```

---

### Column Normalization

Critical for consistent SQL queries!

```python
def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names
    
    Converts various naming conventions to standard format
    """
```

**Why normalize column names?**

```python
# Excel files might have inconsistent naming:
Goal1.xlsx:  "Poverty Rate (%)"
Goal2.xlsx:  "poverty-rate"
Goal3.xlsx:  "Poverty_Rate"
Goal4.xlsx:  "POVERTY RATE"

# After normalization:
All files: "poverty_rate"

# Benefits:
# ✅ Consistent SQL queries
# ✅ No case sensitivity issues
# ✅ No special character problems
```

---

#### Create Column Mapping

```python
    # Create column name mapping
    column_mapping = {}
    
    for col in df.columns:
```

**Loop through all columns:**
```python
df.columns = ['Poverty Rate (%)', 'Year', 'Value']

for col in df.columns:
    # col = 'Poverty Rate (%)'
    # col = 'Year'
    # col = 'Value'
```

---

#### Normalization Steps

```python
        # Convert to lowercase and replace spaces/special chars with underscore
        normalized = col.lower().strip()
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', '_', normalized)
        column_mapping[col] = normalized
```

**Step-by-step transformation:**

```python
# Step 1: Original
col = "Poverty Rate (%)"

# Step 2: Lowercase
normalized = col.lower()
# → "poverty rate (%)"

# Step 3: Remove leading/trailing spaces
normalized = normalized.strip()
# → "poverty rate (%)"  (no change if no extra spaces)

# Step 4: Remove special characters
normalized = re.sub(r'[^\w\s]', '', normalized)
# → "poverty rate "  (removed parentheses and %)

# Step 5: Replace spaces with underscores
normalized = re.sub(r'\s+', '_', normalized)
# → "poverty_rate_"

# Final result: "poverty_rate_"
```

**Regex patterns explained:**

```python
# Pattern 1: r'[^\w\s]'
[^...]  # NOT matching
\w      # Word characters (a-z, A-Z, 0-9, _)
\s      # Whitespace (spaces, tabs)
# Matches: Any character that's NOT alphanumeric or space
# Example: "(%)" → matches "(" ")" "%"

# Pattern 2: r'\s+'
\s+     # One or more whitespace characters
# Matches: "  " (multiple spaces), "\t" (tabs)
# Replaces with: "_"
```

**Example transformations:**

```python
"Poverty Rate (%)"  → "poverty_rate"
"GDP per Capita"    → "gdp_per_capita"
"POPULATION-2020"   → "population_2020"
"Health Score"      → "health_score"
```

---

#### Apply Column Mapping

```python
    df = df.rename(columns=column_mapping)
    
    return df
```

**`df.rename()`:**
```python
# Before:
df.columns = ['Poverty Rate (%)', 'Year', 'Value']

column_mapping = {
    'Poverty Rate (%)': 'poverty_rate',
    'Year': 'year',
    'Value': 'value'
}

# Apply:
df = df.rename(columns=column_mapping)

# After:
df.columns = ['poverty_rate', 'year', 'value']
```

---

### Processing All Excel Files

```python
def process_all_excel_files(self, folder_path: str) -> pd.DataFrame:
    """
    Process all 17 UN SDG Excel files
    
    Args:
        folder_path: Path to folder containing Goal1.xlsx through Goal17.xlsx
        
    Returns:
        Combined DataFrame with all SDG data
    """
```

---

#### Find Excel Files

```python
    excel_files = sorted(Path(folder_path).glob("Goal*.xlsx"))
```

**`glob()` pattern matching:**

```python
Path("data/raw/un_sdg_excel").glob("Goal*.xlsx")

# Pattern: Goal*.xlsx
# Matches:
# ✅ Goal1.xlsx
# ✅ Goal2.xlsx
# ✅ Goal17.xlsx
# ✅ Goal123.xlsx

# Doesn't match:
# ❌ goal1.xlsx (lowercase)
# ❌ SDG1.xlsx (different prefix)
# ❌ Goal1.xls (wrong extension)
```

**`sorted()`:**
```python
# Without sorting:
files = ['Goal2.xlsx', 'Goal17.xlsx', 'Goal1.xlsx']

# With sorting:
files = sorted(files)
# → ['Goal1.xlsx', 'Goal2.xlsx', 'Goal17.xlsx']

# Ensures consistent processing order
```

---

#### Process Each File

```python
    all_data = []
    
    for file_path in tqdm(excel_files, desc="Loading Excel files"):
        # Extract goal number from filename (Goal1.xlsx -> 1)
        filename = file_path.stem  # Gets 'Goal1' from 'Goal1.xlsx'
        goal_number = int(re.search(r'\d+', filename).group())
```

**`.stem` property:**
```python
file_path = Path("data/raw/un_sdg_excel/Goal5.xlsx")

file_path.name  # → "Goal5.xlsx"
file_path.stem  # → "Goal5"  (filename without extension)
file_path.suffix  # → ".xlsx"  (extension only)
```

**Extract number from filename:**
```python
filename = "Goal5"

# Regex: r'\d+'
\d+  # One or more digits

# Search:
match = re.search(r'\d+', filename)
# Finds: "5"

match.group()  # Returns matched string: "5"
int(match.group())  # Convert to integer: 5
```

**Example for all goals:**
```python
"Goal1"   → 1
"Goal5"   → 5
"Goal17"  → 17
```

---

#### Load and Normalize

```python
        # Load Excel file
        df = self.load_excel_file(str(file_path), goal_number)
        
        if not df.empty:
            # Normalize column names
            df = self.normalize_columns(df)
            all_data.append(df)
```

**Check if DataFrame is empty:**
```python
if not df.empty:
    # Process only if data was loaded successfully
    # Skips files that had errors
```

**Accumulate data:**
```python
all_data = []

# File 1:
all_data.append(df1)  # [df1]

# File 2:
all_data.append(df2)  # [df1, df2]

# File 17:
all_data.append(df17)  # [df1, df2, ..., df17]
```

---

#### Combine All Data

```python
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    
    print(f"✅ Loaded {len(combined_df)} rows from {len(excel_files)} files")
    
    return combined_df
```

**`pd.concat()`:**

```python
# Before:
df1 = | year | indicator | value | goal_number |
      | 2020 | Poverty   | 23.5  | 1           |

df2 = | year | indicator | value | goal_number |
      | 2020 | Hunger    | 15.2  | 2           |

# After concat:
combined = pd.concat([df1, df2], ignore_index=True)

| year | indicator | value | goal_number |
| 2020 | Poverty   | 23.5  | 1           |
| 2020 | Hunger    | 15.2  | 2           |
```

**`ignore_index=True`:**
```python
# Without ignore_index:
Index: [0, 1, 2, 0, 1, 2, 0, 1...]  # Duplicate indexes! ❌

# With ignore_index=True:
Index: [0, 1, 2, 3, 4, 5, 6, 7...]  # Sequential! ✅
```

---

### Creating SQL Tables

```python
def create_tables(self, df: pd.DataFrame):
    """
    Create SQL tables from DataFrame
    
    Args:
        df: Combined SDG data
    """
```

---

#### Main Data Table

```python
    # Main SDG data table
    df.to_sql('sdg_indicators', self.conn, if_exists='replace', index=False)
    print(f"✅ Created table: sdg_indicators ({len(df)} rows)")
```

**`df.to_sql()`:**

```python
# Converts DataFrame → SQL table

df.to_sql(
    'sdg_indicators',    # Table name
    self.conn,           # Database connection
    if_exists='replace', # What to do if table exists
    index=False          # Don't save DataFrame index as column
)
```

**`if_exists` options:**

```python
if_exists='replace'
# Table exists? Drop it and create new one
# Use when rebuilding database

if_exists='append'
# Table exists? Add rows to existing table
# Use when adding new data

if_exists='fail'
# Table exists? Raise error
# Use when table shouldn't exist yet
```

**`index=False`:**
```python
# DataFrame has index (row numbers):
Index | year | indicator | value
0     | 2020 | Poverty   | 23.5
1     | 2021 | Poverty   | 22.1

# With index=True:
CREATE TABLE sdg_indicators (
    index INTEGER,      ← Added (don't want this)
    year INTEGER,
    indicator TEXT,
    value REAL
)

# With index=False:
CREATE TABLE sdg_indicators (
    year INTEGER,       ← Clean!
    indicator TEXT,
    value REAL
)
```

---

#### Reference Table

```python
    # Create SDG goals reference table
    goals_df = pd.DataFrame([
        {'goal_number': num, 'goal_name': name}
        for num, name in self.sdg_goals.items()
    ])
    goals_df.to_sql('sdg_goals', self.conn, if_exists='replace', index=False)
```

**List comprehension:**
```python
self.sdg_goals = {1: "No Poverty", 2: "Zero Hunger", ...}

goals_df = pd.DataFrame([
    {'goal_number': 1, 'goal_name': "No Poverty"},
    {'goal_number': 2, 'goal_name': "Zero Hunger"},
    ...
])

# Result:
| goal_number | goal_name     |
|-------------|---------------|
| 1           | No Poverty    |
| 2           | Zero Hunger   |
| ...         | ...           |
```

**Why separate table?**

```python
# Relational database design:

# Table 1: sdg_goals (reference)
| goal_number | goal_name     |
|-------------|---------------|
| 1           | No Poverty    |

# Table 2: sdg_indicators (data)
| year | value | goal_number |
|------|-------|-------------|
| 2020 | 23.5  | 1           |

# Join when needed:
SELECT i.year, i.value, g.goal_name
FROM sdg_indicators i
JOIN sdg_goals g ON i.goal_number = g.goal_number

# Benefits:
# ✅ No data duplication
# ✅ Can update goal names in one place
# ✅ Smaller database size
```

---

#### Create Indexes

```python
    # Create indexes for faster queries
    cursor = self.conn.cursor()
    
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_goal_number ON sdg_indicators(goal_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_year ON sdg_indicators(year)") if 'year' in df.columns else None
        self.conn.commit()
        print("✅ Created indexes")
    except Exception as e:
        print(f"⚠️  Index creation: {str(e)}")
```

**What is an index?**

Like a book's index - helps find information quickly!

```python
# Without index:
SELECT * FROM sdg_indicators WHERE goal_number = 5
# → Scans all 10,000 rows (slow!) ❌

# With index:
CREATE INDEX idx_goal_number ON sdg_indicators(goal_number)
SELECT * FROM sdg_indicators WHERE goal_number = 5
# → Jumps directly to goal 5 rows (fast!) ✅
```

**Index performance:**

| Operation | Without Index | With Index |
|-----------|---------------|------------|
| Find by goal | 100ms | 5ms |
| Find by year | 80ms | 3ms |
| Insert row | 1ms | 2ms (slightly slower) |

**When to index:**

```python
# Index columns that are:
✅ Frequently used in WHERE clauses
✅ Frequently used in JOIN conditions
✅ Used in ORDER BY

# Don't index:
❌ Columns with few unique values (e.g., boolean)
❌ Small tables (< 1000 rows)
❌ Columns rarely queried
```

**`IF NOT EXISTS`:**
```python
# Without IF NOT EXISTS:
CREATE INDEX idx_goal_number ...
# If index exists: Error! ❌

# With IF NOT EXISTS:
CREATE INDEX IF NOT EXISTS idx_goal_number ...
# If index exists: Do nothing ✅
# If index missing: Create it ✅
```

---

## 🎓 Key Takeaways

### 1. **Excel → SQL enables powerful queries**
```python
# Excel: Manual searching
# SQL: Millisecond queries with complex conditions
```

### 2. **Normalization ensures consistency**
```python
# Standardized column names
# No case sensitivity issues
# Clean, predictable schema
```

### 3. **Metadata enables filtering**
```python
# goal_number, goal_name, source_file
# Can filter and organize data
```

### 4. **Indexing speeds up queries**
```python
# 20x faster queries
# Essential for production systems
```

### 5. **Pandas + SQLite = Perfect combo**
```python
# Pandas: Data processing
# SQLite: Fast, structured queries
# Together: Powerful data pipeline
```

---

**Continue to next document: Streamlit app interface...**

This comprehensive guide covers Excel to SQL conversion in depth!

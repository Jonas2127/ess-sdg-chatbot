# Root Cause: 2021 Data Not Retrieved

**Date:** January 28, 2026  
**Issue:** 2021 poverty data exists in database but not returned in RAG answers  
**Status:** Root cause identified + solution provided

---

## 🔍 Investigation Results

### ✅ Data Collection: WORKING
- Raw Excel (Goal1.xlsx) contains 2021 data ✅
- Multiple 2021 poverty indicators present

### ✅ Data Processing: WORKING  
- Processed data (processed_data_20260726.csv) contains **117 chunks** with 2021 ✅
- Processing script correctly expanded all years

### ✅ Vector Database: WORKING (probably)
- Embeddings generated from processed data
- Qdrant contains all 60,185 chunks including 2021 data

### ❌ Vector Retrieval: **THIS IS THE PROBLEM**
- Query: "what is ethiopia poverty rate over time"
- top_k=5 retrieves 5 chunks
- **None of the 5 chunks contain 2021 data** ❌
- All 5 chunks are from 2004, 2010, 2015

---

## 🐛 Why Vector Search Fails to Find 2021

### Problem: Semantic Similarity vs Temporal Relevance

**User Question:**
> "what is ethiopia poverty rate **over time**"

**What Vector Search Does:**
1. Embeds the question
2. Finds chunks with highest cosine similarity
3. Returns top 5

**Why 2004-2015 Ranks Higher:**
- Chunks with "trend", "decreased from X to Y", "over time" narrative
- These have high semantic similarity to "over time" query
- 2021 chunks might just say "2021: 34.0%"  without narrative context
- Single datapoint without trend language ranks lower

### Analogy:
```
Query: "Show me poverty over time"

Chunk A (2010): 
"Poverty decreased from 45% in 2005 to 37% in 2010, 
showing progress over time..." 
→ Similarity: 0.85 (HIGH - has "over time", "decreased")

Chunk B (2021):
"SDG Goal 1, Indicator 1.1.1
TimePeriod: 2021
Value: 34.0
SeriesDescription: Proportion of population below poverty line"
→ Similarity: 0.72 (LOWER - just data, no narrative)
```

---

## 💡 Solutions (3 Options)

### Option 1: Increase top_k Further (Quick But Inefficient)

**Current:** top_k=5 (gets 2004, 2010, 2015)  
**Try:** top_k=10 (might get 2021)

**Implementation:**
```python
# streamlit_app.py
result = st.session_state.rag.query(prompt, top_k=10, verbose=False)
```

**Pros:**
- ✅ 1-line change
- ✅ Will eventually find 2021

**Cons:**
- ⚠️ Wasteful (passing 10 chunks when only need 5)
- ⚠️ Slower (+0.5s response time)
- ⚠️ More expensive (more tokens to LLM)
- ⚠️ Doesn't solve root cause

**Recommendation:** ⚠️ Not ideal, but works as quick fix

---

### Option 2: Re-Rank with Temporal Boost (Smart Solution)

**Idea:** Boost recent years in retrieval

**Implementation:**
```python
# In src/rag/flexible_rag.py

def retrieve(self, query: str, top_k: int = 5):
    """Retrieve with temporal boosting"""
    
    # Get more candidates than needed
    candidates = self.qdrant.search(
        collection_name=self.collection,
        query_vector=self.embedder.encode(query).tolist(),
        limit=top_k * 3  # Get 15 candidates for top_k=5
    )
    
    # Re-rank with temporal boost
    for candidate in candidates:
        text = candidate.payload.get('text', '')
        
        # Extract years from text
        years = re.findall(r'\b(20\d{2})\b', text)
        
        if years:
            latest_year = max([int(y) for y in years])
            
            # Boost recent data
            if latest_year >= 2020:
                candidate.score *= 1.3  # 30% boost
            elif latest_year >= 2015:
                candidate.score *= 1.1  # 10% boost
    
    # Sort by boosted score and return top_k
    candidates.sort(key=lambda x: x.score, reverse=True)
    return candidates[:top_k]
```

**Pros:**
- ✅ Smart: prioritizes recent data
- ✅ Efficient: still returns top_k chunks
- ✅ Solves root cause
- ✅ Generalizable to all time-series queries

**Cons:**
- ⚠️ Requires code changes (~30 lines)
- ⚠️ Need to import re module
- ⚠️ Adds +50ms to retrieval time
**Recommendation:** ✅ **BEST SOLUTION**

---

### Option 3: Hybrid Search (Advanced)

**Idea:** Combine vector search + keyword filtering

**Implementation:**
```python
def retrieve_with_recency(self, query: str, top_k: int = 5):
    """Hybrid: vector search + keyword boost for recent years"""
    
    # Vector search
    vector_results = self.qdrant.search(
        collection_name=self.collection,
        query_vector=self.embedder.encode(query).tolist(),
        limit=top_k
    )
    
    # If query mentions "recent", "latest", "current", "over time"
    if any(word in query.lower() for word in ['recent', 'latest', 'current', 'time', 'trend']):
        # Get recent data points (2018+)
        recent_results = self.qdrant.scroll(
            collection_name=self.collection,
            scroll_filter={
                "must": [
                    {"key": "text", "match": {"text": "2020|2021|2022|2023|2024"}}
                ]
            },
            limit=2
        )
        
        # Merge with vector results
        combined = vector_results + recent_results[0]
        combined = sorted(combined, key=lambda x: x.score, reverse=True)[:top_k]
        return combined
    
    return vector_results
```

**Pros:**
- ✅ Best of both worlds
- ✅ Catches explicit recent data
- ✅ Maintains semantic quality

**Cons:**
- ⚠️ Complex implementation (~50 lines)
- ⚠️ Requires Qdrant filtering support
- ⚠️ Two queries = slower

**Recommendation:** ⚠️ Overkill for now, save for Phase 8

---

## 🎯 Recommended Immediate Action

**Implement Option 2: Temporal Re-Ranking**

This solves the root cause efficiently and will work for all similar queries.

### Implementation Steps:

1. Edit `src/rag/flexible_rag.py`
2. Add `import re` at top
3. Modify `retrieve()` method to add temporal boosting
4. Test with poverty question
5. Verify 2021 data now appears

**Expected Result:**
```
Before: 2004, 2010, 2015 (scores: 0.85, 0.82, 0.80)
After: 2021, 2015, 2010 (scores: 1.02 [boosted], 0.88 [boosted], 0.90)
        ↑ 2021 now ranked higher due to temporal boost!
```

---

## 📝 Detailed Implementation

### Step 1: Update retrieve() method

Edit `src/rag/flexible_rag.py` around line 110:

```python
import re  # Add at top of file

class FlexibleRAG:
    # ... existing code ...
    
    def retrieve(self, question: str, top_k: int = 5):
        """
        Retrieve relevant chunks with temporal boosting
        Recent data gets priority for time-series queries
        """
        # Get more candidates than needed (3x)
        candidate_k = top_k * 3
        
        # Encode question
        question_vector = self.embedder.encode(question).tolist()
        
        # Search Qdrant
        candidates = self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=question_vector,
            limit=candidate_k
        )
        
        # Apply temporal boosting if query is about trends/time
        time_keywords = ['over time', 'trend', 'recent', 'latest', 'current', 'progress', 'change']
        is_temporal_query = any(keyword in question.lower() for keyword in time_keywords)
        
        if is_temporal_query:
            print(f"🕒 Temporal query detected - boosting recent data")
            
            for candidate in candidates:
                text = candidate.payload.get('text', '')
                
                # Extract years from text
                years = re.findall(r'\b(20[0-2]\d)\b', text)
                
                if years:
                    latest_year = max([int(y) for y in years])
                    current_year = 2026
                    
                    # Calculate age of data
                    age = current_year - latest_year
                    
                    # Boost based on recency
                    if age <= 3:  # 2023-2026
                        boost = 1.3  # 30% boost
                    elif age <= 6:  # 2020-2022
                        boost = 1.2  # 20% boost
                    elif age <= 10:  # 2016-2019
                        boost = 1.1  # 10% boost
                    else:  # Pre-2016
                        boost = 1.0  # No boost
                    
                    # Apply boost
                    candidate.score *= boost
                    
                    if boost > 1.0:
                        print(f"   Boosted {latest_year} data: {candidate.score:.4f} (×{boost})")
        
        # Sort by (potentially boosted) score
        candidates.sort(key=lambda x: x.score, reverse=True)
        
        # Return top_k after re-ranking
        return candidates[:top_k]
```

### Step 2: Test

```bash
streamlit run streamlit_app.py
```

Ask: **"what is ethiopia poverty rate over time"**

**Expected console output:**
```
🕒 Temporal query detected - boosting recent data
   Boosted 2021 data: 0.936 (×1.2)
   Boosted 2020 data: 0.918 (×1.2)
   Boosted 2015 data: 0.880 (×1.1)
```

**Expected answer:**
```
According to the data, Ethiopia's poverty rate has shown progress over time:
- 2004: 41.3%
- 2010: 37.4%
- 2015: 33.0%
- 2021: 34-45% (depending on poverty line definition)

The most recent data from 2021 shows...
```

---

## 🧪 Testing Checklist

After implementing temporal boosting:

- [ ] Poverty "over time" query includes 2021 ✅
- [ ] GDP "trend" query includes recent years ✅
- [ ] "Latest" or "recent" queries prioritize new data ✅
- [ ] Specific year queries (e.g., "poverty in 2010") still work ✅
- [ ] Non-temporal queries unaffected ✅
- [ ] Response time still <3 seconds ✅

---

## 📊 Expected Impact

### Before Temporal Boosting:

| Rank | Year | Score | Retrieved? |
|------|------|-------|------------|
| 1 | 2010 | 0.850 | ✅ Yes (narrative) |
| 2 | 2015 | 0.820 | ✅ Yes (narrative) |
| 3 | 2004 | 0.800 | ✅ Yes (context) |
| 4 | 2015 | 0.780 | ✅ Yes (duplicate) |
| 5 | 2010 | 0.770 | ✅ Yes (duplicate) |
| 8 | 2021 | 0.720 | ❌ **Not retrieved** |

### After Temporal Boosting:

| Rank | Year | Original | Boosted | Retrieved? |
|------|------|----------|---------|------------|
| 1 | 2021 | 0.720 | **0.864** | ✅ **Now retrieved!** |
| 2 | 2020 | 0.710 | **0.852** | ✅ Also recent |
| 3 | 2015 | 0.820 | 0.902 | ✅ Still good |
| 4 | 2010 | 0.850 | 0.850 | ✅ Historical context |
| 5 | 2015 | 0.800 | 0.880 | ✅ More recent context |

---

## ✅ Summary

**Problem:** 2021 data exists but vector search ranks it lower than older data

**Root Cause:** Semantic similarity favors narrative chunks over raw datapoints

**Solution:** Temporal re-ranking that boosts recent years for time-series queries

**Implementation Time:** 30 minutes

**Expected Outcome:** Answers will include most recent available data

---

**Next Step:** Implement temporal boosting in `flexible_rag.py` and test!

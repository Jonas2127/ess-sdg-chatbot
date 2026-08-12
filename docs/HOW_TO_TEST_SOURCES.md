# How to Test the Source Attribution Fix

## 🚀 Quick Start

### Step 1: Start Streamlit
```bash
streamlit run streamlit_app.py
```

### Step 2: Ask a Question
Try one of these questions that should use the AfDB document:

- **"Tell me about Ethiopia's green growth strategy"**
- **"What is the CRGE strategy?"**
- **"What does AfDB report say about Ethiopia?"**

### Step 3: Click the Sources Button
After the answer appears, click the **"📚 Sources"** button at the bottom

### Step 4: Verify the Display

## ✅ What You Should See

### Before the Fix (OLD BEHAVIOR)
```
📚 Sources (5 documents)
  📄 Source 1: ESS - file_12345.pdf
  📄 Source 2: ESS - file_67890.pdf
  📄 Source 3: ESS - file_abcde.pdf
  ...
  [No download button]
```

### After the Fix (NEW BEHAVIOR)
```
📚 Sources

📄 Source 1: AfDB - ETHIOPIA_CSP_BPPS_EN.pdf (2 chunks)
  ▼ Click to expand
    [Content preview shown here...]
    
    📥 Download AfDB PDF    <-- DOWNLOAD BUTTON
    
📄 Source 2: ESS - national-area-production.pdf (1 chunk)
  ▼ Click to expand
    [Content preview shown here...]
    
    📥 Download ESS PDF     <-- DOWNLOAD BUTTON
    
📄 Source 3: ESS - 2.2014_E.C-COMMERCIAL-FARM-REPORT_FINAL.pdf (1 chunk)
  ▼ Click to expand
    [Content preview shown here...]
    
    📥 Download ESS PDF     <-- DOWNLOAD BUTTON
```

## 🎯 Key Improvements

| Feature | Before | After |
|---------|--------|-------|
| **Source Type** | Always "ESS" | Correctly shows "AfDB" or "ESS" |
| **Grouping** | Individual chunks | Grouped by PDF file |
| **Download** | ❌ No button | ✅ Download button for each PDF |
| **Chunk Count** | Not shown | Shows "(X chunks)" |
| **PDF Path** | Not shown | Shown if file not found |

## 🧪 Test Cases

### Test Case 1: AfDB Query
**Query:** "Tell me about Ethiopia's green growth strategy"

**Expected Result:**
- Answer mentions "CRGE Strategy" or "Climate-Resilient Green Economy"
- Sources show **"AfDB"** as source type
- Sources include **"ETHIOPIA_CSP_BPPS_EN.pdf"**
- Download button works

### Test Case 2: ESS Query
**Query:** "What is ESS?"

**Expected Result:**
- Answer explains Ethiopian Statistical Service
- Sources show **"ESS"** as source type
- Sources include ESS reports
- Download button works

### Test Case 3: Mixed Query
**Query:** "Tell me about Ethiopia's poverty and green growth"

**Expected Result:**
- Answer combines information from multiple sources
- Sources show **both "AfDB" and "ESS"** types
- Multiple PDFs listed with correct types
- All download buttons work

## 📥 Testing the Download Button

1. Click **"📥 Download AfDB PDF"** or **"📥 Download ESS PDF"**
2. Browser should download the PDF file
3. Check your Downloads folder
4. Open the PDF to verify it's the correct file

### If Download Fails
The system will show:
```
⚠️ PDF file not found at: data\raw\afdb_reports\ETHIOPIA_CSP_BPPS_EN.pdf
```

This means the PDF path is incorrect or the file is missing.

## 🔍 How to Verify Source Attribution is Working

### Method 1: Visual Check (Quick)
1. Ask the question
2. Check if sources show "AfDB" or "ESS" correctly
3. Verify filename matches the document type

### Method 2: Run Test Script (Detailed)
```bash
python test_sources.py
```

This will show:
- Query: "Tell me about Ethiopia's green growth strategy"
- Answer (should mention CRGE)
- All 5 sources with metadata
- Summary: "✅ SUCCESS: AfDB document IS being used!"

## 🐛 Common Issues

### Issue 1: Still Shows "ESS" for AfDB
**Solution:** Hard refresh browser
- Windows: `Ctrl + F5` or `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

### Issue 2: No Download Button Appears
**Solution:** Check PDF file exists
```bash
dir data\raw\afdb_reports\ETHIOPIA_CSP_BPPS_EN.pdf
```

### Issue 3: "Unknown" Source Type
**Solution:** ChromaDB metadata issue - rebuild vector store
```bash
python build_dual_engine.py
```

### Issue 4: No Sources Shown at All
**Solution:** Check query type - might be using SQL engine only
- Try questions about "ESS", "report", "policy", "strategy"
- Avoid pure numerical questions

## 📊 Expected Behavior Summary

| Question Type | Engines Used | Sources Shown | Source Types |
|--------------|--------------|---------------|--------------|
| "What is ESS?" | PDF only | 5 | ESS |
| "Green growth strategy" | PDF only | 5 | AfDB + ESS |
| "Poverty rate 2021" | SQL + PDF | 5 | ESS (if any) |
| "What is poverty?" | Both | 5 | ESS + AfDB (if relevant) |

## ✅ Success Checklist

- [ ] Sources button appears under answers
- [ ] Clicking shows expandable source list
- [ ] Source type correctly shows "AfDB" or "ESS"
- [ ] Filename is accurate
- [ ] Chunk count is shown
- [ ] Download button appears for each source
- [ ] Download button works
- [ ] Content preview is shown
- [ ] AfDB queries use AfDB document

---

**Ready to test?** Run `streamlit run streamlit_app.py` and follow the steps above!

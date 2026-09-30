# Utility Scripts Guide

This document describes the utility scripts for maintaining and updating the ESS SDG Chatbot database.

---

## Overview

Two essential utility scripts are provided for database maintenance:

1. **`download_pdf_files.py`** - Downloads PDF files from HuggingFace
2. **`add_new_pdfs.py`** - Processes new PDFs and adds them to ChromaDB

---

## download_pdf_files.py

### Purpose
Downloads PDF files from the HuggingFace repository to your local machine.

### When to Use
- Setting up the system on a new machine
- Restoring PDFs if local files are lost
- Syncing with the latest PDF collection from HuggingFace

### Prerequisites
```bash
pip install huggingface-hub tqdm
```

### Usage
```bash
python download_pdf_files.py
```

### What It Does
1. Connects to HuggingFace repository: `Mikigithub/ess-ethiopia-sdg-data`
2. Lists all PDF files in the repository
3. Downloads PDFs to `data/raw/ess_reports/pdfs/`
4. Skips files that already exist locally
5. Shows progress bar and summary

### Output
```
[INFO] Starting PDF download from HuggingFace
============================================================
Repository: Mikigithub/ess-ethiopia-sdg-data
Local directory: data/raw/ess_reports/pdfs

[INFO] Fetching repository file list...
[OK] Found 222 PDF files

Downloading PDFs: 100%|████████████████| 222/222 [05:30<00:00, 1.49s/it]

============================================================
[OK] Download process complete!

Summary:
  Downloaded: 50
  Skipped (already exists): 172
  Failed: 0
  Total PDFs: 222

Next steps:
1. Run 'python add_new_pdfs.py' to add new PDFs to ChromaDB
2. Or run 'python build_dual_engine.py' to rebuild entire database
```

### Customization
You can modify the script to use a different repository:

```python
download_pdfs_from_huggingface(
    repo_id="your-username/your-repo",
    local_dir="data/raw/ess_reports/pdfs"
)
```

---

## add_new_pdfs.py

### Purpose
Processes new PDF files and adds them to the existing ChromaDB vector store without rebuilding the entire database.

### When to Use
- After downloading new PDFs from HuggingFace
- When you manually add new ESS reports to the PDF directory
- When you want to update the database incrementally

### Prerequisites
The system must be already set up with ChromaDB. If starting fresh, use `build_dual_engine.py` instead.

### Usage
```bash
python add_new_pdfs.py
```

### What It Does
1. Scans `data/raw/ess_reports/pdfs/` for all PDF files
2. Checks which PDFs are already in ChromaDB
3. Identifies new PDFs that need processing
4. Extracts text and creates chunks from new PDFs
5. Adds new chunks to the existing ChromaDB vector store
6. Shows statistics about the updated database

### Output
```
[INFO] Starting PDF addition process
============================================================
[INFO] Found 225 PDF files in directory
[INFO] Found 222 PDFs already in database

[INFO] Found 3 new PDFs to process:
  - CPI_JAN_2023.pdf
  - LABOR_FORCE_2023.pdf
  - INFLATION_REPORT_2023.pdf

[INFO] Processing 3 new PDFs...
------------------------------------------------------------

[1/3] Processing: CPI_JAN_2023.pdf
[OK] Extracted 45 chunks from CPI_JAN_2023.pdf

[2/3] Processing: LABOR_FORCE_2023.pdf
[OK] Extracted 67 chunks from LABOR_FORCE_2023.pdf

[3/3] Processing: INFLATION_REPORT_2023.pdf
[OK] Extracted 52 chunks from INFLATION_REPORT_2023.pdf

[INFO] Adding 164 new chunks to ChromaDB...
[OK] Successfully added 164 chunks to the database
[INFO] Total chunks in database: 12,847

============================================================
[OK] PDF addition process complete!

Next steps:
1. Test the system with queries related to the new PDFs
2. Verify sources are displayed correctly in responses
```

### Important Notes

- **Incremental Updates**: This script only processes new PDFs, making it much faster than rebuilding the entire database
- **No Duplicates**: The script checks existing PDFs to avoid duplicates
- **Preserves Existing Data**: All existing chunks in ChromaDB remain unchanged
- **Automatic Detection**: No need to specify which PDFs are new - the script figures it out

---

## Common Workflows

### Workflow 1: Adding New ESS Reports

When ESS publishes new reports:

```bash
# Step 1: Place new PDF files in the directory
# Copy PDFs to: data/raw/ess_reports/pdfs/

# Step 2: Process and add to database
python add_new_pdfs.py

# Step 3: Test with relevant queries
streamlit run streamlit_app.py
```

### Workflow 2: Syncing with HuggingFace

When the HuggingFace repository is updated:

```bash
# Step 1: Download new PDFs
python download_pdf_files.py

# Step 2: Add new PDFs to database
python add_new_pdfs.py

# Step 3: Test the system
streamlit run streamlit_app.py
```

### Workflow 3: Fresh Installation

On a new machine:

```bash
# Step 1: Clone repository
git clone https://github.com/your-repo/ess-sdg-chatbot.git
cd ess-sdg-chatbot

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Download PDFs
python download_pdf_files.py

# Step 4: Build entire database (first time)
python build_dual_engine.py

# Step 5: Run application
streamlit run streamlit_app.py
```

### Workflow 4: Rebuilding Database

If you need to completely rebuild the database:

```bash
# Delete existing ChromaDB
rm -rf chroma_db_ethiopian_sdg/

# Rebuild from scratch (processes all PDFs)
python build_dual_engine.py
```

---

## Troubleshooting

### download_pdf_files.py Issues

**Problem**: `ModuleNotFoundError: No module named 'huggingface_hub'`

**Solution**:
```bash
pip install huggingface-hub
```

**Problem**: Connection timeout or network errors

**Solutions**:
- Check your internet connection
- Try again later (HuggingFace might be experiencing issues)
- Use a VPN if HuggingFace is blocked in your region

**Problem**: Repository not found

**Solution**:
- Verify the repository ID in the script
- Check if the repository is public
- Ensure you have access permissions

### add_new_pdfs.py Issues

**Problem**: `ChromaDB not found` or similar database errors

**Solution**:
- Ensure you've built the database first: `python build_dual_engine.py`
- Check that `chroma_db_ethiopian_sdg/` directory exists

**Problem**: No new PDFs detected but you added files

**Solutions**:
- Verify PDFs are in `data/raw/ess_reports/pdfs/` directory
- Check file extensions are `.pdf` (lowercase)
- Ensure PDFs aren't corrupted (try opening them)

**Problem**: PDF processing fails for specific files

**Solutions**:
- Check if the PDF is encrypted or password-protected
- Verify the PDF isn't corrupted
- Try opening the PDF in a PDF reader
- Check file permissions

---

## Performance Considerations

### download_pdf_files.py
- **Time**: ~5-10 minutes for 200+ PDFs (depending on internet speed)
- **Bandwidth**: ~500MB-1GB total download size
- **Disk Space**: Requires ~1GB free space

### add_new_pdfs.py
- **Time**: ~30 seconds per PDF (varies by PDF size and content)
- **Memory**: ~2-4GB RAM during processing
- **Disk Space**: ChromaDB grows by ~5-10MB per PDF added

---

## Best Practices

1. **Regular Updates**: Run `download_pdf_files.py` monthly to check for new reports

2. **Incremental Addition**: Use `add_new_pdfs.py` instead of rebuilding the entire database when possible

3. **Backup**: Before major updates, backup your `chroma_db_ethiopian_sdg/` directory

4. **Testing**: After adding new PDFs, test with queries related to the new content

5. **Monitoring**: Keep track of database size and performance as it grows

6. **Version Control**: Don't commit PDF files or ChromaDB to git (they're in `.gitignore`)

---

## Technical Details

### PDF Processing Pipeline

```
PDF File
  ↓
Text Extraction (PyMuPDF)
  ↓
Text Cleaning (remove headers/footers)
  ↓
Smart Chunking (500-800 words)
  ↓
Metadata Addition (source, page, date)
  ↓
Embedding Generation (sentence-transformers)
  ↓
ChromaDB Storage
```

### Chunk Metadata Structure

Each chunk stored in ChromaDB includes:

```python
{
    "source": "CPI_JAN_2023.pdf",
    "page": 5,
    "chunk_index": 12,
    "total_chunks": 45,
    "file_type": "pdf",
    "processing_date": "2024-01-15"
}
```

### ChromaDB Collection Details

- **Collection Name**: `ess_ethiopian_sdg`
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Embedding Dimension**: 384
- **Distance Metric**: Cosine similarity

---

## Future Enhancements

Possible improvements to these utilities:

1. **Parallel Processing**: Process multiple PDFs simultaneously
2. **Progress Persistence**: Resume interrupted downloads/processing
3. **Duplicate Detection**: Check for duplicate content, not just filenames
4. **Automatic Scheduling**: Cron job for automatic updates
5. **Diff Reports**: Generate reports showing what changed
6. **PDF Validation**: Pre-check PDF quality before processing

---

## Support

If you encounter issues with these utilities:

1. Check the console output for specific error messages
2. Review the troubleshooting section above
3. Verify all prerequisites are installed
4. Check file permissions and disk space
5. Consult `docs/ARCHITECTURE.md` for system design details

---

## Summary

These utilities provide essential maintenance capabilities:

- **download_pdf_files.py**: Sync PDFs from HuggingFace
- **add_new_pdfs.py**: Incrementally update ChromaDB

Use them regularly to keep your ESS SDG Chatbot database up-to-date with the latest reports and data.

"""
Add New PDFs to ChromaDB Vector Store
======================================
Utility script to process and add new PDF files to the existing ChromaDB vector store.

Usage:
    python add_new_pdfs.py
    
The script will:
1. Scan data/raw/ess_reports/pdfs/ for new PDFs
2. Check which PDFs are already in the database
3. Process only new PDFs
4. Add them to the ChromaDB vector store
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.engine_a_pdf_rag.pdf_processor import ESS_PDFProcessor
from src.engine_a_pdf_rag.chromadb_vectorstore import ChromaDBManager


def main():
    """Main function to add new PDFs to the vector store."""
    
    print("[INFO] Starting PDF addition process")
    print("=" * 60)
    
    # Initialize components
    pdf_processor = ESS_PDFProcessor()
    chroma_manager = ChromaDBManager()
    
    # Define PDF directory
    pdf_directory = Path("data/raw/ess_reports/pdfs")
    
    if not pdf_directory.exists():
        print(f"[ERROR] PDF directory not found: {pdf_directory}")
        return
    
    # Get all PDF files
    all_pdfs = list(pdf_directory.glob("*.pdf"))
    print(f"[INFO] Found {len(all_pdfs)} PDF files in directory")
    
    if not all_pdfs:
        print("[WARN] No PDF files found in directory")
        return
    
    # Get existing PDFs in database
    try:
        collection = chroma_manager.collection
        existing_metadata = collection.get()
        
        existing_sources = set()
        if existing_metadata and 'metadatas' in existing_metadata:
            for metadata in existing_metadata['metadatas']:
                if metadata and 'source' in metadata:
                    # Extract just the filename
                    source_path = Path(metadata['source'])
                    existing_sources.add(source_path.name)
        
        print(f"[INFO] Found {len(existing_sources)} PDFs already in database")
        
    except Exception as e:
        print(f"[WARN] Could not check existing PDFs: {e}")
        existing_sources = set()
    
    # Find new PDFs
    new_pdfs = [pdf for pdf in all_pdfs if pdf.name not in existing_sources]
    
    if not new_pdfs:
        print("[OK] No new PDFs to add. All PDFs are already in the database.")
        return
    
    print(f"\n[INFO] Found {len(new_pdfs)} new PDFs to process:")
    for pdf in new_pdfs:
        print(f"  - {pdf.name}")
    
    # Process new PDFs
    print(f"\n[INFO] Processing {len(new_pdfs)} new PDFs...")
    print("-" * 60)
    
    all_documents = []
    
    for i, pdf_path in enumerate(new_pdfs, 1):
        print(f"\n[{i}/{len(new_pdfs)}] Processing: {pdf_path.name}")
        
        try:
            # Extract text and create chunks
            documents = pdf_processor.process_pdf(str(pdf_path))
            
            if documents:
                all_documents.extend(documents)
                print(f"[OK] Extracted {len(documents)} chunks from {pdf_path.name}")
            else:
                print(f"[WARN] No content extracted from {pdf_path.name}")
                
        except Exception as e:
            print(f"[ERROR] Failed to process {pdf_path.name}: {e}")
            continue
    
    # Add to ChromaDB
    if all_documents:
        print(f"\n[INFO] Adding {len(all_documents)} new chunks to ChromaDB...")
        
        try:
            chroma_manager.add_documents(all_documents)
            print(f"[OK] Successfully added {len(all_documents)} chunks to the database")
            
            # Show updated statistics
            updated_metadata = collection.get()
            total_chunks = len(updated_metadata['ids']) if updated_metadata else 0
            print(f"[INFO] Total chunks in database: {total_chunks}")
            
        except Exception as e:
            print(f"[ERROR] Failed to add documents to ChromaDB: {e}")
            return
    else:
        print("[WARN] No new documents to add")
    
    print("\n" + "=" * 60)
    print("[OK] PDF addition process complete!")
    print("\nNext steps:")
    print("1. Test the system with queries related to the new PDFs")
    print("2. Verify sources are displayed correctly in responses")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Process interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()

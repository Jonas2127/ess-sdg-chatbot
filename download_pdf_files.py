"""
Download PDF Files from HuggingFace
====================================
Utility script to download PDF files from HuggingFace repository.

This is useful for:
1. Setting up the system on a new machine
2. Restoring PDFs if local files are lost
3. Syncing with the latest PDF collection

Usage:
    python download_pdf_files.py
"""

import os
from pathlib import Path
from huggingface_hub import hf_hub_download, list_repo_files
from tqdm import tqdm


def download_pdfs_from_huggingface(
    repo_id="Mikigithub/ess-ethiopia-sdg-data",
    local_dir="data/raw/ess_reports/pdfs"
):
    """
    Download PDF files from HuggingFace repository.
    
    Args:
        repo_id: HuggingFace repository ID
        local_dir: Local directory to save PDFs
    """
    
    print("[INFO] Starting PDF download from HuggingFace")
    print("=" * 60)
    print(f"Repository: {repo_id}")
    print(f"Local directory: {local_dir}")
    print()
    
    # Create local directory if it doesn't exist
    local_path = Path(local_dir)
    local_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # List all files in the repository
        print("[INFO] Fetching repository file list...")
        all_files = list_repo_files(repo_id=repo_id)
        
        # Filter for PDF files
        pdf_files = [f for f in all_files if f.endswith('.pdf')]
        
        if not pdf_files:
            print("[WARN] No PDF files found in repository")
            return
        
        print(f"[OK] Found {len(pdf_files)} PDF files")
        print()
        
        # Download each PDF
        downloaded = 0
        skipped = 0
        failed = 0
        
        for pdf_file in tqdm(pdf_files, desc="Downloading PDFs"):
            local_file = local_path / Path(pdf_file).name
            
            # Skip if file already exists
            if local_file.exists():
                print(f"[SKIP] {Path(pdf_file).name} (already exists)")
                skipped += 1
                continue
            
            try:
                # Download file
                downloaded_path = hf_hub_download(
                    repo_id=repo_id,
                    filename=pdf_file,
                    local_dir=local_path,
                    local_dir_use_symlinks=False
                )
                
                print(f"[OK] Downloaded: {Path(pdf_file).name}")
                downloaded += 1
                
            except Exception as e:
                print(f"[ERROR] Failed to download {pdf_file}: {e}")
                failed += 1
        
        # Summary
        print()
        print("=" * 60)
        print("[OK] Download process complete!")
        print()
        print("Summary:")
        print(f"  Downloaded: {downloaded}")
        print(f"  Skipped (already exists): {skipped}")
        print(f"  Failed: {failed}")
        print(f"  Total PDFs: {len(pdf_files)}")
        
        if downloaded > 0:
            print()
            print("Next steps:")
            print("1. Run 'python add_new_pdfs.py' to add new PDFs to ChromaDB")
            print("2. Or run 'python build_dual_engine.py' to rebuild entire database")
        
    except Exception as e:
        print(f"[ERROR] Failed to access HuggingFace repository: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify the repository ID is correct")
        print("3. Ensure huggingface-hub is installed: pip install huggingface-hub")
        return


def main():
    """Main function."""
    
    # Check if huggingface_hub is installed
    try:
        import huggingface_hub
    except ImportError:
        print("[ERROR] huggingface-hub is not installed")
        print("Install it with: pip install huggingface-hub")
        return
    
    # Run download
    download_pdfs_from_huggingface()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Download interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()

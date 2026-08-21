"""
Download Large Files from Hugging Face for Streamlit Cloud Deployment
=====================================================================

This script downloads the ChromaDB vector store and SQLite database from
Hugging Face when the app starts on Streamlit Cloud.

Files hosted on Hugging Face:
- chromadb.zip (~800MB) - Vector store with embedded PDFs
- sdg_ethiopia.db (~10MB) - SQLite database with SDG indicators

⚠️ IMPORTANT: Update HF_USERNAME below with your Hugging Face username!

Author: Yonas Abiyu Gion
"""

import os
import zipfile
import requests
from pathlib import Path
import sys

def download_large_files():
    """Download large files from Hugging Face on Streamlit Cloud startup"""
    
    # Hugging Face username
    HF_USERNAME = "yonasabiyu"
    HF_REPO = f"{HF_USERNAME}/ess-sdg-chatbot-data"
    
    # Hugging Face download URLs
    CHROMADB_URL = f"https://huggingface.co/{HF_REPO}/resolve/main/chromadb.zip"
    SQLITE_URL = f"https://huggingface.co/{HF_REPO}/resolve/main/sdg_ethiopia.db"
    
    # Local paths
    chromadb_dir = Path("data/vectorstore/chromadb")
    sqlite_db = Path("data/sql_database/sdg_ethiopia.db")
    chromadb_zip = Path("chromadb.zip")
    
    try:
        # Download ChromaDB if not exists
        if not chromadb_dir.exists() or not any(chromadb_dir.iterdir()):
            print("📦 Downloading ChromaDB vector store from Hugging Face...")
            print(f"   URL: {CHROMADB_URL}")
            
            # Download with progress
            response = requests.get(CHROMADB_URL, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0
            
            with open(chromadb_zip, "wb") as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0 and downloaded % (10 * 1024 * 1024) < block_size:
                            percent = (downloaded / total_size) * 100
                            print(f"   Downloaded: {downloaded / 1024 / 1024:.1f}MB / {total_size / 1024 / 1024:.1f}MB ({percent:.1f}%)")
            
            print("📂 Extracting ChromaDB...")
            chromadb_dir.parent.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(chromadb_zip, 'r') as zip_ref:
                zip_ref.extractall("data/vectorstore/")
            
            # Cleanup
            chromadb_zip.unlink()
            print("✅ ChromaDB ready!")
        else:
            print("✅ ChromaDB already exists, skipping download")
        
        # Download SQLite DB if not exists
        if not sqlite_db.exists():
            print("📊 Downloading SQLite database from Hugging Face...")
            print(f"   URL: {SQLITE_URL}")
            
            sqlite_db.parent.mkdir(parents=True, exist_ok=True)
            
            response = requests.get(SQLITE_URL)
            response.raise_for_status()
            
            with open(sqlite_db, "wb") as f:
                f.write(response.content)
            
            file_size = sqlite_db.stat().st_size / 1024 / 1024
            print(f"   Downloaded: {file_size:.1f}MB")
            print("✅ SQLite database ready!")
        else:
            print("✅ SQLite database already exists, skipping download")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Make sure Hugging Face repository exists: https://huggingface.co/{HF_REPO}")
        print(f"   And files are uploaded: chromadb.zip, sdg_ethiopia.db")
        return False
    
    except Exception as e:
        print(f"❌ Error downloading files: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 80)
    print("🌐 Downloading Large Files from Hugging Face")
    print("=" * 80)
    print()
    
    success = download_large_files()
    
    print()
    print("=" * 80)
    if success:
        print("✅ All files downloaded successfully!")
    else:
        print("❌ Download failed! Check errors above.")
    print("=" * 80)
    
    sys.exit(0 if success else 1)

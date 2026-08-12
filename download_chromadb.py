"""
Download ChromaDB from Hugging Face at runtime
This runs automatically when the Streamlit app starts
"""
import os
import urllib.request
import zipfile
import shutil
from pathlib import Path


def download_chromadb():
    """Download and extract ChromaDB from Hugging Face"""
    
    chromadb_path = "data/vectorstore/chromadb"
    
    # Check if ChromaDB already exists
    if os.path.exists(chromadb_path) and os.path.exists(f"{chromadb_path}/chroma.sqlite3"):
        print("✅ ChromaDB already exists, skipping download")
        return True
    
    print("📥 Downloading ChromaDB from Hugging Face...")
    
    # Hugging Face dataset URL
    hf_url = os.getenv("CHROMADB_URL", "https://huggingface.co/datasets/yonasabiyu/ess-chromadb/resolve/main/chromadb.zip")
    
    try:
        # Create temp directory
        os.makedirs("temp", exist_ok=True)
        zip_path = "temp/chromadb.zip"
        
        # Download with progress
        print(f"   Downloading from: {hf_url}")
        urllib.request.urlretrieve(hf_url, zip_path)
        print(f"   ✅ Downloaded: {os.path.getsize(zip_path) / (1024*1024):.2f} MB")
        
        # Extract
        print("   📦 Extracting ChromaDB...")
        os.makedirs("data/vectorstore", exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("data/vectorstore")
        
        print("   ✅ ChromaDB extracted successfully")
        
        # Cleanup
        shutil.rmtree("temp", ignore_errors=True)
        
        # Verify
        if os.path.exists(f"{chromadb_path}/chroma.sqlite3"):
            print("✅ ChromaDB ready!")
            return True
        else:
            print("❌ ChromaDB extraction failed - chroma.sqlite3 not found")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading ChromaDB: {e}")
        print("⚠️  App will continue without vector search capability")
        return False


if __name__ == "__main__":
    # Test the download
    success = download_chromadb()
    if success:
        print("\n🎉 ChromaDB download test successful!")
    else:
        print("\n❌ ChromaDB download test failed")

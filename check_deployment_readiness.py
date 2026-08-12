"""
Pre-Deployment Checklist for Streamlit Cloud
=============================================
Run this script before deploying to verify everything is ready

Usage: python check_deployment_readiness.py
"""

import os
import sys
from pathlib import Path

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_file(path, description):
    """Check if a file exists"""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}")
    if not exists:
        print(f"   → Missing: {path}")
    return exists

def check_directory(path, description, min_files=0):
    """Check if a directory exists and has files"""
    exists = os.path.exists(path)
    if exists:
        file_count = len(list(Path(path).rglob("*"))) if os.path.isdir(path) else 0
        status = "✅" if file_count >= min_files else "⚠️"
        print(f"{status} {description} ({file_count} files)")
        if file_count < min_files:
            print(f"   → Expected at least {min_files} files")
        return file_count >= min_files
    else:
        print(f"❌ {description}")
        print(f"   → Missing: {path}")
        return False

def check_requirements():
    """Check requirements.txt"""
    print_header("📦 CHECKING REQUIREMENTS")
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False
    
    with open("requirements.txt", "r") as f:
        content = f.read()
    
    # Check for required packages
    required = ["streamlit", "langchain", "chromadb", "pandas", "langchain-groq"]
    missing = [pkg for pkg in required if pkg not in content.lower()]
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        return False
    
    # Check for Ollama (should NOT be present for cloud deployment)
    if "ollama" in content.lower() and not content.count("#") > content.count("ollama"):
        print("⚠️  Warning: 'ollama' found in requirements.txt")
        print("   → Remove or comment out for Streamlit Cloud deployment")
        return False
    
    print("✅ requirements.txt is ready for Streamlit Cloud")
    return True

def check_data_files():
    """Check critical data files"""
    print_header("📊 CHECKING DATA FILES")
    
    all_good = True
    
    # ChromaDB vector store
    chromadb_ok = check_directory(
        "data/vectorstore/chromadb",
        "ChromaDB Vector Store",
        min_files=5
    )
    all_good = all_good and chromadb_ok
    
    # SQLite database
    sqlite_ok = check_file(
        "data/sql_database/sdg_ethiopia.db",
        "SQLite Database"
    )
    all_good = all_good and sqlite_ok
    
    # UN SDG Excel files
    excel_ok = check_directory(
        "data/raw/un_sdg_excel",
        "UN SDG Excel Files",
        min_files=17
    )
    all_good = all_good and excel_ok
    
    return all_good

def check_core_files():
    """Check core application files"""
    print_header("🔧 CHECKING CORE FILES")
    
    files = {
        "streamlit_app.py": "Main Streamlit Application",
        ".streamlit/config.toml": "Streamlit Configuration",
        "src/dual_engine_router/__init__.py": "Dual Engine Router Module",
        "src/dual_engine_router/langchain_rag.py": "LangChain RAG System",
        "src/export/__init__.py": "Export Module",
        "assets/ess_logo_fixed.png": "ESS Logo",
    }
    
    all_good = True
    for path, desc in files.items():
        all_good = all_good and check_file(path, desc)
    
    return all_good

def check_gitignore():
    """Check .gitignore configuration"""
    print_header("🚫 CHECKING .gitignore")
    
    if not os.path.exists(".gitignore"):
        print("❌ .gitignore not found!")
        return False
    
    with open(".gitignore", "r") as f:
        content = f.read()
    
    # Check that .env is ignored
    if ".env" not in content:
        print("⚠️  Warning: .env should be in .gitignore")
        return False
    
    # Check that ChromaDB is NOT ignored (should be commented out)
    if "data/vectorstore/chromadb" in content and not content.count("#data/vectorstore/chromadb") > 0:
        lines = content.split("\n")
        chromadb_lines = [l for l in lines if "data/vectorstore/chromadb" in l and not l.strip().startswith("#")]
        if chromadb_lines:
            print("⚠️  Warning: ChromaDB is being ignored by .gitignore")
            print("   → This MUST be included for Streamlit Cloud deployment")
            print("   → Comment out or remove this line:")
            for line in chromadb_lines:
                print(f"     {line}")
            return False
    
    print("✅ .gitignore is configured correctly")
    return True

def check_secrets():
    """Check secrets configuration"""
    print_header("🔐 CHECKING SECRETS")
    
    # Check if .env exists (should NOT be committed)
    if os.path.exists(".env"):
        print("⚠️  Warning: .env file exists")
        print("   → Do NOT commit this file to Git!")
        print("   → Add secrets to Streamlit Cloud dashboard instead")
    
    # Check if secrets template exists
    if check_file(".streamlit/secrets.toml.example", "Secrets Template"):
        print("   → Copy contents to Streamlit Cloud: App Settings → Secrets")
    
    return True

def estimate_repo_size():
    """Estimate repository size"""
    print_header("📏 ESTIMATING REPOSITORY SIZE")
    
    total_size = 0
    
    # Calculate size
    for root, dirs, files in os.walk("."):
        # Skip .git directory
        if ".git" in root:
            continue
        for file in files:
            try:
                total_size += os.path.getsize(os.path.join(root, file))
            except:
                pass
    
    size_mb = total_size / (1024 * 1024)
    print(f"📦 Estimated repository size: {size_mb:.2f} MB")
    
    if size_mb > 1000:
        print("⚠️  Warning: Repository is quite large (>1 GB)")
        print("   → Consider using external storage for large files")
        print("   → Streamlit Cloud may have upload limits")
        return False
    elif size_mb > 500:
        print("⚠️  Repository is moderately large (>500 MB)")
        print("   → Should work but may take longer to deploy")
    else:
        print("✅ Repository size is acceptable for Streamlit Cloud")
    
    return True

def main():
    """Run all checks"""
    print("\n" + "🚀" * 35)
    print("  STREAMLIT CLOUD DEPLOYMENT READINESS CHECK")
    print("  ET ESS RAG Bot - Pre-Deployment Verification")
    print("🚀" * 35)
    
    checks = {
        "Core Files": check_core_files(),
        "Requirements": check_requirements(),
        "Data Files": check_data_files(),
        "Git Ignore": check_gitignore(),
        "Secrets": check_secrets(),
        "Repository Size": estimate_repo_size(),
    }
    
    # Summary
    print_header("📋 SUMMARY")
    
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    for name, status in checks.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {name}")
    
    print(f"\n{'=' * 70}")
    print(f"  RESULT: {passed}/{total} checks passed")
    print(f"{'=' * 70}")
    
    if passed == total:
        print("\n🎉 SUCCESS! Your app is ready for Streamlit Cloud deployment!")
        print("\nNext steps:")
        print("1. Commit changes: git add . && git commit -m 'Ready for deployment'")
        print("2. Push to GitHub: git push origin main")
        print("3. Deploy on Streamlit Cloud: https://share.streamlit.io")
        print("4. Add secrets in Streamlit Cloud dashboard")
        print("\n📖 See docs/STREAMLIT_CLOUD_DEPLOYMENT.md for detailed guide")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues above before deploying.")
        print("\n📖 See docs/STREAMLIT_CLOUD_DEPLOYMENT.md for help")
        return 1

if __name__ == "__main__":
    sys.exit(main())

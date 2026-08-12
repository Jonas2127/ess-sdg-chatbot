"""
DUAL-ENGINE BUILD SCRIPT
=========================
One command to build everything:
- Engine A: Process 222 PDFs → ChromaDB
- Engine B: Process 17 Excel files → SQLite

Usage:
    python build_dual_engine.py
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from engine_a_pdf_rag import PDFProcessor, ChromaDBVectorStore
from engine_b_excel_sql import ExcelProcessor


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"🚀 {title}")
    print("=" * 80)


def build_engine_a():
    """Build Engine A: PDF RAG System"""
    print_header("ENGINE A: PDF RAG SYSTEM")
    
    # Initialize PDF processor
    pdf_processor = PDFProcessor(chunk_size=700, chunk_overlap=100)
    
    # Process ESS PDFs (221 files)
    print("\n📄 Step 1: Processing ESS PDF Reports...")
    ess_chunks = pdf_processor.process_folder(
        "data/raw/ess_reports/pdfs",
        "ESS"
    )
    
    # Process AfDB PDF (1 file)
    print("\n📄 Step 2: Processing AfDB Policy Document...")
    afdb_chunks = pdf_processor.process_folder(
        "data/raw/afdb_reports",
        "AfDB"
    )
    
    # Combine all chunks
    all_chunks = ess_chunks + afdb_chunks
    
    print(f"\n✅ Total PDF chunks extracted: {len(all_chunks)}")
    
    # Initialize ChromaDB vector store
    print("\n🔄 Step 3: Creating ChromaDB vector store...")
    vectorstore = ChromaDBVectorStore()
    vectorstore.create_collection(reset=True)
    
    # Add chunks to vector store
    print("\n🔄 Step 4: Vectorizing and storing chunks...")
    vectorstore.add_documents(all_chunks, batch_size=100)
    
    # Get stats
    stats = vectorstore.get_stats()
    print(f"\n📊 Engine A Stats:")
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Collection: {stats['collection_name']}")
    print(f"   Location: {stats['persist_directory']}")
    
    return stats


def build_engine_b():
    """Build Engine B: Excel SQL System"""
    print_header("ENGINE B: EXCEL SQL SYSTEM")
    
    # Initialize Excel processor
    excel_processor = ExcelProcessor()
    excel_processor.connect_db()
    
    # Process all 17 UN SDG Excel files
    print("\n📊 Step 1: Processing UN SDG Excel files...")
    df = excel_processor.process_all_excel_files("data/raw/un_sdg_excel")
    
    # Create SQL tables
    print("\n🔄 Step 2: Creating SQL database...")
    excel_processor.create_tables(df)
    
    # Get database info
    info = excel_processor.get_table_info()
    print(f"\n📊 Engine B Stats:")
    for table_name, table_info in info.items():
        print(f"   {table_name}: {table_info['row_count']} rows, {len(table_info['columns'])} columns")
    
    # Test query
    print("\n🔍 Sample Query: Indicators per Goal")
    test_query = """
    SELECT goal_number, goal_name, COUNT(*) as indicator_count 
    FROM sdg_indicators 
    GROUP BY goal_number 
    ORDER BY goal_number
    LIMIT 5
    """
    results = excel_processor.execute_query(test_query)
    if not results.empty:
        print(results.to_string(index=False))
    
    excel_processor.close_db()
    
    return info


def main():
    """Build complete dual-engine system"""
    start_time = datetime.now()
    
    print("=" * 80)
    print("🇪🇹 ESS DUAL-ENGINE RAG CHATBOT - BUILD SCRIPT")
    print("=" * 80)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Build Engine A (PDF RAG)
        engine_a_stats = build_engine_a()
        
        # Build Engine B (Excel SQL)
        engine_b_stats = build_engine_b()
        
        # Summary
        print_header("BUILD COMPLETE ✅")
        
        print(f"\n📊 Final Summary:")
        print(f"\n   Engine A (PDF RAG):")
        print(f"   • 221 ESS PDFs + 1 AfDB PDF processed")
        print(f"   • {engine_a_stats['total_chunks']} chunks vectorized")
        print(f"   • ChromaDB ready at: {engine_a_stats['persist_directory']}")
        
        print(f"\n   Engine B (Excel SQL):")
        print(f"   • 17 UN SDG Excel files processed")
        sdg_table = engine_b_stats.get('sdg_indicators', {})
        print(f"   • {sdg_table.get('row_count', 0)} indicators stored")
        print(f"   • SQLite DB ready at: data/sql_database/sdg_ethiopia.db")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n⏱️  Total processing time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        
        print("\n" + "=" * 80)
        print("🎉 DUAL-ENGINE SYSTEM READY!")
        print("=" * 80)
        print("\nNext step: Run the chatbot")
        print("   streamlit run streamlit_app.py")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

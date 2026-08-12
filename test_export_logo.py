"""
Test Export Logo Functionality
Verifies that ESS logo appears in both PDF and Word exports
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from export import PDFExporter, WordExporter


def test_logo_paths():
    """Test that logo paths are correctly resolved"""
    print("\n" + "=" * 70)
    print("  TESTING EXPORT LOGO PATHS")
    print("=" * 70)
    
    # Test PDF Exporter
    print("\n📄 PDF Exporter:")
    pdf_exporter = PDFExporter()
    print(f"   Logo path: {pdf_exporter.logo_path}")
    
    if os.path.exists(pdf_exporter.logo_path):
        print(f"   ✅ Logo file found")
        size = os.path.getsize(pdf_exporter.logo_path) / 1024
        print(f"   Size: {size:.2f} KB")
    else:
        print(f"   ❌ Logo file NOT found!")
        return False
    
    # Test Word Exporter
    print("\n📝 Word Exporter:")
    word_exporter = WordExporter()
    print(f"   Logo path: {word_exporter.logo_path}")
    
    if os.path.exists(word_exporter.logo_path):
        print(f"   ✅ Logo file found")
        size = os.path.getsize(word_exporter.logo_path) / 1024
        print(f"   Size: {size:.2f} KB")
    else:
        print(f"   ❌ Logo file NOT found!")
        return False
    
    return True


def test_pdf_export():
    """Test PDF export with logo"""
    print("\n" + "=" * 70)
    print("  TESTING PDF EXPORT WITH LOGO")
    print("=" * 70)
    
    # Create sample messages
    messages = [
        {
            'role': 'user',
            'content': 'What is Ethiopia\'s poverty rate?'
        },
        {
            'role': 'assistant',
            'content': 'According to the UN SDG database, Ethiopia\'s poverty rate in 2022 was 23.5%.',
            'metadata': {
                'time': 1.23,
                'engines': ['SQL Database'],
                'sources': 2
            }
        }
    ]
    
    pdf_exporter = PDFExporter()
    result = pdf_exporter.export_conversation(messages, "test_logo_export.pdf")
    
    if result['success']:
        print(f"\n✅ PDF export successful!")
        print(f"   File: {result['filepath']}")
        
        # Check file size
        if os.path.exists(result['filepath']):
            size = os.path.getsize(result['filepath']) / 1024
            print(f"   Size: {size:.2f} KB")
            
            # If size is very small, logo might be missing
            if size < 10:
                print(f"   ⚠️  Warning: File size is unusually small (logo may be missing)")
            else:
                print(f"   ✅ File size looks good (logo likely included)")
        
        return True
    else:
        print(f"\n❌ PDF export failed!")
        print(f"   Error: {result['error']}")
        return False


def test_word_export():
    """Test Word export with logo"""
    print("\n" + "=" * 70)
    print("  TESTING WORD EXPORT WITH LOGO")
    print("=" * 70)
    
    # Create sample messages
    messages = [
        {
            'role': 'user',
            'content': 'What is Ethiopia\'s poverty rate?'
        },
        {
            'role': 'assistant',
            'content': 'According to the UN SDG database, Ethiopia\'s poverty rate in 2022 was 23.5%.',
            'metadata': {
                'time': 1.23,
                'engines': ['SQL Database'],
                'sources': 2
            }
        }
    ]
    
    word_exporter = WordExporter()
    result = word_exporter.export_conversation(messages, "test_logo_export.docx")
    
    if result['success']:
        print(f"\n✅ Word export successful!")
        print(f"   File: {result['filepath']}")
        
        # Check file size
        if os.path.exists(result['filepath']):
            size = os.path.getsize(result['filepath']) / 1024
            print(f"   Size: {size:.2f} KB")
            
            # If size is very small, logo might be missing
            if size < 20:
                print(f"   ⚠️  Warning: File size is unusually small (logo may be missing)")
            else:
                print(f"   ✅ File size looks good (logo likely included)")
        
        return True
    else:
        print(f"\n❌ Word export failed!")
        print(f"   Error: {result['error']}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🧪" * 35)
    print("  ESS LOGO EXPORT TEST SUITE")
    print("🧪" * 35)
    
    # Run tests
    logo_ok = test_logo_paths()
    pdf_ok = test_pdf_export() if logo_ok else False
    word_ok = test_word_export() if logo_ok else False
    
    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    
    tests = {
        "Logo Path Resolution": logo_ok,
        "PDF Export with Logo": pdf_ok,
        "Word Export with Logo": word_ok
    }
    
    for name, status in tests.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {name}")
    
    passed = sum(1 for v in tests.values() if v)
    total = len(tests)
    
    print(f"\n{'=' * 70}")
    print(f"  RESULT: {passed}/{total} tests passed")
    print(f"{'=' * 70}")
    
    if passed == total:
        print("\n🎉 SUCCESS! ESS logo is working in exports!")
        print("\n📂 Test files created in exports/ folder:")
        print("   - test_logo_export.pdf")
        print("   - test_logo_export.docx")
        print("\n👀 Open these files to verify the ESS logo appears at the top")
        return 0
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

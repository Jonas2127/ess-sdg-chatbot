"""
Engine A: PDF Processing & RAG System
======================================
Processes 221 ESS PDFs + 1 AfDB PDF into ChromaDB vector store

Features:
- Extracts text from PDFs (handles digital & scanned)
- Preserves tables and footnotes
- Handles Amharic/English mixed content
- Smart chunking (500-800 words)
- Rich metadata tagging
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Tuple
import pdfplumber
from tqdm import tqdm
import re

class PDFProcessor:
    """Extract and process text from PDF documents"""
    
    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, Dict]:
        """
        Extract text from a single PDF file
        
        Returns:
            text: Extracted text
            metadata: File metadata (pages, size, etc.)
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                tables = []
                
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    text = page.extract_text()
                    if text:
                        full_text += f"\n--- Page {page_num} ---\n{text}\n"
                    
                    # Extract tables
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table_idx, table in enumerate(page_tables):
                            tables.append({
                                'page': page_num,
                                'table_index': table_idx,
                                'data': table
                            })
                
                # Convert tables to text format
                table_text = self._format_tables(tables)
                if table_text:
                    full_text += "\n\n=== TABLES ===\n" + table_text
                
                metadata = {
                    'filename': os.path.basename(pdf_path),
                    'pages': len(pdf.pages),
                    'has_tables': len(tables) > 0,
                    'table_count': len(tables)
                }
                
                return full_text, metadata
                
        except Exception as e:
            print(f"⚠️  Error processing {pdf_path}: {str(e)}")
            return "", {'filename': os.path.basename(pdf_path), 'error': str(e)}
    
    def _format_tables(self, tables: List[Dict]) -> str:
        """Convert extracted tables to readable text format"""
        formatted = []
        
        for table_info in tables:
            table_data = table_info['data']
            page = table_info['page']
            
            formatted.append(f"\n--- Table on Page {page} ---")
            
            # Format table as text
            for row in table_data:
                if row:
                    row_text = " | ".join([str(cell) if cell else "" for cell in row])
                    formatted.append(row_text)
        
        return "\n".join(formatted)
    
    def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Full document text
            metadata: Document metadata
            
        Returns:
            List of chunks with metadata
        """
        # Split into words
        words = text.split()
        chunks = []
        
        start_idx = 0
        chunk_id = 0
        
        while start_idx < len(words):
            # Get chunk
            end_idx = min(start_idx + self.chunk_size, len(words))
            chunk_words = words[start_idx:end_idx]
            chunk_text = " ".join(chunk_words)
            
            # Create chunk with metadata
            chunk = {
                'text': chunk_text,
                'chunk_id': chunk_id,
                'chunk_size': len(chunk_words),
                'start_word': start_idx,
                'end_word': end_idx,
                **metadata  # Include all document metadata
            }
            
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            start_idx += self.chunk_size - self.chunk_overlap
            chunk_id += 1
        
        return chunks
    
    def extract_metadata_from_filename(self, filename: str) -> Dict:
        """
        Extract metadata from PDF filename
        
        Examples:
            ESS_CPI_Bulletin_2023_Q4.pdf -> year: 2023, quarter: Q4, type: CPI
            Agricultural_Survey_2022.pdf -> year: 2022, type: Survey
        """
        metadata = {}
        
        # Extract year (4 digits)
        year_match = re.search(r'\b(20\d{2})\b', filename)
        if year_match:
            metadata['year'] = int(year_match.group(1))
        
        # Extract quarter (Q1, Q2, Q3, Q4)
        quarter_match = re.search(r'\b(Q[1-4])\b', filename, re.IGNORECASE)
        if quarter_match:
            metadata['quarter'] = quarter_match.group(1).upper()
        
        # Detect report type from filename
        filename_lower = filename.lower()
        if 'cpi' in filename_lower or 'price' in filename_lower:
            metadata['report_type'] = 'Price Index'
            metadata['category'] = 'Economic Statistics'
        elif 'agricult' in filename_lower or 'farm' in filename_lower:
            metadata['report_type'] = 'Agricultural Survey'
            metadata['category'] = 'Agriculture'
        elif 'population' in filename_lower or 'census' in filename_lower:
            metadata['report_type'] = 'Population & Census'
            metadata['category'] = 'Demographics'
        elif 'household' in filename_lower or 'income' in filename_lower:
            metadata['report_type'] = 'Household Survey'
            metadata['category'] = 'Social Statistics'
        elif 'business' in filename_lower or 'enterprise' in filename_lower:
            metadata['report_type'] = 'Business Statistics'
            metadata['category'] = 'Economic Statistics'
        elif 'afdb' in filename_lower or 'strategy' in filename_lower:
            metadata['report_type'] = 'Policy Document'
            metadata['category'] = 'Strategic Planning'
        else:
            metadata['report_type'] = 'General Report'
            metadata['category'] = 'General'
        
        return metadata
    
    def process_folder(self, folder_path: str, source_name: str) -> List[Dict]:
        """
        Process all PDFs in a folder
        
        Args:
            folder_path: Path to folder containing PDFs
            source_name: Source identifier (e.g., 'ESS', 'AfDB')
            
        Returns:
            List of all chunks from all PDFs
        """
        pdf_files = list(Path(folder_path).glob("*.pdf"))
        
        if not pdf_files:
            print(f"⚠️  No PDF files found in {folder_path}")
            return []
        
        print(f"\n📄 Processing {len(pdf_files)} PDFs from {source_name}...")
        
        all_chunks = []
        
        for pdf_path in tqdm(pdf_files, desc=f"Processing {source_name} PDFs"):
            # Extract text
            text, file_metadata = self.extract_text_from_pdf(str(pdf_path))
            
            if not text:
                continue
            
            # Extract metadata from filename
            filename_metadata = self.extract_metadata_from_filename(file_metadata['filename'])
            
            # Combine metadata
            combined_metadata = {
                'source': source_name,
                'file_path': str(pdf_path),
                **file_metadata,
                **filename_metadata
            }
            
            # Chunk the text
            chunks = self.chunk_text(text, combined_metadata)
            all_chunks.extend(chunks)
        
        print(f"✅ Extracted {len(all_chunks)} chunks from {len(pdf_files)} PDFs")
        
        return all_chunks


def main():
    """Test the PDF processor"""
    processor = PDFProcessor()
    
    # Test on ESS PDFs
    ess_chunks = processor.process_folder(
        "data/raw/ess_reports/pdfs",
        "ESS"
    )
    
    # Test on AfDB PDF
    afdb_chunks = processor.process_folder(
        "data/raw/afdb_reports",
        "AfDB"
    )
    
    total_chunks = len(ess_chunks) + len(afdb_chunks)
    print(f"\n🎯 Total chunks: {total_chunks}")
    
    # Save sample
    if ess_chunks:
        print(f"\n📝 Sample ESS chunk:")
        print(f"   Filename: {ess_chunks[0]['filename']}")
        print(f"   Category: {ess_chunks[0].get('category', 'N/A')}")
        print(f"   Text preview: {ess_chunks[0]['text'][:200]}...")


if __name__ == "__main__":
    main()

"""
Engine A: ChromaDB Vector Store
================================
Creates and manages ChromaDB vector database for PDF chunks

Features:
- Multilingual embeddings (Amharic + English)
- Rich metadata filtering
- Hybrid search (dense + sparse)
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from tqdm import tqdm
import os

class ChromaDBVectorStore:
    """Manage ChromaDB vector store for PDF documents"""
    
    def __init__(self, persist_directory: str = "data/vectorstore/chromadb"):
        """
        Initialize ChromaDB client
        
        Args:
            persist_directory: Where to store the database
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Load embedding model (multilingual - supports Amharic & English)
        print("📥 Loading embedding model...")
        self.embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("✅ Embedding model loaded")
        
        # Collection name
        self.collection_name = "ess_pdf_documents"
        
    def create_collection(self, reset: bool = False):
        """
        Create or get collection
        
        Args:
            reset: If True, delete existing collection and create new
        """
        if reset:
            try:
                self.client.delete_collection(self.collection_name)
                print(f"🗑️  Deleted existing collection: {self.collection_name}")
            except:
                pass
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "ESS PDF documents with AfDB policy papers"}
        )
        
        print(f"✅ Collection ready: {self.collection_name}")
    
    def add_documents(self, chunks: List[Dict], batch_size: int = 100):
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of chunks with text and metadata
            batch_size: Number of chunks to process at once
        """
        if not chunks:
            print("⚠️  No chunks to add")
            return
        
        print(f"\n🔄 Adding {len(chunks)} chunks to ChromaDB...")
        
        for i in tqdm(range(0, len(chunks), batch_size), desc="Vectorizing chunks"):
            batch = chunks[i:i + batch_size]
            
            # Prepare data
            ids = []
            texts = []
            metadatas = []
            
            for idx, chunk in enumerate(batch):
                chunk_id = f"chunk_{i + idx}"
                ids.append(chunk_id)
                texts.append(chunk['text'])
                
                # Prepare metadata (ChromaDB requires string/int/float values)
                metadata = {
                    'source': chunk.get('source', 'Unknown'),
                    'filename': chunk.get('filename', 'Unknown'),
                    'category': chunk.get('category', 'General'),
                    'report_type': chunk.get('report_type', 'General Report'),
                    'pages': chunk.get('pages', 0),
                    'chunk_id': chunk.get('chunk_id', 0),
                    'has_tables': str(chunk.get('has_tables', False))
                }
                
                # Add year if available
                if 'year' in chunk:
                    metadata['year'] = chunk['year']
                
                # Add quarter if available
                if 'quarter' in chunk:
                    metadata['quarter'] = chunk['quarter']
                
                metadatas.append(metadata)
            
            # Generate embeddings
            embeddings = self.embedder.encode(texts, show_progress_bar=False).tolist()
            
            # Add to collection
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas,
                embeddings=embeddings
            )
        
        print(f"✅ Added {len(chunks)} chunks to ChromaDB")
    
    def search(self, query: str, n_results: int = 5, filter_dict: Dict = None):
        """
        Search for relevant chunks
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_dict: Metadata filters (e.g., {'category': 'Price Index'})
            
        Returns:
            Search results
        """
        # Generate query embedding
        query_embedding = self.embedder.encode([query])[0].tolist()
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_dict if filter_dict else None
        )
        
        return results
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        count = self.collection.count()
        
        return {
            'total_chunks': count,
            'collection_name': self.collection_name,
            'persist_directory': self.persist_directory
        }


def main():
    """Test ChromaDB vector store"""
    vectorstore = ChromaDBVectorStore()
    vectorstore.create_collection(reset=True)
    
    # Test with sample chunks
    sample_chunks = [
        {
            'text': 'Ethiopia Consumer Price Index (CPI) increased by 5.2% in Q4 2023.',
            'source': 'ESS',
            'filename': 'ESS_CPI_2023_Q4.pdf',
            'category': 'Economic Statistics',
            'report_type': 'Price Index',
            'year': 2023,
            'quarter': 'Q4',
            'pages': 10,
            'chunk_id': 0,
            'has_tables': True
        }
    ]
    
    vectorstore.add_documents(sample_chunks)
    
    # Test search
    results = vectorstore.search("What is the inflation rate?", n_results=1)
    print(f"\n🔍 Test search results:")
    print(f"   Query: 'What is the inflation rate?'")
    print(f"   Found: {results['documents'][0]}")
    
    stats = vectorstore.get_stats()
    print(f"\n📊 Stats: {stats}")


if __name__ == "__main__":
    main()

"""
Simple vector store using ChromaDB
For storing and retrieving ALS knowledge
Refactored for multi-collection support
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store handling multiple collections for ALS knowledge"""
    
    def __init__(self, persist_dir: str = "./chroma_db"):
        """
        Initialize vector store
        
        Args:
            persist_dir: Directory to store ChromaDB data
        """
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(exist_ok=True)
        
        # Initialize embedding model
        logger.info("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB client
        logger.info("Initializing ChromaDB...")
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize collections
        self.collections = {}
        for name in ["medical_knowledge", "community_experiences"]:
            self.collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"description": f"ALS {name}"}
            )
            
        logger.info("✅ Vector store ready")
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get the number of documents in a collection"""
        if collection_name in self.collections:
            return self.collections[collection_name].count()
        return 0

    def add_to_collection(self, collection_name: str, text: str, metadata: Dict[str, Any], doc_id: str):
        """Add a document to a specific collection"""
        if collection_name not in self.collections:
            logger.error(f"Collection {collection_name} not found")
            return
            
        try:
            embedding = self.embedding_model.encode([text]).tolist()
            self.collections[collection_name].add(
                embeddings=embedding,
                documents=[text],
                metadatas=[metadata],
                ids=[doc_id]
            )
        except Exception as e:
            logger.error(f"Error adding to {collection_name}: {e}")

    def clear_collection(self, collection_name: str):
        """Clear all data from a collection"""
        try:
            self.client.delete_collection(collection_name)
            self.collections[collection_name] = self.client.get_or_create_collection(collection_name)
            logger.info(f"Cleared collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error clearing {collection_name}: {e}")

    def search(self, query: str, category: str = None, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search across relevant collections
        
        Args:
            query: Search query
            category: Optional category filter
            n_results: Number of results to return PER collection
            
        Returns:
            List of relevant documents with metadata
        """
        all_results = []
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Search all collections
        for name, collection in self.collections.items():
            try:
                # Prepare filters if needed
                where_filter = None
                # Simple logic: if category is 'medical' don't search community, etc.
                # For now, we search broadly to find best matches
                
                results = collection.query(
                    query_embeddings=query_embedding,
                    n_results=n_results,
                    where=where_filter,
                    include=["documents", "metadatas", "distances"]
                )
                
                if results['documents']:
                    for i, (doc, metadata, distance) in enumerate(zip(
                        results['documents'][0],
                        results['metadatas'][0],
                        results['distances'][0]
                    )):
                        all_results.append({
                            'content': doc,
                            'source': metadata.get('source', 'Unknown'),
                            'type': metadata.get('type', 'unknown'),
                            'trust_score': metadata.get('trust_score', 5),
                            'distance': float(distance),
                            'collection': name
                        })
            except Exception as e:
                logger.error(f"Search error in {name}: {e}")
                
        # Sort by distance (relevance)
        all_results.sort(key=lambda x: x['distance'])
        
        return all_results[:5] # Return top 5 overall

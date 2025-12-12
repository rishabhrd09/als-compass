"""
Enhanced Vector Store with Multi-Collection Hierarchy and Hybrid Search
Supports specialized collections for different content types with priority routing
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)


class EnhancedVectorStore:
    """Enhanced vector store with multi-collection hierarchy and hybrid search"""
    
    def __init__(self, persist_dir: str = "./chroma_db_enhanced"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(exist_ok=True)
        
        # Load embedding model
        logger.info("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        logger.info("Initializing ChromaDB Enhanced...")
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Define collection hierarchy with priority and trust scores
        self.collection_config = {
            # WhatsApp community collections
            'community_qa_pairs': {
                'description': 'Question-Answer pairs from WhatsApp',
                'priority': 10,
                'trust_base': 8
            },
            'emergency_experiences': {
                'description': 'Emergency situations and responses',
                'priority': 10,
                'trust_base': 9
            },
            'community_discussions': {
                'description': 'General community discussions',
                'priority': 7,
                'trust_base': 7
            },
            # Medical authority collections
            'medical_authoritative': {
                'description': 'Tier 1 medical sources (ALS Assoc, NIH)',
                'priority': 9,
                'trust_base': 10
            },
            'medical_clinical': {
                'description': 'Tier 2 clinical guidelines',
                'priority': 8,
                'trust_base': 9
            },
            'medical_community': {
                'description': 'Tier 3 support organizations',
                'priority': 7,
                'trust_base': 8
            }
        }
        
        # Initialize all collections
        self.collections = {}
        for name, config in self.collection_config.items():
            self.collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={
                    'description': config['description'],
                    'priority': config['priority']
                }
            )
        
        logger.info(f"✅ Enhanced Vector Store ready with {len(self.collections)} collections")
    
    def add_document(
        self, 
        collection_name: str, 
        text: str, 
        metadata: Dict, 
        doc_id: str
    ):
        """Add document to a specific collection"""
        if collection_name not in self.collections:
            logger.error(f"Collection {collection_name} not found")
            return False
        
        try:
            embedding = self.embedding_model.encode([text]).tolist()
            
            # Ensure metadata values are serializable
            clean_metadata = {}
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    clean_metadata[key] = value
                elif isinstance(value, list):
                    clean_metadata[key] = str(value)  # Convert lists to strings
                elif value is None:
                    clean_metadata[key] = ""
                else:
                    clean_metadata[key] = str(value)
            
            self.collections[collection_name].add(
                embeddings=embedding,
                documents=[text],
                metadatas=[clean_metadata],
                ids=[doc_id]
            )
            return True
            
        except Exception as e:
            logger.error(f"Error adding to {collection_name}: {e}")
            return False
    
    def hybrid_search(
        self,
        query: str,
        category: Optional[str] = None,
        india_priority: bool = True,
        emergency_mode: bool = False,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Advanced hybrid search with priority routing
        
        Args:
            query: Search query
            category: Query category (medical, equipment, caregiving, etc.)
            india_priority: Prioritize India-specific content
            emergency_mode: Emergency query mode
            n_results: Number of results per collection
        """
        query_embedding = self.embedding_model.encode([query]).tolist()
        all_results = []
        
        # Determine collection search order based on context
        if emergency_mode:
            search_order = [
                'emergency_experiences', 
                'community_qa_pairs', 
                'medical_authoritative'
            ]
        elif category == 'india':
            search_order = [
                'community_qa_pairs', 
                'community_discussions', 
                'medical_community'
            ]
        elif category in ['medical', 'medication']:
            search_order = [
                'medical_authoritative', 
                'medical_clinical', 
                'community_qa_pairs'
            ]
        else:
            # Default: community first (real experiences), then medical
            search_order = [
                'community_qa_pairs', 
                'community_discussions', 
                'medical_authoritative', 
                'medical_clinical'
            ]
        
        # Search collections in priority order
        for collection_name in search_order:
            if collection_name not in self.collections:
                continue
            
            try:
                results = self.collections[collection_name].query(
                    query_embeddings=query_embedding,
                    n_results=min(n_results, 20),
                    include=["documents", "metadatas", "distances"]
                )
                
                if results['documents'] and results['documents'][0]:
                    for doc, metadata, distance in zip(
                        results['documents'][0],
                        results['metadatas'][0],
                        results['distances'][0]
                    ):
                        # Calculate relevance score
                        collection_priority = self.collection_config[collection_name]['priority']
                        trust_score = int(metadata.get('trust_score', 5))
                        
                        # Check India-specific flag
                        is_india = str(metadata.get('india_specific', 'False')).lower() == 'true'
                        is_emergency = str(metadata.get('emergency', 'False')).lower() == 'true'
                        
                        # Boost factors
                        india_boost = 1.5 if is_india and india_priority else 1.0
                        emergency_boost = 2.0 if is_emergency and emergency_mode else 1.0
                        
                        # Calculate final relevance score
                        relevance_score = (
                            (1 / (1 + distance)) *  # Distance score (0-1)
                            (collection_priority / 10) *  # Priority weight
                            (trust_score / 10) *  # Trust weight
                            india_boost *
                            emergency_boost
                        )
                        
                        all_results.append({
                            'content': doc,
                            'source': metadata.get('source', 'Unknown'),
                            'type': metadata.get('type', 'unknown'),
                            'trust_score': trust_score,
                            'collection': collection_name,
                            'distance': float(distance),
                            'relevance_score': relevance_score,
                            'india_specific': is_india,
                            'emergency': is_emergency,
                            'symptoms': metadata.get('symptoms', '[]'),
                            'costs': metadata.get('costs_mentioned', '[]'),
                            'chunk_type': metadata.get('chunk_type', 'general')
                        })
                        
            except Exception as e:
                logger.error(f"Search error in {collection_name}: {e}")
        
        # Sort by relevance score
        all_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Return top results with diversity
        return self._diversify_results(all_results, max_results=n_results)
    
    def _diversify_results(
        self, 
        results: List[Dict], 
        max_results: int = 10
    ) -> List[Dict]:
        """Ensure diversity in results (different sources/collections)"""
        diversified = []
        seen_sources = set()
        seen_collections = set()
        
        # First pass: high relevance with diversity
        for result in results:
            if len(diversified) >= max_results:
                break
            
            source = result['source']
            collection = result['collection']
            
            # Add if from new source or collection (for diversity)
            if source not in seen_sources or collection not in seen_collections:
                diversified.append(result)
                seen_sources.add(source)
                seen_collections.add(collection)
        
        # Second pass: fill remaining slots with best remaining results
        for result in results:
            if len(diversified) >= max_results:
                break
            if result not in diversified:
                diversified.append(result)
        
        return diversified[:max_results]
    
    def search(
        self, 
        query: str, 
        category: Optional[str] = None, 
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Simple search interface (wrapper for hybrid_search)"""
        return self.hybrid_search(
            query=query,
            category=category,
            india_priority=True,
            emergency_mode=False,
            n_results=n_results
        )
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics for all collections"""
        stats = {}
        total = 0
        for name, collection in self.collections.items():
            count = collection.count()
            stats[name] = count
            total += count
        stats['total'] = total
        return stats
    
    def clear_all_collections(self):
        """Clear all collections (use with caution!)"""
        for name in self.collections.keys():
            try:
                self.client.delete_collection(name)
            except Exception as e:
                logger.error(f"Error deleting {name}: {e}")
        
        # Reinitialize collections
        self.collections = {}
        for name, config in self.collection_config.items():
            self.collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={
                    'description': config['description'],
                    'priority': config['priority']
                }
            )
        logger.info("All collections cleared and reinitialized")

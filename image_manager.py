"""
Image Manager for ALS AI Assistant
Handles intelligent image selection based on query context
"""
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

class ImageManager:
    """Manages medical images and provides intelligent selection"""
    
    def __init__(self, images_dir: str = "ai_assistant_images"):
        """
        Initialize Image Manager
        
        Args:
            images_dir: Root directory for images
        """
        self.images_dir = Path(images_dir)
        self.catalog_file = self.images_dir / "catalog_metadata.json"
        self.catalog = {}
        self.category_keywords = {}
        
        # Initialize if directory exists
        if self.images_dir.exists():
            self._load_or_build_catalog()
            self._build_category_keywords()
        else:
            logger.warning(f"Images directory not found: {self.images_dir}")
    
    def _load_or_build_catalog(self):
        """Load existing catalog or build new one"""
        if self.catalog_file.exists():
            try:
                with open(self.catalog_file, 'r', encoding='utf-8') as f:
                    self.catalog = json.load(f)
                logger.info(f"✅ Loaded image catalog: {len(self.catalog)} images")
            except Exception as e:
                logger.error(f"Error loading catalog: {e}")
                self._build_catalog()
        else:
            self._build_catalog()
    
    def _build_catalog(self):
        """Scan directory and build image catalog"""
        logger.info("Building image catalog...")
        self.catalog = {}
        
        # Supported image formats
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        
        # Scan all subdirectories
        for category_dir in self.images_dir.iterdir():
            if not category_dir.is_dir():
                continue
            
            category = category_dir.name
            
            for image_path in category_dir.iterdir():
                if image_path.suffix.lower() in image_extensions:
                    # Create relative path from images_dir
                    rel_path = str(image_path.relative_to(self.images_dir)).replace('\\', '/')
                    
                    # Extract keywords from filename and category
                    keywords = self._extract_keywords(image_path.stem, category)
                    
                    self.catalog[rel_path] = {
                        "category": category,
                        "filename": image_path.name,
                        "keywords": keywords,
                        "description": self._generate_description(image_path.stem, category),
                        "priority": 5,  # Default priority
                        "full_path": str(image_path)
                    }
        
        # Save catalog
        self._save_catalog()
        logger.info(f"✅ Built catalog with {len(self.catalog)} images")
    
    def _extract_keywords(self, filename: str, category: str) -> List[str]:
        """Extract keywords from filename and category"""
        keywords = []
        
        # Add category keywords
        keywords.append(category)
        keywords.extend(category.split('_'))
        
        # Extract from filename (split by underscores, hyphens, spaces)
        name_parts = re.split(r'[_\-\s]+', filename.lower())
        keywords.extend(name_parts)
        
        # Add medical term mappings and equipment synonyms
        keyword_mappings = {
            'tt': ['tracheostomy', 'trach', 'tube'],
            'bipap': ['respiratory', 'breathing', 'ventilation', 'mask'],
            'peg': ['feeding', 'tube', 'nutrition', 'gastrostomy'],
            'wheelchair': ['mobility', 'movement', 'chair'],
            'eye': ['communication', 'gaze', 'tracker'],
            'suction': ['suctioning', 'secretion', 'airway'],
            'cuff': ['balloon', 'inflation', 'pressure'],
            'oxygen': ['o2', 'concentrator', 'respiratory'],
            'emergency': ['urgent', 'critical', 'protocol', 'crisis', 'immediate'],
            # Power/Electricity/Backup synonyms
            'ups': ['power', 'backup', 'battery', 'electricity', 'inverter', 'power supply', 'uninterruptible'],
            'power': ['electricity', 'backup', 'ups', 'battery', 'generator', 'supply', 'outage', 'cut'],
            'electricity': ['power', 'electric', 'backup', 'ups', 'supply', 'outage', 'cut'],
            'backup': ['power', 'ups', 'battery', 'emergency', 'reserve', 'electricity', 'generator'],
            'battery': ['backup', 'power', 'ups', 'charge', 'electricity'],
            'generator': ['backup', 'power', 'electricity', 'emergency'],
            'kva': ['power', 'capacity', 'rating', 'load'],
            'voltage': ['power', 'electricity', 'supply', 'input', 'output'],
            'inverter': ['ups', 'power', 'backup', 'battery'],
            # Emergency power-related
            'outage': ['power', 'electricity', 'cut', 'failure', 'blackout', 'emergency'],
            'blackout': ['power', 'outage', 'electricity', 'cut', 'failure']
        }
        
        for key, synonyms in keyword_mappings.items():
            if key in ' '.join(keywords):
                keywords.extend(synonyms)
        
        # Remove duplicates and empty strings
        keywords = list(set([k.strip() for k in keywords if k.strip()]))
        
        return keywords

    
    def _generate_description(self, filename: str, category: str) -> str:
        """Generate human-readable description"""
        # Convert filename to readable text
        name = filename.replace('_', ' ').replace('-', ' ').title()
        category_name = category.replace('_', ' ').title()
        return f"{name} - {category_name}"
    
    def _save_catalog(self):
        """Save catalog to JSON file"""
        try:
            with open(self.catalog_file, 'w', encoding='utf-8') as f:
                json.dump(self.catalog, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving catalog: {e}")
    
    def _build_category_keywords(self):
        """Build mapping of categories to their keywords"""
        self.category_keywords = {}
        for img_path, metadata in self.catalog.items():
            category = metadata['category']
            if category not in self.category_keywords:
                self.category_keywords[category] = set()
            self.category_keywords[category].update(metadata['keywords'])
    
    def suggest_images(self, query: str, context: str = "", max_images: int = 3) -> List[Dict[str, Any]]:
        """
        Suggest relevant images based on query and context
        
        Args:
            query: User's question
            context: Additional context from RAG
            max_images: Maximum number of images to return
            
        Returns:
            List of image metadata dictionaries
        """
        if not self.catalog:
            return []
        
        # Combine query and context for matching
        search_text = f"{query} {context}".lower()
        
        # Score each image
        scored_images = []
        for img_path, metadata in self.catalog.items():
            score = self._calculate_relevance_score(search_text, metadata)
            if score > 0:
                scored_images.append({
                    'path': img_path,
                    'score': score,
                    'metadata': metadata
                })
        
        # Sort by score and return top results
        scored_images.sort(key=lambda x: x['score'], reverse=True)
        
        # Format results
        results = []
        for item in scored_images[:max_images]:
            results.append({
                'path': item['path'],
                'description': item['metadata']['description'],
                'category': item['metadata']['category'],
                'alt_text': item['metadata']['description']
            })
        
        if results:
            logger.info(f"Selected {len(results)} images for query: {query[:50]}...")
        
        return results
    
    def _calculate_relevance_score(self, search_text: str, metadata: Dict) -> float:
        """Calculate relevance score for an image"""
        score = 0.0
        
        # Exact keyword matches (high weight)
        for keyword in metadata['keywords']:
            if keyword.lower() in search_text:
                score += 2.0
        
        # Category match (medium weight)
        if metadata['category'].replace('_', ' ') in search_text:
            score += 1.5
        
        # Filename match (medium weight)
        filename_words = metadata['filename'].lower().replace('_', ' ').split()
        for word in filename_words:
            if len(word) > 3 and word in search_text:
                score += 1.0
        
        # Priority boost
        score *= (metadata.get('priority', 5) / 5.0)
        
        return score
    
    def get_categories(self) -> List[str]:
        """Get list of available categories"""
        categories = set()
        for metadata in self.catalog.values():
            categories.add(metadata['category'])
        return sorted(list(categories))
    
    def get_images_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all images in a specific category"""
        results = []
        for img_path, metadata in self.catalog.items():
            if metadata['category'] == category:
                results.append({
                    'path': img_path,
                    'description': metadata['description'],
                    'category': category,
                    'keywords': metadata['keywords']
                })
        return results
    
    def add_image_metadata(self, image_path: str, keywords: List[str] = None, 
                          description: str = None, priority: int = 5):
        """
        Add or update metadata for an image
        
        Args:
            image_path: Relative path to image from images_dir
            keywords: Additional keywords for better matching
            description: Human-readable description
            priority: Priority score (1-10)
        """
        if image_path not in self.catalog:
            logger.warning(f"Image not in catalog: {image_path}")
            return
        
        if keywords:
            existing = set(self.catalog[image_path]['keywords'])
            existing.update(keywords)
            self.catalog[image_path]['keywords'] = list(existing)
        
        if description:
            self.catalog[image_path]['description'] = description
        
        if priority:
            self.catalog[image_path]['priority'] = max(1, min(10, priority))
        
        self._save_catalog()
        logger.info(f"Updated metadata for: {image_path}")
    
    def rebuild_catalog(self):
        """Force rebuild of catalog from filesystem"""
        logger.info("Rebuilding catalog...")
        self._build_catalog()
        self._build_category_keywords()
    
    def get_catalog_stats(self) -> Dict[str, Any]:
        """Get statistics about the image catalog"""
        stats = {
            'total_images': len(self.catalog),
            'categories': {},
            'total_keywords': 0
        }
        
        all_keywords = set()
        for metadata in self.catalog.values():
            category = metadata['category']
            if category not in stats['categories']:
                stats['categories'][category] = 0
            stats['categories'][category] += 1
            all_keywords.update(metadata['keywords'])
        
        stats['total_keywords'] = len(all_keywords)
        return stats


# Initialize global instance
_image_manager = None

def get_image_manager() -> ImageManager:
    """Get singleton image manager instance"""
    global _image_manager
    if _image_manager is None:
        _image_manager = ImageManager()
    return _image_manager


if __name__ == "__main__":
    # Test the image manager
    logging.basicConfig(level=logging.INFO)
    
    manager = ImageManager()
    
    # Print stats
    stats = manager.get_catalog_stats()
    print("\n📊 Image Catalog Statistics:")
    print(f"   Total Images: {stats['total_images']}")
    print(f"   Total Keywords: {stats['total_keywords']}")
    print(f"   Categories: {len(stats['categories'])}")
    for cat, count in stats['categories'].items():
        print(f"      - {cat}: {count} images")
    
    # Test image suggestion
    test_queries = [
        "What does a tracheostomy tube look like?",
        "How do I use BiPAP for my patient?",
        "Show me feeding tube equipment",
    ]
    
    print("\n🔍 Testing Image Suggestions:")
    for query in test_queries:
        images = manager.suggest_images(query, max_images=2)
        print(f"\n   Query: {query}")
        if images:
            for img in images:
                print(f"      ✓ {img['description']} ({img['category']})")
        else:
            print("      ✗ No images found")

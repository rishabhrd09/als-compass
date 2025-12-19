"""
Intelligent Data Ingestion with Semantic Chunking
Advanced ingestion with Q&A extraction, symptom detection, and hierarchical organization

Usage:
  python ingest_data_intelligent.py           # Interactive mode
  python ingest_data_intelligent.py --clear   # Auto-clear and rebuild
"""
import os
import yaml
import re
import logging
import argparse
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from tqdm import tqdm
import hashlib
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IntelligentDataIngestion:
    """Advanced data ingestion with semantic understanding"""
    
    def __init__(self):
        # Import here to avoid circular imports
        from vector_store_enhanced import EnhancedVectorStore
        self.store = EnhancedVectorStore()
        
        # ALS-specific patterns for intelligent chunking
        self.symptom_patterns = {
            'breathing': [r'breath', r'spo2', r'oxygen', r'bipap', r'ventilat', r'gasp', r'respiratory'],
            'feeding': [r'peg', r'ryles', r'feed', r'swallow', r'chok', r'aspirat', r'nutrition'],
            'secretions': [r'saliva', r'secret', r'mucus', r'suction', r'phlegm', r'foamy'],
            'equipment': [r'machine', r'device', r'ventilator', r'wheelchair', r'cost', r'₹', r'price'],
            'medication': [r'drug', r'medicine', r'dose', r'prescription', r'mg', r'tablet'],
            'emergency': [r'emergency', r'urgent', r'crisis', r'immediate', r'hospital', r'911', r'102'],
            'tracheostomy': [r'trach', r'cannula', r'stoma', r'cuff'],
            'mobility': [r'walk', r'movement', r'physiotherapy', r'exercise', r'wheelchair']
        }
    
    def scrub_pii(self, text: str) -> str:
        """Enhanced PII removal"""
        # Email
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
            '[EMAIL]', 
            text
        )
        # Phone - Indian and international formats
        text = re.sub(
            r'\b(?:\+\d{1,3}\s?)?\(?\d{3,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{4}\b', 
            '[PHONE]', 
            text
        )
        # Names with Dr./Mr./Mrs. prefix
        text = re.sub(
            r'\b(Dr\.|Mr\.|Mrs\.|Ms\.)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b', 
            r'\1 [NAME]', 
            text
        )
        # URLs
        text = re.sub(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 
            '[URL]', 
            text
        )
        return text
    
    def extract_context_metadata(self, text: str) -> Dict:
        """Extract semantic metadata from text"""
        metadata = {
            'symptoms': [],
            'equipment_mentioned': [],
            'costs_mentioned': [],
            'emergency_indicators': False,
            'india_specific': False,
            'has_solution': False,
            'has_question': False
        }
        
        text_lower = text.lower()
        
        # Detect symptoms
        for symptom, patterns in self.symptom_patterns.items():
            if any(re.search(pattern, text_lower) for pattern in patterns):
                metadata['symptoms'].append(symptom)
        
        # Detect costs (Indian context)
        if re.search(r'₹|rupees?|rs\.?|cost|price|lakh|thousand', text_lower):
            cost_matches = re.findall(r'₹\s*(\d+[\d,]*)', text)
            if cost_matches:
                metadata['costs_mentioned'] = [
                    int(c.replace(',', '')) for c in cost_matches
                ]
        
        # India-specific indicators
        india_terms = [
            'india', 'indian', 'delhi', 'mumbai', 'bangalore', 'chennai', 
            'hyderabad', 'kolkata', 'pune', 'aiims', 'apollo', 'fortis'
        ]
        if any(term in text_lower for term in india_terms):
            metadata['india_specific'] = True
        
        # Emergency indicators
        emergency_terms = [
            'emergency', 'urgent', 'immediate', 'crisis', 'cannot breathe',
            'spo2', 'choking', 'gasping', 'blue', 'unconscious'
        ]
        if any(term in text_lower for term in emergency_terms):
            metadata['emergency_indicators'] = True
        
        # Question vs Solution detection
        question_indicators = [
            '?', 'how to', 'what to', 'should i', 'can i', 'help',
            'suggest', 'advice', 'anyone', 'please'
        ]
        if any(q in text_lower for q in question_indicators):
            metadata['has_question'] = True
        
        solution_indicators = [
            'solution', 'worked', 'helped', 'recommend', 'suggest',
            'try', 'use', 'we did', 'i did', 'works well'
        ]
        if any(sol in text_lower for sol in solution_indicators):
            metadata['has_solution'] = True
        
        return metadata
    
    def chunk_whatsapp_conversation(self, messages: List[str]) -> List[Dict]:
        """Intelligently chunk WhatsApp conversations into semantic threads"""
        chunks = []
        current_thread = []
        thread_id = None
        
        for i, msg in enumerate(messages):
            # Skip short messages
            if len(msg.strip()) < 15:
                continue
            
            # Skip system messages
            if any(skip in msg.lower() for skip in [
                'joined using', 'left the group', 'changed the subject',
                'messages and calls are end-to-end encrypted',
                'created group', 'added', 'removed'
            ]):
                continue
            
            clean_msg = self.scrub_pii(msg)
            metadata = self.extract_context_metadata(clean_msg)
            
            # Start new thread on questions
            if metadata['has_question'] and len(current_thread) > 0:
                # Save previous thread
                if current_thread:
                    chunk = self._create_thread_chunk(current_thread, thread_id)
                    if chunk:
                        chunks.append(chunk)
                
                # Start new thread
                current_thread = [{
                    'text': clean_msg, 
                    'metadata': metadata, 
                    'index': i
                }]
                thread_id = hashlib.md5(clean_msg.encode()).hexdigest()[:12]
            else:
                # Continue current thread
                current_thread.append({
                    'text': clean_msg, 
                    'metadata': metadata, 
                    'index': i
                })
            
            # Max thread length (to avoid huge chunks)
            if len(current_thread) >= 8:
                chunk = self._create_thread_chunk(current_thread, thread_id)
                if chunk:
                    chunks.append(chunk)
                current_thread = []
                thread_id = None
        
        # Save final thread
        if current_thread:
            chunk = self._create_thread_chunk(current_thread, thread_id)
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def _create_thread_chunk(
        self, 
        thread: List[Dict], 
        thread_id: Optional[str]
    ) -> Optional[Dict]:
        """Create a semantic chunk from conversation thread"""
        if not thread:
            return None
        
        # Combine messages
        combined_text = "\n".join([msg['text'] for msg in thread])
        
        # Skip if too short
        if len(combined_text) < 50:
            return None
        
        # Aggregate metadata
        all_symptoms = set()
        all_costs = []
        is_emergency = False
        is_india = False
        has_q = False
        has_sol = False
        
        for msg in thread:
            meta = msg['metadata']
            all_symptoms.update(meta['symptoms'])
            all_costs.extend(meta.get('costs_mentioned', []))
            is_emergency = is_emergency or meta['emergency_indicators']
            is_india = is_india or meta['india_specific']
            has_q = has_q or meta['has_question']
            has_sol = has_sol or meta['has_solution']
        
        # Determine chunk type
        if has_q and has_sol:
            chunk_type = 'qa_pair'
        elif is_emergency:
            chunk_type = 'emergency_discussion'
        elif has_q:
            chunk_type = 'question'
        elif has_sol:
            chunk_type = 'solution'
        else:
            chunk_type = 'discussion'
        
        return {
            'text': combined_text,
            'thread_id': thread_id or hashlib.md5(combined_text.encode()).hexdigest()[:12],
            'chunk_type': chunk_type,
            'symptoms': list(all_symptoms),
            'costs': all_costs,
            'emergency': is_emergency,
            'india_specific': is_india,
            'message_count': len(thread),
            'avg_cost': sum(all_costs) / len(all_costs) if all_costs else None
        }
    
    def ingest_whatsapp_intelligently(
        self, 
        filepath: str, 
        limit: Optional[int] = None
    ) -> Dict[str, int]:
        """Intelligent WhatsApp ingestion with semantic chunking"""
        logger.info("📱 Intelligent WhatsApp ingestion starting...")
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        if limit:
            lines = lines[:limit]
        
        logger.info(f"   Processing {len(lines)} of {total_lines} messages...")
        
        # Chunk into semantic threads
        chunks = self.chunk_whatsapp_conversation(lines)
        logger.info(f"   Created {len(chunks)} semantic chunks")
        
        # Ingest into appropriate collections
        stats = {
            'qa_pairs': 0,
            'emergency_cases': 0,
            'general_discussions': 0,
            'total_chunks': len(chunks)
        }
        
        for chunk in tqdm(chunks, desc="Ingesting chunks"):
            if not chunk:
                continue
            
            # Determine collection based on chunk type
            if chunk['chunk_type'] == 'qa_pair':
                collection = 'community_qa_pairs'
                stats['qa_pairs'] += 1
            elif chunk['chunk_type'] == 'emergency_discussion':
                collection = 'emergency_experiences'
                stats['emergency_cases'] += 1
            else:
                collection = 'community_discussions'
                stats['general_discussions'] += 1
            
            # Add to vector store
            self.store.add_document(
                collection_name=collection,
                text=chunk['text'],
                metadata={
                    'source': 'ALS Care & Support India - WhatsApp',
                    'chunk_type': chunk['chunk_type'],
                    'symptoms': str(chunk['symptoms']),
                    'thread_id': chunk['thread_id'],
                    'emergency': chunk['emergency'],
                    'india_specific': chunk['india_specific'],
                    'costs_mentioned': str(chunk['costs']),
                    'avg_cost': chunk['avg_cost'] or 0,
                    'trust_score': 8 if chunk['chunk_type'] == 'qa_pair' else 7,
                    'ingestion_date': datetime.now().isoformat()
                },
                doc_id=f"whatsapp_{chunk['thread_id']}"
            )
        
        logger.info("✅ WhatsApp ingestion complete:")
        logger.info(f"   - Q&A pairs: {stats['qa_pairs']}")
        logger.info(f"   - Emergency cases: {stats['emergency_cases']}")
        logger.info(f"   - General discussions: {stats['general_discussions']}")
        
        return stats
    
    def ingest_medical_sources_hierarchical(self, filepath: str) -> Dict[str, int]:
        """Hierarchical medical source ingestion"""
        logger.info("📚 Loading medical sources hierarchically...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Map tiers to collections - match actual YAML keys (tier1, tier2, tier3)
        tier_collections = {
            'tier1': 'medical_authoritative',
            'tier2': 'medical_clinical',
            'tier3': 'medical_community'
        }
        
        count_by_tier = {'tier1': 0, 'tier2': 0, 'tier3': 0}
        
        sources = data.get('sources', {})
        
        # Handle both flat and nested source structures
        if isinstance(sources, list):
            # Flat list - all go to authoritative
            for source in sources:
                self._ingest_single_source(source, 'medical_authoritative', 'tier1')
                count_by_tier['tier1'] += 1
        elif isinstance(sources, dict):
            # Nested by tier
            for tier_name, tier_sources in sources.items():
                collection = tier_collections.get(tier_name, 'medical_community')
                if isinstance(tier_sources, list):
                    for source in tier_sources:
                        self._ingest_single_source(source, collection, tier_name)
                        if tier_name in count_by_tier:
                            count_by_tier[tier_name] += 1
        
        logger.info("✅ Medical sources loaded:")
        for tier, count in count_by_tier.items():
            if count > 0:
                logger.info(f"   - {tier}: {count} sources")
        
        return count_by_tier
    
    def _ingest_single_source(
        self, 
        source: Dict, 
        collection: str, 
        tier: str
    ):
        """Ingest a single medical source"""
        name = source.get('name', 'Unknown')
        
        text = f"Organization: {name}\n"
        text += f"Description: {source.get('description', '')}\n"
        text += f"URL: {source.get('url', '')}\n"
        
        topics = source.get('topics', [])
        if topics:
            text += f"Key Topics: {', '.join(topics)}\n"
        
        # Check India relevance
        india_relevant = (
            'india' in name.lower() or 
            'india' in source.get('description', '').lower()
        )
        
        self.store.add_document(
            collection_name=collection,
            text=text,
            metadata={
                'source': name,
                'type': 'medical_authority',
                'tier': tier,
                'trust_score': source.get('trust_score', 8),
                'url': source.get('url', ''),
                'topics': str(topics),
                'india_relevant': india_relevant,
                'ingestion_date': datetime.now().isoformat()
            },
            doc_id=f"{tier}_{name.replace(' ', '_').lower()[:30]}"
        )
    
    def ingest_faq_json(self, filepath: str) -> int:
        """Ingest FAQ JSON file into knowledge base"""
        logger.info(f"📋 Loading FAQ from {filepath}...")
        
        import json
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        count = 0
        source_name = data.get('source', 'FAQ')
        category = data.get('category', 'general')
        india_specific = data.get('india_specific', False)
        trust_score = data.get('trust_score', 8)
        
        # Process Q&A pairs
        qa_pairs = data.get('qa_pairs', [])
        
        for qa in qa_pairs:
            question = qa.get('question', '')
            answer = qa.get('answer', '')
            
            if not question or not answer:
                continue
            
            # Combine Q&A for better context
            text = f"Question: {question}\n\nAnswer: {answer}"
            
            # Extract costs if available
            costs = qa.get('costs', [])
            avg_cost = sum(costs) / len(costs) if costs else 0
            
            # Get metadata
            qa_metadata = qa.get('metadata', {})
            urgency = qa_metadata.get('urgency', 'medium')
            qa_type = qa_metadata.get('type', 'general')
            
            # Determine if emergency
            is_emergency = urgency == 'high' or 'emergency' in question.lower()
            
            # Add to vector store
            self.store.add_document(
                collection_name='community_qa_pairs',
                text=text,
                metadata={
                    'source': source_name,
                    'chunk_type': 'qa_pair',
                    'category': category,
                    'question': question,
                    'emergency': is_emergency,
                    'india_specific': india_specific,
                    'costs_mentioned': str(costs),
                    'avg_cost': avg_cost,
                    'trust_score': trust_score,
                    'qa_type': qa_type,
                    'urgency': urgency,
                    'ingestion_date': datetime.now().isoformat()
                },
                doc_id=f"faq_{hashlib.md5(question.encode()).hexdigest()[:12]}"
            )
            count += 1
        
        logger.info(f"✅ Loaded {count} FAQ entries from {filepath}")
        return count



def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Intelligent ALS Knowledge Base Ingestion'
    )
    parser.add_argument(
        '--clear', 
        action='store_true',
        help='Clear database directory and rebuild without prompts'
    )
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("  🧠 INTELLIGENT ALS KNOWLEDGE BASE INGESTION")
    print("     Advanced RAG with Semantic Chunking")
    print("=" * 80)
    print()
    
    # Handle --clear flag: delete database directory first
    if args.clear:
        from pathlib import Path
        db_path = Path("./chroma_db_enhanced")
        if db_path.exists():
            print("🗑️  --clear flag detected")
            print(f"   Deleting database at {db_path}...")
            shutil.rmtree(db_path)
            print("   ✅ Database deleted")
            print()
        else:
            print("ℹ️  --clear flag detected but no database found")
            print()
    
    ingestion = IntelligentDataIngestion()
    
    # Check files
    whatsapp_paths = [
        Path("data/whatsapp_anonymized.txt"),
        Path("data/whatsapp_als_care_india.txt")
    ]
    sources_path = Path("data/sources.yaml")
    
    whatsapp_path = None
    for wp in whatsapp_paths:
        if wp.exists():
            whatsapp_path = wp
            break
    
    print("📁 Data files:")
    print(f"   {'✅' if whatsapp_path else '❌'} WhatsApp data: {whatsapp_path or 'Not found'}")
    print(f"   {'✅' if sources_path.exists() else '❌'} {sources_path}")
    print()
    
    if not whatsapp_path and not sources_path.exists():
        print("❌ No data files found!")
        return
    
    # Show current stats
    print("📊 Current database status:")
    stats = ingestion.store.get_collection_stats()
    for name, count in stats.items():
        print(f"   - {name}: {count}")
    print()
    
    # Confirm rebuild
    print("⚠️  This will rebuild the enhanced knowledge base.")
    print("    (Original database in chroma_db/ is untouched)")
    response = input("\nType 'REBUILD' to confirm: ")
    
    if response != 'REBUILD':
        print("Cancelled.")
        return
    
    print("\n" + "=" * 80)
    print("  STARTING INTELLIGENT INGESTION")
    print("=" * 80 + "\n")
    
    # Clear and rebuild
    print("🗑️  Clearing enhanced collections...")
    ingestion.store.clear_all_collections()
    
    # Ingest medical sources
    if sources_path.exists():
        ingestion.ingest_medical_sources_hierarchical(str(sources_path))
    
    # Ingest BiPAP FAQ
    bipap_faq_path = Path("data/bipap_faq.json")
    if bipap_faq_path.exists():
        ingestion.ingest_faq_json(str(bipap_faq_path))
    
    # Ingest WhatsApp with intelligence
    if whatsapp_path:
        stats = ingestion.ingest_whatsapp_intelligently(
            str(whatsapp_path), 
            limit=5000  # Process up to 5000 messages
        )

    
    # Final stats
    print("\n" + "=" * 80)
    print("  ✅ INTELLIGENT INGESTION COMPLETE!")
    print("=" * 80)
    
    final_stats = ingestion.store.get_collection_stats()
    print("\n📊 Final database statistics:")
    for name, count in final_stats.items():
        print(f"   - {name}: {count}")
    
    print("\n🚀 Next steps:")
    print("   1. Run: python app.py")
    print("   2. Visit: http://127.0.0.1:5000/ai-assistant")
    print("   3. Try queries with emergency or India-specific context!")
    print()


if __name__ == "__main__":
    main()

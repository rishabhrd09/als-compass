"""
FINAL OPTIMIZED Data Ingestion Script
- Fast processing (limits to 500 messages)
- Progress bars
- Clear warnings
- Error handling
"""
import os
import yaml
import re
import logging
from pathlib import Path
from vector_store import VectorStore
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrub_pii(text: str) -> str:
    """Remove privacy-sensitive information"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b(?:\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
    text = re.sub(email_pattern, '[EMAIL]', text)
    text = re.sub(phone_pattern, '[PHONE]', text)
    return text

def ingest_medical_sources(store: VectorStore):
    """Load medical sources"""
    sources_path = Path("data/sources.yaml")
    
    if not sources_path.exists():
        logger.warning("⚠️ data/sources.yaml not found - skipping medical sources")
        return 0

    try:
        logger.info("📚 Loading medical sources...")
        with open(sources_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        count = 0
        for tier_name, tier_sources in data.get('sources', {}).items():
            for source in tier_sources:
                text = f"Source: {source['name']}\n"
                text += f"Description: {source.get('description', '')}\n"
                
                store.add_to_collection(
                    collection_name="medical_knowledge",
                    text=text,
                    metadata={
                        'source': source['name'],
                        'type': 'medical_authority',
                        'tier': tier_name,
                        'trust_score': source.get('trust_score', 8)
                    },
                    doc_id=f"{tier_name}_{source['name'].replace(' ', '_').lower()}"
                )
                count += 1
        
        logger.info(f"✅ Loaded {count} medical sources")
        return count
        
    except Exception as e:
        logger.error(f"❌ Error loading medical sources: {e}")
        return 0

def ingest_whatsapp_data(store: VectorStore, max_lines=500):
    """Load WhatsApp chats - LIMITED & FAST"""
    chat_path = Path("data/whatsapp_anonymized.txt")
    
    if not chat_path.exists():
        logger.warning("⚠️ data/whatsapp_anonymized.txt not found - skipping WhatsApp")
        return 0

    try:
        logger.info(f"💬 Loading WhatsApp (max {max_lines} messages)...")
        
        with open(chat_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        total = len(lines)
        logger.info(f"   Found {total} total lines in file")
        
        lines_to_process = [l for l in lines[:max_lines] if len(l.strip()) >= 10]
        logger.info(f"   Processing {len(lines_to_process)} valid messages")
        
        count = 0
        for i, line in enumerate(tqdm(lines_to_process, desc="Processing messages")):
            clean_text = scrub_pii(line.strip())
            
            store.add_to_collection(
                collection_name="community_experiences",
                text=clean_text,
                metadata={
                    'source': 'ALS Care and Support India - WhatsApp',
                    'type': 'whatsapp_chat',
                    'trust_score': 7
                },
                doc_id=f"whatsapp_{i}"
            )
            count += 1
        
        logger.info(f"✅ Loaded {count} WhatsApp messages")
        if total > max_lines:
            logger.info(f"   ℹ️  Skipped {total - max_lines} lines for performance")
        
        return count
        
    except Exception as e:
        logger.error(f"❌ Error loading WhatsApp: {e}")
        return 0

def main():
    print("\n" + "="*70)
    print("  📥 ALS CAREGIVER'S COMPASS - DATA INGESTION")
    print("="*70)
    print()
    
    # Check data files exist
    print("📁 Checking data files...\n")
    
    sources_exists = Path("data/sources.yaml").exists()
    whatsapp_exists = Path("data/whatsapp_anonymized.txt").exists()
    
    print(f"   {'✅' if sources_exists else '❌'} data/sources.yaml")
    print(f"   {'✅' if whatsapp_exists else '❌'} data/whatsapp_anonymized.txt")
    print()
    
    if not sources_exists and not whatsapp_exists:
        print("❌ ERROR: No data files found!")
        print("\n   Create these files in the data/ folder:")
        print("     - data/sources.yaml")
        print("     - data/whatsapp_anonymized.txt\n")
        return
    
    # Initialize vector store
    try:
        print("🔧 Initializing database...\n")
        store = VectorStore(persist_dir="./chroma_db")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}\n")
        return
    
    # Check existing data
    medical_count = store.get_collection_count("medical_knowledge")
    community_count = store.get_collection_count("community_experiences")
    
    if medical_count > 0 or community_count > 0:
        print("⚠️" * 35)
        print()
        print("  🚨 WARNING - EXISTING DATA FOUND! 🚨")
        print()
        print(f"  Current database contains:")
        print(f"    - Medical sources: {medical_count} items")
        print(f"    - Community chats: {community_count} items")
        print()
        print("  This operation will:")
        print("    ❌ DELETE all existing data")
        print("    ✅ Load new data from files")
        print()
        print("⚠️" * 35)
        print()
        
        print("Type 'OVERWRITE' to confirm deletion and reload:")
        response = input(">> ").strip()
        
        if response != 'OVERWRITE':
            print("\n❌ Cancelled. Database not modified.\n")
            return
        
        print("\n🗑️  Clearing existing data...")
        store.clear_collection("medical_knowledge")
        store.clear_collection("community_experiences")
        print("✅ Cleared\n")
    
    # Ingest data
    print("="*70)
    print("Starting data ingestion...")
    print("="*70)
    print()
    
    medical_added = 0
    community_added = 0
    
    if sources_exists:
        medical_added = ingest_medical_sources(store)
    
    if whatsapp_exists:
        community_added = ingest_whatsapp_data(store, max_lines=500)
    
    # Final status
    print()
    print("="*70)
    print("📊 INGESTION COMPLETE!")
    print("="*70)
    print()
    print(f"✅ Medical sources:     {medical_added} loaded")
    print(f"✅ Community messages:  {community_added} loaded")
    print()
    print("="*70)
    print()
    print("🚀 Next step:")
    print("   Run: python app.py")
    print("   Then visit: http://127.0.0.1:5000")
    print()
    print("="*70)
    print()

if __name__ == "__main__":
    main()

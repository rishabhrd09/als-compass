"""
Database Management Script
Clear and rebuild ChromaDB
"""
import os
import shutil
from pathlib import Path

def clear_database():
    """Clear ChromaDB database"""
    db_path = Path("./chroma_db")
    
    if db_path.exists():
        print("🗑️  Clearing ChromaDB database...")
        shutil.rmtree(db_path)
        print("✅ Database cleared successfully")
    else:
        print("ℹ️  No database found to clear")

def verify_data_files():
    """Check if required data files exist"""
    data_dir = Path("./data")
    
    required_files = {
        "sources.yaml": "Medical sources metadata",
        "whatsapp_anonymized.txt": "WhatsApp community chats (or whatsapp_als_care_india.txt)"
    }
    
    print("\n📁 Checking data files...")
    all_exist = True
    
    for filename, description in required_files.items():
        file_path = data_dir / filename
        if file_path.exists():
            print(f"✅ {filename} - {description}")
        else:
            print(f"❌ {filename} MISSING - {description}")
            all_exist = False
    
    return all_exist

def check_database_status():
    """Check current database status"""
    try:
        from vector_store import VectorStore
        store = VectorStore()
        
        medical_count = store.get_collection_count("medical_knowledge")
        community_count = store.get_collection_count("community_experiences")
        
        print("\n📊 Current Database Status:")
        print(f"   Medical Sources: {medical_count}")
        print(f"   Community Chats: {community_count}")
        
        return medical_count > 0 or community_count > 0
    except Exception as e:
        print(f"\n❌ Error checking database: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  ⚠️  DANGER ZONE - Database Management")
    print("="*60)
    print()
    
    # Check current status first
    print("📊 Checking current database status...\n")
    has_db = check_database_status()
    print()
    
    if not has_db:
        print("ℹ️  No database found. Nothing to clear.")
        print("\n💡 To create database, run: python ingest_data_fast.py\n")
        return
    
    # Show data files status
    data_exists = verify_data_files()
    print()
    
    # WARNING
    print("⚠️" * 30)
    print()
    print("  🚨 WARNING - THIS WILL DELETE ALL YOUR DATA! 🚨")
    print()
    print("  What will be deleted:")
    print("    ❌ All medical sources from database")
    print("    ❌ All WhatsApp community chats from database")
    print("    ❌ All vector embeddings")
    print()
    print("  What happens next:")
    if data_exists:
        print("    ✅ You can re-run: python ingest_data_fast.py")
    else:
        print("    ⚠️  WARNING: data/ files are MISSING!")
        print("    ⚠️  You won't be able to reload data!")
    print()
    print("⚠️" * 30)
    print()
    
    # Triple confirmation
    print("Type 'DELETE' (in capitals) to confirm deletion:")
    response1 = input(">> ").strip()
    
    if response1 != 'DELETE':
        print("\n❌ Cancelled. Database not cleared.\n")
        return
    
    print("\nAre you ABSOLUTELY sure? (yes/no):")
    response2 = input(">> ").lower().strip()
    
    if response2 not in ['yes', 'y']:
        print("\n❌ Cancelled. Database not cleared.\n")
        return
    
    # Clear database
    print("\n🗑️  Clearing database...")
    clear_database()
    
    print("\n" + "="*60)
    print("✅ Database cleared successfully!")
    print("="*60)
    
    if data_exists:
        print("\n💡 Next step:")
        print("   Run: python ingest_data_fast.py")
        print("   This will reload your data into the database\n")
    else:
        print("\n⚠️  WARNING: Data files missing in ./data/ folder!")
        print("   You need these files to reload data:")
        print("     - data/sources.yaml")
        print("     - data/whatsapp_anonymized.txt\n")

if __name__ == "__main__":
    main()

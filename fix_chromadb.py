"""
Fix ChromaDB Schema Issue
Deletes and rebuilds the ChromaDB database to fix "no such column: collections.topic" error
"""
import shutil
from pathlib import Path

def fix_chromadb():
    db_path = Path("./chroma_db_enhanced")
    
    if db_path.exists():
        print(f"🗑️  Deleting corrupted database at {db_path}")
        shutil.rmtree(db_path)
        print("✅ Database deleted successfully")
    else:
        print("⚠️  Database directory not found")
    
    print("\n📝 Next step: Run data ingestion to rebuild:")
    print("   python ingest_data_intelligent.py")

if __name__ == "__main__":
    response = input("⚠️  This will DELETE the entire ChromaDB database. Continue? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        fix_chromadb()
    else:
        print("❌ Operation cancelled")

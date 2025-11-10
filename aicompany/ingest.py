"""
AICompany policy document ingestion to Supabase
"""
import json
import sys
sys.path.append('..')

from common.database import ingest_chunks

def ingest_aicompany_policies(chunks_file: str = "./db/aicompany-chunks.json"):
    """
    Ingest AICompany policy chunks into Supabase.
    
    Args:
        chunks_file: Path to the JSON file with chunks
    """
    # Load chunks
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} AICompany policy chunks")
    
    # Ingest with section-specific fields
    result = ingest_chunks(
        chunks=chunks,
        table_name='aicompany_policies',
        chunk_fields=['section_number', 'section_title'],
        batch_size=10
    )
    
    return result

if __name__ == "__main__":
    ingest_aicompany_policies()

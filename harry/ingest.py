"""
Harry Potter screenplay ingestion to Supabase
"""
import json
import sys
sys.path.append('..')

from common.database import ingest_chunks

def ingest_harry_potter(chunks_file: str = "./db/harry-potter-chunks.json"):
    """
    Ingest Harry Potter screenplay chunks into Supabase.
    
    Args:
        chunks_file: Path to the JSON file with chunks
    """
    # Load chunks
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} Harry Potter screenplay chunks")
    
    # Ingest with scene-specific fields
    result = ingest_chunks(
        chunks=chunks,
        table_name='harry_potter',
        chunk_fields=['scene_number', 'scene_title'],
        batch_size=10
    )
    
    return result

if __name__ == "__main__":
    ingest_harry_potter()

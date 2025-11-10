"""
Shared database operations for Supabase
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import time
from tqdm import tqdm
from .embeddings import generate_embedding

load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def ingest_chunks(chunks: list[dict], table_name: str = 'documents', 
                 chunk_fields: list[str] = None, batch_size: int = 10):
    """
    Insert chunks into Supabase with embeddings.
    
    Args:
        chunks: List of chunk dictionaries with 'text' and metadata
        table_name: Name of the Supabase table
        chunk_fields: List of additional fields to extract from chunks (e.g., ['scene_number', 'scene_title'])
        batch_size: Number of chunks to process in each batch
    
    Returns:
        Dictionary with success and failure counts
    """
    print(f"Ingesting {len(chunks)} chunks into '{table_name}' table...")
    
    successful = 0
    failed = 0
    
    # Process in batches with progress bar
    for i in tqdm(range(0, len(chunks), batch_size)):
        batch = chunks[i:i + batch_size]
        
        for chunk in batch:
            try:
                # Generate embedding
                embedding = generate_embedding(chunk['text'])
                
                # Prepare base data for insertion
                data = {
                    'chunk_id': chunk['id'],
                    'content': chunk['text'],
                    'embedding': embedding,
                    'metadata': chunk['metadata']
                }
                
                # Add any additional fields specified
                if chunk_fields:
                    for field in chunk_fields:
                        if field in chunk:
                            data[field] = chunk[field]
                
                # Insert into Supabase
                result = supabase.table(table_name).insert(data).execute()
                successful += 1
                
            except Exception as e:
                print(f"\nError processing chunk {chunk['id']}: {e}")
                failed += 1
        
        # Small delay to avoid rate limits
        time.sleep(0.5)
    
    print(f"\n✅ Ingestion complete!")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Total: {len(chunks)}")
    
    return {'successful': successful, 'failed': failed, 'total': len(chunks)}

def search_documents(query: str, table_name: str = 'documents', 
                    match_threshold: float = 0.45, match_count: int = 5):
    """
    Search documents using vector similarity.
    
    Args:
        query: The search query
        table_name: Name of the Supabase table
        match_threshold: Minimum similarity threshold
        match_count: Number of results to return
    
    Returns:
        List of matching documents
    """
    # Generate embedding for query
    query_embedding = generate_embedding(query)
    
    # Search in Supabase using RPC function
    result = supabase.rpc(
        'match_documents',
        {
            'query_embedding': query_embedding,
            'match_threshold': match_threshold,
            'match_count': match_count
        }
    ).execute()
    
    return result.data

def get_supabase_client():
    """Get the initialized Supabase client."""
    return supabase

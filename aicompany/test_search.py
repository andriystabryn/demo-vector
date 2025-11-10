"""
Test search functionality for AICompany policies
"""
import sys
sys.path.append('..')

from common.database import search_documents, generate_embedding

def test_search(query: str):
    """Test a search query and show results"""
    print(f"\n{'='*60}")
    print(f"Testing query: '{query}'")
    print(f"{'='*60}\n")
    
    # Try different thresholds
    thresholds = [0.3, 0.4, 0.45, 0.5]
    
    for threshold in thresholds:
        print(f"\n--- Threshold: {threshold} ---")
        
        # Generate embedding
        query_embedding = generate_embedding(query)
        
        # Search
        from common.database import get_supabase_client
        supabase = get_supabase_client()
        
        result = supabase.rpc(
            'match_aicompany_policies',
            {
                'query_embedding': query_embedding,
                'match_threshold': threshold,
                'match_count': 5
            }
        ).execute()
        
        if result.data:
            print(f"Found {len(result.data)} results:")
            for i, doc in enumerate(result.data, 1):
                print(f"\n{i}. Section {doc['section_number']}: {doc['section_title']}")
                print(f"   Similarity: {doc['similarity']:.3f}")
                print(f"   Preview: {doc['content'][:150]}...")
        else:
            print("No results found")

if __name__ == "__main__":
    # Test queries
    queries = [
        "logging time",
        "time tracking",
        "how to log hours",
        "track working hours",
        "Jira time entries"
    ]
    
    for query in queries:
        test_search(query)
        print("\n" + "="*60 + "\n")

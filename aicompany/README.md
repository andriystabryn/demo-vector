# RAG demo
Our goal is to build AICompany policies assistant who knows everything about the company policies. 
We are going to build a RAG (Retrieval Augmented Generation) system using Supabase and OpenAI.


## Prepare the Vector DB:
1. Show the content of the text file:

2. Create the Supabase DB:
```SQL
-- Enable the pgvector extension to work with embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- AICompany Policies Table
CREATE TABLE aicompany_policies (
  id BIGSERIAL PRIMARY KEY,
  chunk_id TEXT NOT NULL,
  content TEXT NOT NULL,
  embedding VECTOR(1536),
  metadata JSONB,
  section_number INTEGER,
  section_title TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on section_number for faster queries
CREATE INDEX idx_aicompany_section_number ON aicompany_policies(section_number);

-- Create vector similarity search index
CREATE INDEX ON aicompany_policies USING ivfflat (embedding vector_cosine_ops);

-- Create RPC function for similarity search
DROP FUNCTION IF EXISTS match_aicompany_policies(vector, double precision, integer);

CREATE OR REPLACE FUNCTION match_aicompany_policies (
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 5
)
RETURNS TABLE (
  id bigint,
  chunk_id text,
  content text,
  metadata jsonb,
  section_number integer,
  section_title text,
  similarity float
)
LANGUAGE sql STABLE
AS $$
  SELECT
    aicompany_policies.id,
    aicompany_policies.chunk_id,
    aicompany_policies.content,
    aicompany_policies.metadata,
    aicompany_policies.section_number,
    aicompany_policies.section_title,
    1 - (aicompany_policies.embedding <=> query_embedding) AS similarity
  FROM aicompany_policies
  WHERE 1 - (aicompany_policies.embedding <=> query_embedding) > match_threshold
  ORDER BY aicompany_policies.embedding <=> query_embedding
  LIMIT match_count;
$$;
```

3. Chunk the movie script:
```bash
python chunk_text.py
```

4. Ingest the chunks:
```bash
python ingest.py
```

5. Test the query, in two variants:

Without a RAG:
```bash
python 1.py
```

With a RAG:
```bash
python 2.py
```

## Questions:
   1. How do I track my working hours?
   2. What time should I be in the office?
   3. How much is the referral bonus?
   4. What happens when I leave the company?
   5. What are the password requirements?

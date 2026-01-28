# RAG demo
Our goal is to build Harry Potter fan assistant who knows everything about the movie. 
We are going to build a RAG (Retrieval Augmented Generation) system using Supabase and OpenAI.
The perfect project to show vector DB limitations.

## Prepare the Vector DB:
1. Show the content of the text file:

2. Create the DB in Supabase:
```SQL
-- Enable the pgvector extension to work with embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Harry Potter Screenplay Table
CREATE TABLE harry_potter (
  id BIGSERIAL PRIMARY KEY,
  chunk_id TEXT NOT NULL,
  content TEXT NOT NULL,
  embedding VECTOR(1536),
  metadata JSONB,
  scene_number INTEGER,
  scene_title TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on scene_number for faster queries
CREATE INDEX idx_harry_scene_number ON harry_potter(scene_number);

-- Create vector similarity search index
CREATE INDEX ON harry_potter USING ivfflat (embedding vector_cosine_ops);

-- Create RPC function for similarity search
DROP FUNCTION IF EXISTS match_harry_potter(vector, double precision, integer);

CREATE OR REPLACE FUNCTION match_harry_potter (
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 5
)
RETURNS TABLE (
  id bigint,
  chunk_id text,
  content text,
  metadata jsonb,
  scene_number integer,
  scene_title text,
  similarity float
)
LANGUAGE sql STABLE
AS $$
  SELECT
    harry_potter.id,
    harry_potter.chunk_id,
    harry_potter.content,
    harry_potter.metadata,
    harry_potter.scene_number,
    harry_potter.scene_title,
    1 - (harry_potter.embedding <=> query_embedding) AS similarity
  FROM harry_potter
  WHERE 1 - (harry_potter.embedding <=> query_embedding) > match_threshold
  ORDER BY harry_potter.embedding <=> query_embedding
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
1. Working questions:
    1. What is Dumbledore's first line in the movie?
    2. What does Hagrid say about Dumbledore?
    3. What does Hermione do on the train?
    4. How many times does Dumbledore say something? - not ideal, but better than general. The problem is that we get from the vector only the first 5 results. Ideally would be to create a separate tool for calculation.
    5. Did Harry mention Severus in the movie?
    6. How many times is the Wingardium Leviosa spell used in the movie?

2. Not working questions / Bad results:
   1. What is hidden at Hogwarts?
   2. What is the last word of Harry?
   3. How many times does Hermione say something? I need a number.
   4. Does the cat appear in the movies? And how many times? 
   5. What does Harry say to Ron in the last scene?
   6. How many times did Harry call Ron?
   7. What magic spell is used the most in the movie?
   8. Can you give me the full list of magic spells used in the movie?

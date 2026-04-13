-- Drop old function and replace with hybrid search using RRF
DROP FUNCTION IF EXISTS match_chunks(vector, double precision, integer, uuid);

CREATE OR REPLACE FUNCTION match_chunks(
    query_embedding vector(1536),
    match_threshold float,
    match_count int,
    p_user_id uuid,
    query_text text DEFAULT ''
)
RETURNS TABLE (
    id uuid,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE sql
SECURITY DEFINER
AS $$
    WITH vector_ranked AS (
        SELECT
            chunks.id,
            ROW_NUMBER() OVER (ORDER BY chunks.embedding <=> query_embedding) AS rank
        FROM chunks
        WHERE chunks.user_id = p_user_id
          AND 1 - (chunks.embedding <=> query_embedding) > match_threshold
    ),
    keyword_ranked AS (
        SELECT
            chunks.id,
            ROW_NUMBER() OVER (ORDER BY ts_rank(chunks.fts, plainto_tsquery('english', query_text)) DESC) AS rank
        FROM chunks
        WHERE chunks.user_id = p_user_id
          AND (query_text = '' OR chunks.fts @@ plainto_tsquery('english', query_text))
    ),
    rrf AS (
        SELECT
            COALESCE(v.id, k.id) AS id,
            COALESCE(1.0 / (60 + v.rank), 0) + COALESCE(1.0 / (60 + k.rank), 0) AS score
        FROM vector_ranked v
        FULL OUTER JOIN keyword_ranked k ON v.id = k.id
    )
    SELECT
        chunks.id,
        chunks.content,
        chunks.metadata,
        rrf.score AS similarity
    FROM rrf
    JOIN chunks ON chunks.id = rrf.id
    ORDER BY rrf.score DESC
    LIMIT match_count;
$$;

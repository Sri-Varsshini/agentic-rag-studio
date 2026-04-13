-- Add content hash for deduplication
ALTER TABLE documents ADD COLUMN IF NOT EXISTS content_hash TEXT;

-- Index for fast hash lookups
CREATE INDEX IF NOT EXISTS idx_documents_content_hash ON documents(user_id, content_hash);

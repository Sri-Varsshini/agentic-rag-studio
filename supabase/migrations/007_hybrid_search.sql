-- Add tsvector column for full-text keyword search
-- Using trigger-based update instead of GENERATED ALWAYS to avoid maintenance_work_mem limits
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS fts tsvector;

-- Trigger function to keep fts in sync
CREATE OR REPLACE FUNCTION chunks_fts_update() RETURNS trigger AS $$
BEGIN
    NEW.fts := to_tsvector('english', NEW.content);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS chunks_fts_trigger ON chunks;
CREATE TRIGGER chunks_fts_trigger
    BEFORE INSERT OR UPDATE OF content ON chunks
    FOR EACH ROW EXECUTE FUNCTION chunks_fts_update();

-- Backfill existing rows in small batches to stay within memory limits
DO $$
DECLARE
    batch_size INT := 100;
    offset_val INT := 0;
    rows_updated INT;
BEGIN
    LOOP
        UPDATE chunks
        SET fts = to_tsvector('english', content)
        WHERE id IN (
            SELECT id FROM chunks
            WHERE fts IS NULL
            LIMIT batch_size
        );
        GET DIAGNOSTICS rows_updated = ROW_COUNT;
        EXIT WHEN rows_updated = 0;
    END LOOP;
END;
$$;

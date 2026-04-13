from openai import OpenAI
from supabase import Client
from config import settings
from services.metadata_service import extract_metadata
from services.parser_service import parse_document
import tiktoken
import hashlib

client = OpenAI(api_key=settings.openai_api_key)
EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def compute_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def chunk_text(text: str) -> list[str]:
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + CHUNK_SIZE, len(tokens))
        chunks.append(enc.decode(tokens[start:end]))
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in response.data]


def ingest_document(supabase: Client, document_id: str, user_id: str, text: str, filename: str = ""):
    try:
        chunks = chunk_text(text)
        embeddings = embed_texts(chunks)

        rows = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            metadata = extract_metadata(chunk, filename)
            rows.append({
                "document_id": document_id,
                "user_id": user_id,
                "content": chunk,
                "embedding": embedding,
                "chunk_index": i,
                "metadata": metadata,
            })

        for i in range(0, len(rows), 50):
            supabase.table("chunks").insert(rows[i:i+50]).execute()

        supabase.table("documents").update({
            "status": "completed",
            "chunk_count": len(chunks)
        }).eq("id", document_id).execute()

    except Exception as e:
        supabase.table("documents").update({
            "status": "failed",
            "error": str(e)
        }).eq("id", document_id).execute()
        raise


def check_and_ingest(supabase: Client, user_id: str, filename: str, content: bytes, document_id: str):
    """
    Record manager logic:
    - Same file, same hash → skip ingestion
    - Same file, different hash → delete old chunks, re-ingest
    - New file → ingest normally
    """
    content_hash = compute_hash(content)

    # Look for existing document with same filename for this user (excluding current upload)
    existing = supabase.table("documents") \
        .select("id, content_hash") \
        .eq("user_id", user_id) \
        .eq("filename", filename) \
        .neq("id", document_id) \
        .execute()

    if existing.data:
        old_doc = existing.data[0]

        if old_doc["content_hash"] == content_hash:
            # Same content — skip ingestion, mark as completed immediately
            print(f"[record_manager] '{filename}' unchanged, skipping ingestion")
            supabase.table("documents").update({
                "status": "completed",
                "content_hash": content_hash,
                "chunk_count": 0
            }).eq("id", document_id).execute()

            # Delete the duplicate upload, keep the original
            supabase.table("documents").delete().eq("id", document_id).execute()
            return

        else:
            # Content changed — delete old document and its chunks
            print(f"[record_manager] '{filename}' changed, re-ingesting")
            supabase.table("documents").delete().eq("id", old_doc["id"]).execute()

    # Store hash then ingest
    supabase.table("documents").update({"content_hash": content_hash}).eq("id", document_id).execute()

    text = parse_document(content, filename)
    ingest_document(supabase, document_id, user_id, text, filename)

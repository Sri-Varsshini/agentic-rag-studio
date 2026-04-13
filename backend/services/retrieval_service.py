from openai import OpenAI
from supabase import Client
from config import settings

try:
    from sentence_transformers import CrossEncoder
    _CROSSENCODER_AVAILABLE = True
except ImportError:
    _CROSSENCODER_AVAILABLE = False
    print("[retrieval] sentence-transformers not installed, reranking disabled")

client = OpenAI(api_key=settings.openai_api_key)
EMBEDDING_MODEL = "text-embedding-3-small"
TOP_K = 10
FINAL_K = 5
SIMILARITY_THRESHOLD = 0.3

_reranker: CrossEncoder | None = None

def _get_reranker() -> "CrossEncoder":
    global _reranker
    if not _CROSSENCODER_AVAILABLE:
        raise RuntimeError("sentence-transformers not installed. Run: pip install sentence-transformers")
    if _reranker is None:
        from sentence_transformers import CrossEncoder
        _reranker = CrossEncoder(settings.reranker_model)
    return _reranker


def retrieve_context(supabase: Client, user_id: str, query: str) -> str:
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=query)
    query_embedding = response.data[0].embedding
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    result = supabase.rpc("match_chunks", {
        "query_embedding": embedding_str,
        "match_threshold": SIMILARITY_THRESHOLD,
        "match_count": TOP_K,
        "p_user_id": user_id,
        "query_text": query,
    }).execute()

    chunks = result.data or []
    print(f"[retrieval] hybrid found {len(chunks)} chunks")

    if not chunks:
        return ""

    if settings.reranker_enabled:
        chunks = _rerank(query, chunks)

    chunks = chunks[:FINAL_K]

    parts = []
    for row in chunks:
        meta = row.get("metadata") or {}
        header_parts = []
        if meta.get("title"):
            header_parts.append(f"Title: {meta['title']}")
        if meta.get("document_type"):
            header_parts.append(f"Type: {meta['document_type']}")
        if meta.get("date"):
            header_parts.append(f"Date: {meta['date']}")
        if meta.get("keywords"):
            header_parts.append(f"Keywords: {', '.join(meta['keywords'])}")
        header = "\n".join(header_parts)
        parts.append(f"{header}\n\n{row['content']}" if header else row["content"])

    return "\n\n---\n\n".join(parts)


def _rerank(query: str, chunks: list[dict]) -> list[dict]:
    reranker = _get_reranker()
    docs = [row["content"] for row in chunks]
    scores = reranker.predict([(query, doc) for doc in docs])
    ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
    reranked = [chunk for _, chunk in ranked[:FINAL_K]]
    print(f"[retrieval] reranked to {len(reranked)} chunks")
    return reranked

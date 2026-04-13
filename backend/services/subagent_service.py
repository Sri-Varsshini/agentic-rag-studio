from openai import OpenAI
from langsmith import traceable
from supabase import Client
from config import settings
import json

client = OpenAI(api_key=settings.openai_api_key)

SUBAGENT_SYSTEM_PROMPT = """You are a document analysis specialist. You have been given the full content of one or more documents.
Analyze them thoroughly and answer the user's question with detail and precision.
Cite specific sections when relevant. Do not make up information not present in the documents."""


def _fetch_all_chunks(supabase: Client, document_ids: list[str]) -> str:
    """Fetch all chunks for given document IDs, ordered by position."""
    result = supabase.table("chunks") \
        .select("content, metadata, document_id") \
        .in_("document_id", document_ids) \
        .order("id") \
        .execute()

    chunks = result.data or []
    if not chunks:
        return "No document content found."

    parts = []
    for chunk in chunks:
        meta = chunk.get("metadata") or {}
        header = meta.get("title", "")
        content = chunk["content"]
        parts.append(f"[{header}]\n{content}" if header else content)

    return "\n\n---\n\n".join(parts)


@traceable(name="subagent_run")
def _trace_subagent(query: str, document_ids: list[str]) -> str:
    return query


def run_subagent(supabase: Client, query: str, document_ids: list[str]):
    _trace_subagent(query, document_ids)
    """
    Run an isolated sub-agent over the full content of the given documents.
    Yields SSE-style dicts: subagent_start, subagent_reasoning, subagent_done.
    Returns the final answer string as the last yielded value via subagent_done.
    """
    yield {"event": "subagent_start", "data": json.dumps({"document_ids": document_ids, "query": query})}

    doc_content = _fetch_all_chunks(supabase, document_ids)
    print(f"[subagent] loaded {len(doc_content)} chars for {len(document_ids)} doc(s)")

    messages = [
        {"role": "system", "content": SUBAGENT_SYSTEM_PROMPT},
        {"role": "user", "content": f"Documents:\n\n{doc_content}\n\n---\n\nQuestion: {query}"}
    ]

    yield {"event": "subagent_reasoning", "data": json.dumps({"status": "Analyzing document content..."})}

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0
    )

    answer = response.choices[0].message.content
    print(f"[subagent] answer length={len(answer)}")

    yield {"event": "subagent_done", "data": json.dumps({"answer": answer})}

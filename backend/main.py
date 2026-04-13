from fastapi import FastAPI, Depends, HTTPException, Header, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from supabase import create_client, Client
from config import settings
from models.schemas import ThreadCreate, ThreadResponse, MessageCreate
from services.openai_service import send_message_stream
from services.ingestion_service import ingest_document, check_and_ingest
from services.retrieval_service import retrieve_context
from services.sql_service import query_database
from services.search_service import web_search
from services.subagent_service import run_subagent
from typing import Optional
import json
import uuid

app = FastAPI(title="Agentic RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)
auth_client: Client = create_client(settings.supabase_url, settings.supabase_anon_key)


def get_user_id(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.replace("Bearer ", "")
    try:
        user = auth_client.auth.get_user(token)
        print(f"[auth] user_id={user.user.id}")
        return user.user.id
    except Exception as e:
        print(f"[auth] error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ── Threads ──────────────────────────────────────────────────────────────────

@app.post("/api/threads", response_model=ThreadResponse)
async def create_new_thread(thread_data: ThreadCreate, user_id: str = Depends(get_user_id)):
    result = supabase.table("threads").insert({
        "user_id": user_id,
        "title": thread_data.title
    }).execute()
    return result.data[0]


@app.get("/api/threads")
async def list_threads(user_id: str = Depends(get_user_id)):
    result = supabase.table("threads").select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
    return result.data


@app.post("/api/threads/{thread_id}/messages")
async def send_message(thread_id: str, message_data: MessageCreate, user_id: str = Depends(get_user_id)):
    thread_result = supabase.table("threads").select("id").eq("id", thread_id).eq("user_id", user_id).execute()
    if not thread_result.data:
        raise HTTPException(status_code=404, detail="Thread not found")

    history_result = supabase.table("messages").select("role,content").eq("thread_id", thread_id).order("created_at").execute()
    history = [{"role": m["role"], "content": m["content"]} for m in history_result.data]

    supabase.table("messages").insert({
        "thread_id": thread_id,
        "user_id": user_id,
        "role": "user",
        "content": message_data.content
    }).execute()

    def retrieve_fn(query: str) -> str:
        return retrieve_context(supabase, user_id, query)

    def query_db_fn(query: str) -> str:
        return query_database(supabase, query)

    def search_fn(query: str) -> str:
        return web_search(query)

    async def subagent_fn(query: str, document_ids: list):
        for event in run_subagent(supabase, query, document_ids):
            yield event

    docs_result = supabase.table("documents").select("id, filename").eq("user_id", user_id).eq("status", "completed").execute()
    documents = docs_result.data or []

    async def event_generator():
        full_response = ""
        is_subagent_response = False
        async for event in send_message_stream(history, message_data.content, retrieve_fn, query_db_fn, search_fn, subagent_fn, documents):
            if event["event"] == "subagent_start":
                is_subagent_response = True
            if event["event"] == "message":
                chunk = json.loads(event["data"])["content"]
                full_response += chunk
            yield event

        # Prefix subagent responses in history so LLM knows it was a full-doc analysis
        saved_content = f"[Full document analysis]\n{full_response}" if is_subagent_response else full_response

        supabase.table("messages").insert({
            "thread_id": thread_id,
            "user_id": user_id,
            "role": "assistant",
            "content": saved_content
        }).execute()

        supabase.table("threads").update({"updated_at": "now()"}).eq("id", thread_id).execute()
        yield {"event": "done", "data": json.dumps({"status": "complete"})}

    return EventSourceResponse(event_generator())


@app.get("/api/threads/{thread_id}/messages")
async def get_messages(thread_id: str, user_id: str = Depends(get_user_id)):
    result = supabase.table("messages").select("*").eq("thread_id", thread_id).eq("user_id", user_id).order("created_at").execute()
    return result.data


# ── Documents ─────────────────────────────────────────────────────────────────

@app.post("/api/documents")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_user_id)
):
    content = await file.read()

    # Upload to Supabase Storage
    storage_path = f"{user_id}/{uuid.uuid4()}/{file.filename}"
    supabase.storage.from_(settings.supabase_storage_bucket).upload(
        storage_path,
        content,
        {"content-type": file.content_type or "text/plain"}
    )

    # Create document record
    result = supabase.table("documents").insert({
        "user_id": user_id,
        "filename": file.filename,
        "storage_path": storage_path,
        "status": "processing"
    }).execute()

    document_id = result.data[0]["id"]

    background_tasks.add_task(check_and_ingest, supabase, user_id, file.filename, content, document_id)

    return result.data[0]


@app.get("/api/documents")
async def list_documents(user_id: str = Depends(get_user_id)):
    result = supabase.table("documents").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return result.data


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str, user_id: str = Depends(get_user_id)):
    doc = supabase.table("documents").select("storage_path").eq("id", document_id).eq("user_id", user_id).execute()
    if not doc.data:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from storage
    supabase.storage.from_(settings.supabase_storage_bucket).remove([doc.data[0]["storage_path"]])

    # Delete record (chunks cascade)
    supabase.table("documents").delete().eq("id", document_id).execute()
    return {"status": "deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

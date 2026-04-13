# Agentic RAG Studio

Build a full-featured agentic RAG application.

## What You'll Build

- Chat interface with threaded conversations, streaming, tool calls, and subagent reasoning
- Document ingestion with drag-and-drop upload and processing status
- Full RAG pipeline: chunking, embedding, hybrid search, reranking
- Agentic patterns: text-to-SQL, web search, subagents with isolated context

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | React, TypeScript, Tailwind, shadcn/ui, Vite |
| Backend | Python, FastAPI |
| Database | Supabase (Postgres + pgvector + Auth + Storage) |
| Doc Processing | Docling |
| AI Models | Local (LM Studio) or Cloud (OpenAI, OpenRouter) |
| Observability | LangSmith |

## The 8 Modules

1. App Shell — Auth, chat UI, managed RAG with OpenAI Responses API
2. BYO Retrieval + Memory — Ingestion, pgvector, generic completions API
3. Record Manager — Content hashing, deduplication
4. Metadata Extraction — LLM-extracted metadata, filtered retrieval
5. Multi-Format Support — PDF, DOCX, HTML, Markdown via Docling
6. Hybrid Search & Reranking — Keyword + vector search, RRF, reranking
7. Additional Tools — Text-to-SQL, web search fallback
8. Subagents — Isolated context, document analysis delegation

## Docs

- [SETUP.md](./SETUP.md) — Detailed setup guide
- [QUICKSTART.md](./QUICKSTART.md) — 5-minute quick start

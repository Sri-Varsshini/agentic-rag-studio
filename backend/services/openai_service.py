from openai import OpenAI
from langsmith import traceable
from config import settings
import os
import json

os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
os.environ["LANGCHAIN_TRACING_V2"] = "true" if settings.langsmith_api_key else "false"
os.environ["LANGCHAIN_ENDPOINT"] = settings.langsmith_endpoint

client = OpenAI(api_key=settings.openai_api_key)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "retrieve_context",
            "description": "Search the user's uploaded documents for relevant information. Use this for targeted questions about content the user has ingested.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "Query structured/tabular data in the database using natural language. Use this for questions about counts, statistics, or data stored in tables.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Natural language question about the data"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current events, recent information, or anything not found in the user's documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The web search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delegate_to_subagent",
            "description": "Delegate full-document analysis to a sub-agent when the question requires reading an entire document (e.g. 'summarize the whole document', 'analyze everything', 'compare all sections'). The sub-agent gets isolated context with the full document content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The analysis task for the sub-agent"},
                    "document_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of document IDs to analyze. Use retrieve_context first to identify relevant document IDs if needed."
                    },
                    "reason": {"type": "string", "description": "Why full-document analysis is needed"}
                },
                "required": ["query", "document_ids", "reason"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a helpful assistant with access to four tools:
- retrieve_context: search the user's uploaded documents (for targeted questions)
- query_database: query structured data in the database
- web_search: search the web for current or external information
- delegate_to_subagent: delegate full-document analysis when the user asks to summarize, analyze, or compare entire documents

Use delegate_to_subagent when the question requires reading a whole document (e.g. "summarize the entire document", "analyze the whole report", "compare all sections"). For targeted questions, use retrieve_context instead.

In conversation history, messages prefixed with [Full document analysis] were produced by a sub-agent that read the entire document. For follow-up questions about the same document, use retrieve_context for targeted lookups or delegate_to_subagent again if full context is needed.

IMPORTANT: Always give a complete, specific answer based on the retrieved content. Never end responses with generic phrases like 'If you have more questions, feel free to ask' or 'Let me know if you need more details'. Just answer the question directly and thoroughly."""


@traceable(name="chat_completion")
def _trace_chat(messages_payload: list, new_message: str) -> str:
    """Thin traceable wrapper so LangSmith captures the chat turn."""
    return new_message  # input captured by LangSmith; actual work happens in the generator


async def send_message_stream(messages: list, new_message: str, retrieve_fn, query_db_fn, search_fn, subagent_fn, documents: list = []):
    _trace_chat(messages, new_message)  # register trace with LangSmith
    doc_context = ""
    doc_context = ""
    if documents:
        doc_lines = "\n".join(f"- {d['filename']} (id: {d['id']})" for d in documents)
        doc_context = f"\n\nUser's uploaded documents:\n{doc_lines}"

    messages_payload = [{"role": "system", "content": SYSTEM_PROMPT + doc_context}] + messages + [{"role": "user", "content": new_message}]

    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_payload,
            tools=TOOLS,
            tool_choice="auto"
        )

        choice = response.choices[0]
        messages_payload.append(choice.message)

        if choice.finish_reason != "tool_calls":
            break

        for tool_call in choice.message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"[tool_call] {name} args={args}")

            if name == "retrieve_context":
                result = retrieve_fn(args["query"])
                content = result if result else "No relevant documents found."

            elif name == "query_database":
                content = query_db_fn(args["query"])

            elif name == "web_search":
                content = search_fn(args["query"])

            elif name == "delegate_to_subagent":
                subagent_answer = ""
                async for event in subagent_fn(args["query"], args["document_ids"]):
                    yield event
                    if event["event"] == "subagent_done":
                        subagent_answer = json.loads(event["data"]).get("answer", "")
                content = subagent_answer if subagent_answer else "Sub-agent returned no result."
                messages_payload.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": content
                })
                # Stream subagent answer directly, skip final LLM call
                for char in content:
                    yield {"event": "message", "data": json.dumps({"content": char})}
                return

            else:
                content = f"Unknown tool: {name}"

            print(f"[tool_call] {name} result length={len(content)}")
            messages_payload.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": content
            })

    # Stream the final response
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_payload,
        stream=True
    )

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield {"event": "message", "data": json.dumps({"content": delta.content})}

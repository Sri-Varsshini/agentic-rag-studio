from openai import OpenAI
from pydantic import BaseModel
from config import settings

client = OpenAI(api_key=settings.openai_api_key)


class ChunkMetadata(BaseModel):
    title: str
    summary: str
    keywords: list[str]
    document_type: str  # e.g. "report", "article", "manual", "email", "other"
    date: str | None    # ISO date string if found, else None


def extract_metadata(chunk_text: str, filename: str) -> dict:
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract structured metadata from the given document chunk. "
                    "Use the filename as a hint for context. "
                    "For 'date', extract any date mentioned in the text (ISO format), or null if none. "
                    "For 'document_type', infer from content and filename."
                )
            },
            {
                "role": "user",
                "content": f"Filename: {filename}\n\nChunk:\n{chunk_text}"
            }
        ],
        response_format=ChunkMetadata,
    )
    return response.choices[0].message.parsed.model_dump()

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ThreadCreate(BaseModel):
    title: Optional[str] = "New Chat"

class ThreadResponse(BaseModel):
    id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

class MessageCreate(BaseModel):
    content: str

class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    chunk_count: Optional[int]
    created_at: datetime

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="User input")
    session_id: Optional[str] = Field(None, description="Client session identifier for context")


class TableColumn(BaseModel):
    id: str
    label: str


class TableData(BaseModel):
    columns: List[TableColumn]
    rows: List[Dict[str, Any]]
    title: Optional[str] = None


class ChatMessage(BaseModel):
    role: str
    text: str
    table: Optional[TableData] = None
    warnings: Optional[List[str]] = None


class ChatResponse(BaseModel):
    messages: List[ChatMessage]
    metadata: Dict[str, Any] = Field(default_factory=dict)


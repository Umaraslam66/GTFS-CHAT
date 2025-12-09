from typing import List, Optional

from . import schemas


def build_chat_response(
    text: str,
    tables: Optional[List[schemas.TableData]] = None,
    warnings: Optional[List[str]] = None,
    metadata: Optional[dict] = None,
) -> schemas.ChatResponse:
    messages = [
        schemas.ChatMessage(
            role="assistant",
            text=text,
            table=tables[0] if tables else None,
            warnings=warnings,
        )
    ]
    return schemas.ChatResponse(messages=messages, metadata=metadata or {})


from fastapi import APIRouter
from typing import List, Dict

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models", response_model=List[Dict[str, str]])
async def list_models():
    """List available models for the chat interface."""
    return [
        {
            "value": "mistralai/devstral-2512:free",
            "label": "Mistral Devstral 2.5 (Free)",
            "description": "Fast, good JSON support",
        },
        {
            "value": "amazon/nova-2-lite-v1:free",
            "label": "Amazon Nova 2 Lite (Free)",
            "description": "May have JSON issues",
        },
        {
            "value": "openrouter/meta-llama/llama-3.1-8b-instruct:free",
            "label": "Llama 3.1 8B (Free)",
            "description": "Good for tool calling",
        },
        {
            "value": "openrouter/google/gemini-2.0-flash-exp",
            "label": "Google Gemini 2.0 Flash",
            "description": "Excellent JSON support",
        },
        {
            "value": "openrouter/anthropic/claude-3-haiku",
            "label": "Claude 3 Haiku",
            "description": "Reliable, paid",
        },
    ]


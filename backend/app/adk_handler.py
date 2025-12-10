"""
ADK handler for running the agent and converting responses to API schema.
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from .adk_agent_config import gtfs_agent
from . import schemas

logger = logging.getLogger(__name__)


async def run_adk_agent(
    message: str,
    session: Session,
    session_id: Optional[str] = None,
) -> schemas.ChatResponse:
    """
    Run the ADK agent with a user message and convert the response.

    Args:
        message: User's message/query
        session: Database session for tools to use
        session_id: Optional session ID for conversation continuity

    Returns:
        ChatResponse with agent's response and any table data
    """
    try:
        # Create tool context with database session
        from google.adk.tools.tool_context import ToolContext

        tool_context = ToolContext()
        tool_context.state["session"] = session

        # Run the agent
        # ADK agent.run() returns a response object
        response = await gtfs_agent.run(
            message,
            tool_context=tool_context,
        )

        # Extract response text - ADK responses can be various types
        response_text = ""
        table_data = None
        warnings = []

        # Handle different response types
        if isinstance(response, str):
            response_text = response
        elif hasattr(response, "text"):
            response_text = response.text
        elif hasattr(response, "content"):
            # Response might have content attribute
            content = response.content
            if isinstance(content, str):
                response_text = content
            elif isinstance(content, list):
                # Content might be a list of parts
                text_parts = []
                for part in content:
                    if isinstance(part, str):
                        text_parts.append(part)
                    elif hasattr(part, "text"):
                        text_parts.append(part.text)
                    elif isinstance(part, dict) and "text" in part:
                        text_parts.append(part["text"])
                response_text = " ".join(text_parts)
        else:
            response_text = str(response)

        # Try to extract tool results from tool context state
        # Tools store results in the context for table formatting
        if "tool_results" in tool_context.state:
            tool_results = tool_context.state["tool_results"]
            for result in tool_results:
                if isinstance(result, dict) and "departures" in result:
                    departures = result["departures"]
                    if departures and len(departures) > 0:
                        # Format as table - departures are already dicts
                        first_dep = departures[0]
                        columns = [
                            schemas.TableColumn(id=k, label=k.replace("_", " ").title())
                            for k in first_dep.keys()
                        ]
                        table_data = schemas.TableData(
                            columns=columns,
                            rows=departures,
                            title=f"Departures from {result.get('origin', 'Origin')} to {result.get('destination', 'Destination')}",
                        )
                        break

        return schemas.ChatResponse(
            messages=[
                schemas.ChatMessage(
                    role="assistant",
                    text=response_text or "I couldn't process that request.",
                    table=table_data,
                    warnings=warnings if warnings else None,
                )
            ],
            metadata={"session_id": session_id} if session_id else {},
        )

    except Exception as e:
        logger.error(f"Error running ADK agent: {e}", exc_info=True)
        return schemas.ChatResponse(
            messages=[
                schemas.ChatMessage(
                    role="assistant",
                    text=f"I encountered an error processing your request: {str(e)}",
                    warnings=["Agent execution error"],
                )
            ],
            metadata={},
        )


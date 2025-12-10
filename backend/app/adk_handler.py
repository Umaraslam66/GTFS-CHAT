"""
ADK handler for running the agent and converting responses to API schema.
"""

import logging
from typing import Optional

from google.adk.runners import Runner, InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from sqlalchemy.orm import Session

from .adk_agent_config import create_agent_with_model, gtfs_agent
from . import schemas

logger = logging.getLogger(__name__)

# Create session service (reusable)
_session_service = InMemorySessionService()

# Cache runners by model to avoid recreating them
_runner_cache: dict[str, Runner] = {}


def get_runner_for_model(model: Optional[str] = None) -> Runner:
    """Get or create a runner for the specified model."""
    cache_key = model or "default"
    
    if cache_key not in _runner_cache:
        agent = create_agent_with_model(model) if model else gtfs_agent
        _runner_cache[cache_key] = Runner(
            app_name="gtfs_chat",
            agent=agent,
            session_service=_session_service,
        )
    
    return _runner_cache[cache_key]


async def run_adk_agent(
    message: str,
    session: Session,
    session_id: Optional[str] = None,
    model: Optional[str] = None,
) -> schemas.ChatResponse:
    """
    Run the ADK agent with a user message and convert the response.

    Args:
        message: User's message/query
        session: Database session for tools to use
        session_id: Optional session ID for conversation continuity
        model: Optional model override (e.g., 'mistralai/devstral-2512:free')

    Returns:
        ChatResponse with agent's response and any table data
    """
    try:
        # Get runner for the specified model
        runner = get_runner_for_model(model)
        
        # Use provided session_id or create a default one
        user_id = "user"
        actual_session_id = session_id or "default_session"
        
        # Create or get session
        adk_session = await _session_service.create_session(
            app_name="gtfs_chat",
            user_id=user_id,
            session_id=actual_session_id,
        )
        
        # Store database session in session state for tools to access
        adk_session.state["db_session"] = session
        
        # Create user message content
        user_content = types.Content(
            role="user",
            parts=[types.Part(text=message)]
        )
        
        # Run the agent and collect events
        events = []
        tool_results = []
        
        async for event in runner.run_async(
            user_id=user_id,
            session_id=adk_session.id,
            new_message=user_content,
        ):
            events.append(event)
            
            # Extract tool results from events if available
            if hasattr(event, "tool_code_execution_finished") and hasattr(event, "result"):
                tool_results.append(event.result)
        
        # Extract response from events
        response_text = ""
        table_data = None
        warnings = []

        # Process events to extract text and table data
        for event in events:
            # Extract text from content events
            if hasattr(event, "content") and event.content:
                if hasattr(event.content, "parts"):
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            response_text += part.text + " "
                elif isinstance(event.content, str):
                    response_text += event.content + " "
            
            # Extract tool results
            if hasattr(event, "tool_code_execution_finished"):
                if hasattr(event, "result"):
                    result = event.result
                    if isinstance(result, dict):
                        tool_results.append(result)

        # Process tool results to create table data
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
            elif isinstance(result, dict) and "stops" in result:
                stops = result["stops"]
                if stops and len(stops) > 0:
                    first_stop = stops[0]
                    columns = [
                        schemas.TableColumn(id=k, label=k.replace("_", " ").title())
                        for k in first_stop.keys()
                    ]
                    table_data = schemas.TableData(
                        columns=columns,
                        rows=stops,
                        title="Search Results for Stops",
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
        error_msg = str(e)
        logger.error(f"Error running ADK agent: {error_msg}", exc_info=True)
        
        # Provide user-friendly error messages for common issues
        if "JSONDecodeError" in error_msg or "Extra data" in error_msg:
            user_message = (
                "I'm having trouble processing your request due to a technical issue with the AI model. "
                "Please try rephrasing your question or try again in a moment."
            )
        elif "database" in error_msg.lower() or "connection" in error_msg.lower():
            user_message = (
                "I'm having trouble accessing the railway database. "
                "Please try again in a moment."
            )
        else:
            user_message = (
                "I encountered an error processing your request. "
                "Please try rephrasing your question or try again later."
            )
        
        return schemas.ChatResponse(
            messages=[
                schemas.ChatMessage(
                    role="assistant",
                    text=user_message,
                    warnings=["Agent execution error"],
                )
            ],
            metadata={},
        )


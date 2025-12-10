"""
GTFS Sweden railway assistant agent for ADK web interface.
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
import os

from app.config import get_settings
from app.adk_tools import get_departures, search_rail_stops, get_next_departures, get_route_stops

settings = get_settings()

# Configure LiteLLM for OpenRouter
os.environ["OPENROUTER_API_KEY"] = settings.openrouter_api_key or ""
os.environ["LITELLM_API_BASE"] = "https://openrouter.ai/api/v1"

# Create LiteLLM model instance
model_name = settings.openrouter_model
if not model_name.startswith("openrouter/"):
    if "/" in model_name:
        model_name = f"openrouter/{model_name}"
    else:
        model_name = f"openrouter/{model_name}"

litellm_model = LiteLlm(model=model_name)

# Create ADK agent - must be named root_agent for ADK web
root_agent = Agent(
    model=litellm_model,
    name="gtfs_sweden_assistant",
    description=(
        "A helpful assistant for Swedish railway schedules and routes. "
        "Can search for railway stations and find train departures between locations."
    ),
    instruction="""
You are a helpful assistant for Swedish railway travel information.
You help users find train schedules, stations, and routes using the GTFS Sweden dataset.

Available tools:
- search_rail_stops: Find railway stations by name
- get_departures: Find trains between two specific stations
- get_next_departures: Get upcoming departures from a station (no destination needed)
- get_route_stops: Get all stops along a specific train trip

When users ask about trains or routes:
1. Use search_rail_stops to find station names if needed
2. Use get_departures for point-to-point queries
3. Use get_next_departures when user asks "what trains leave from X" without destination
4. Use get_route_stops to show all stops on a specific train
5. Provide clear, concise answers with relevant details

Always be helpful and provide accurate information based on the tool results.
If you cannot find information, suggest alternative queries or time windows.
    """,
    tools=[search_rail_stops, get_departures, get_next_departures, get_route_stops],
)


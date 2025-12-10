"""
ADK tools for GTFS Sweden railway queries.
These tools are used by the ADK agent to interact with the database.
"""

from datetime import date, time
from typing import List, Optional

from google.adk.tools.tool_context import ToolContext
from sqlalchemy.orm import Session

from sqlalchemy import text

from .query_planner import active_services, departures_between, search_stops
from .db import SessionLocal


def search_rail_stops(
    name: str,
    limit: int = 10,
    tool_context: ToolContext = None,
) -> List[dict]:
    """Search for railway stops by name.

    Use this tool to find railway stations/stops when the user mentions a location.
    The search is case-insensitive and matches partial names.

    Args:
        name: The stop name or partial name to search for (e.g., "Stockholm", "Göteborg").
        limit: Maximum number of results to return (default: 10).
        tool_context: ADK tool context providing database session access.

    Returns:
        A list of dictionaries with 'stop_id' and 'stop_name' keys.
        Example: [{"stop_id": "740000002", "stop_name": "Stockholm Central"}]
    """
    # Get session from context or create a new one
    if tool_context and "session" in tool_context.state:
        session: Session = tool_context.state["session"]
        use_existing = True
    else:
        # Create a new session for ADK web usage
        session = SessionLocal()
        use_existing = False
    
    try:
        result = search_stops(session, name, limit)
        
        # Store result in tool context
        if tool_context:
            if "tool_results" not in tool_context.state:
                tool_context.state["tool_results"] = []
            tool_context.state["tool_results"].append({"stops": result})
        
        return result
    finally:
        # Only close if we created the session
        if not use_existing:
            session.close()


def get_departures(
    origin_name: str,
    destination_name: str,
    travel_date: Optional[str] = None,
    after_time: Optional[str] = None,
    limit_rows: int = 50,
    tool_context: ToolContext = None,
) -> dict:
    """Find railway departures between two stations.

    Use this tool when the user asks about train schedules, departures, or routes
    between two locations. The tool searches for direct connections on the specified
    date and time.

    Args:
        origin_name: The origin station name (e.g., "Stockholm Central").
        destination_name: The destination station name (e.g., "Göteborg Central").
        travel_date: Optional date in YYYY-MM-DD format (default: today).
        after_time: Optional time filter in HH:MM format (e.g., "14:00").
        limit_rows: Maximum number of departures to return (default: 50).
        tool_context: ADK tool context providing database session access.

    Returns:
        A dictionary with 'departures' list containing departure information.
        Each departure has: departure, arrival, origin_name, destination_name,
        agency_name, route_short_name, trip_id, route_id.
    """
    # Get session from context or create a new one
    if tool_context and "session" in tool_context.state:
        session: Session = tool_context.state["session"]
        use_existing = True
    else:
        # Create a new session for ADK web usage
        session = SessionLocal()
        use_existing = False

    try:
        # Parse date if provided
        parsed_date = None
        if travel_date:
            try:
                parsed_date = date.fromisoformat(travel_date)
            except ValueError:
                return {"departures": [], "error": f"Invalid date format: {travel_date}"}

        # Parse time if provided
        parsed_time = None
        if after_time:
            try:
                hour, minute = map(int, after_time.split(":"))
                parsed_time = time(hour, minute)
            except (ValueError, AttributeError):
                return {"departures": [], "error": f"Invalid time format: {after_time}"}

        # Call the query planner function
        tables = departures_between(
            session=session,
            origin_name=origin_name,
            destination_name=destination_name,
            travel_date=parsed_date,
            after_time=parsed_time,
            limit_rows=limit_rows,
        )

        if not tables:
            return {"departures": [], "message": "No departures found for the specified route"}

        # Table rows are already dictionaries
        table = tables[0]
        result = {
            "departures": table.rows,
            "count": len(table.rows),
            "origin": origin_name,
            "destination": destination_name,
        }
        
        # Store result in tool context for handler to access
        if tool_context:
            if "tool_results" not in tool_context.state:
                tool_context.state["tool_results"] = []
            tool_context.state["tool_results"].append(result)
        
        return result
    finally:
        # Only close if we created the session
        if not use_existing:
            session.close()


def get_next_departures(
    station_name: str,
    travel_date: Optional[str] = None,
    after_time: Optional[str] = None,
    limit_rows: int = 20,
    tool_context: ToolContext = None,
) -> dict:
    """Get next departures from a railway station.

    Use this tool when the user asks about departures from a specific station
    without specifying a destination, or wants to see all upcoming trains.

    Args:
        station_name: The station name (e.g., "Stockholm Central").
        travel_date: Optional date in YYYY-MM-DD format (default: today).
        after_time: Optional time filter in HH:MM format (e.g., "14:00").
        limit_rows: Maximum number of departures to return (default: 20).
        tool_context: ADK tool context providing database session access.

    Returns:
        A dictionary with 'departures' list containing departure information.
    """
    # Get session from context or create a new one
    if tool_context and "session" in tool_context.state:
        session: Session = tool_context.state["session"]
        use_existing = True
    else:
        session = SessionLocal()
        use_existing = False

    try:
        # Find station
        stations = search_stops(session, station_name, limit=3)
        if not stations:
            return {"departures": [], "error": f"Station '{station_name}' not found"}

        station_ids = [s["stop_id"] for s in stations]

        # Parse date if provided
        parsed_date = None
        if travel_date:
            try:
                parsed_date = date.fromisoformat(travel_date)
            except ValueError:
                return {"departures": [], "error": f"Invalid date format: {travel_date}"}

        # Parse time if provided
        parsed_time = None
        if after_time:
            try:
                hour, minute = map(int, after_time.split(":"))
                parsed_time = time(hour, minute)
            except (ValueError, AttributeError):
                return {"departures": [], "error": f"Invalid time format: {after_time}"}

        # Get active services for date
        services = active_services(session, parsed_date) if parsed_date else None
        if parsed_date and not services:
            return {"departures": [], "message": "No services available on the specified date"}

        # Build query
        params = {
            "station_ids": tuple(station_ids),
            "limit_rows": limit_rows,
        }
        time_clause = ""
        if parsed_time:
            params["after_time"] = parsed_time.strftime("%H:%M:%S")
            time_clause = "AND st.departure_time >= :after_time"

        service_clause = ""
        if services is not None:
            params["services"] = tuple(services)
            service_clause = "AND t.service_id IN :services"

        sql = text(
            f"""
            SELECT
                st.departure_time AS departure,
                s.stop_name AS station_name,
                r.agency_name,
                r.route_short_name,
                t.trip_id,
                t.route_id,
                t.trip_headsign
            FROM stop_times_rail st
            JOIN trips_rail t ON t.trip_id = st.trip_id
            JOIN routes_rail_with_agency r ON r.route_id = t.route_id
            JOIN stops_rail s ON s.stop_id = st.stop_id
            WHERE st.stop_id IN :station_ids
              {time_clause}
              {service_clause}
            ORDER BY st.departure_time
            LIMIT :limit_rows
            """
        )

        rows = session.execute(sql, params).mappings().all()
        departures = [dict(row) for row in rows]

        result = {
            "departures": departures,
            "count": len(departures),
            "station": station_name,
        }

        # Store result in tool context
        if tool_context:
            if "tool_results" not in tool_context.state:
                tool_context.state["tool_results"] = []
            tool_context.state["tool_results"].append(result)

        return result
    finally:
        if not use_existing:
            session.close()


def get_route_stops(
    trip_id: str,
    tool_context: ToolContext = None,
) -> dict:
    """Get all stops along a specific train trip/route.

    Use this tool when the user asks about stops on a specific train,
    or wants to see the full route of a train.

    Args:
        trip_id: The trip ID (e.g., from departure results).
        tool_context: ADK tool context providing database session access.

    Returns:
        A dictionary with 'stops' list containing all stops in order.
    """
    # Get session from context or create a new one
    if tool_context and "session" in tool_context.state:
        session: Session = tool_context.state["session"]
        use_existing = True
    else:
        session = SessionLocal()
        use_existing = False

    try:
        sql = text(
            """
            SELECT
                st.stop_sequence,
                s.stop_name,
                st.arrival_time,
                st.departure_time,
                st.stop_id
            FROM stop_times_rail st
            JOIN stops_rail s ON s.stop_id = st.stop_id
            WHERE st.trip_id = :trip_id
            ORDER BY st.stop_sequence
            """
        )

        rows = session.execute(sql, {"trip_id": trip_id}).mappings().all()
        if not rows:
            return {"stops": [], "error": f"Trip '{trip_id}' not found"}

        stops = [dict(row) for row in rows]

        result = {
            "stops": stops,
            "count": len(stops),
            "trip_id": trip_id,
        }

        # Store result in tool context
        if tool_context:
            if "tool_results" not in tool_context.state:
                tool_context.state["tool_results"] = []
            tool_context.state["tool_results"].append(result)

        return result
    finally:
        if not use_existing:
            session.close()

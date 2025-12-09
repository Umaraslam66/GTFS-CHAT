from datetime import date, time
from typing import List, Optional, Sequence

from sqlalchemy import text
from sqlalchemy.orm import Session

from . import schemas
from .models import Stop


def search_stops(session: Session, name: str, limit: int = 10) -> List[Stop]:
    query = (
        session.query(Stop)
        .filter(Stop.stop_name.ilike(f"%{name}%"))
        .order_by(Stop.stop_name)
        .limit(limit)
    )
    return list(query.all())


def active_services(session: Session, target_date: date) -> List[str]:
    """Return active service_ids for a given date using calendar + calendar_dates."""
    dow = target_date.weekday()  # Monday=0
    day_cols = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_col = day_cols[dow]

    sql = text(
        f"""
        WITH base AS (
            SELECT service_id FROM calendar
            WHERE start_date <= :target_date
              AND end_date >= :target_date
              AND {day_col} = true
        ),
        added AS (
            SELECT service_id FROM calendar_dates
            WHERE date = :target_date AND exception_type = 1
        ),
        removed AS (
            SELECT service_id FROM calendar_dates
            WHERE date = :target_date AND exception_type = 2
        )
        SELECT service_id FROM base
        UNION
        SELECT service_id FROM added
        EXCEPT
        SELECT service_id FROM removed
        """
    )
    rows = session.execute(sql, {"target_date": target_date}).scalars().all()
    return list(rows)


def departures_between(
    session: Session,
    origin_name: str,
    destination_name: str,
    travel_date: Optional[date],
    after_time: Optional[time],
    limit_rows: int = 50,
) -> Sequence[schemas.TableData]:
    """Find departures between two stop names, optionally filtered by date/time."""
    origin_candidates = search_stops(session, origin_name, limit=3)
    dest_candidates = search_stops(session, destination_name, limit=3)
    if not origin_candidates or not dest_candidates:
        return []

    origin_ids = [s.stop_id for s in origin_candidates]
    dest_ids = [s.stop_id for s in dest_candidates]

    services = active_services(session, travel_date) if travel_date else None
    if travel_date and not services:
        return []

    params = {
        "origin_ids": tuple(origin_ids),
        "dest_ids": tuple(dest_ids),
        "limit_rows": limit_rows,
    }
    time_clause = ""
    if after_time:
        params["after_time"] = after_time.strftime("%H:%M:%S")
        time_clause = "AND st_origin.departure_time >= :after_time"

    service_clause = ""
    if services is not None:
        params["services"] = tuple(services)
        service_clause = "AND t.service_id IN :services"

    sql = text(
        f"""
        SELECT
            st_origin.departure_time AS departure,
            st_dest.arrival_time AS arrival,
            s_origin.stop_name AS origin_name,
            s_dest.stop_name AS destination_name,
            t.trip_id,
            t.route_id
        FROM stop_times st_origin
        JOIN stop_times st_dest
            ON st_origin.trip_id = st_dest.trip_id
           AND st_origin.stop_sequence < st_dest.stop_sequence
        JOIN trips t ON t.trip_id = st_origin.trip_id
        JOIN stops s_origin ON s_origin.stop_id = st_origin.stop_id
        JOIN stops s_dest ON s_dest.stop_id = st_dest.stop_id
        WHERE st_origin.stop_id IN :origin_ids
          AND st_dest.stop_id IN :dest_ids
          {time_clause}
          {service_clause}
        ORDER BY st_origin.departure_time
        LIMIT :limit_rows
        """
    )

    rows = session.execute(sql, params).mappings().all()
    if not rows:
        return []

    columns = [
        schemas.TableColumn(id="departure", label="Departure"),
        schemas.TableColumn(id="arrival", label="Arrival"),
        schemas.TableColumn(id="origin_name", label="Origin"),
        schemas.TableColumn(id="destination_name", label="Destination"),
        schemas.TableColumn(id="route_id", label="Route"),
        schemas.TableColumn(id="trip_id", label="Trip"),
    ]

    data_rows = [dict(row) for row in rows]
    table = schemas.TableData(columns=columns, rows=data_rows, title="Departures")
    return [table]


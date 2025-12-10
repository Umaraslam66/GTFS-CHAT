import logging
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests
from sqlalchemy import text

from ..config import get_settings
from ..db import engine
from ..models import Base

settings = get_settings()
logger = logging.getLogger(__name__)

# Rail-focused route type whitelist (GTFS + common extensions for rail/metro/light rail/monorail)
RAIL_ROUTE_TYPES = {
    100,
    101,
    102,
    103,
    104,
    105,
    106,
    107,
    108,
    109,
    200,
    201,
    202,
    204,
    205,
    900,
}


GTFS_FILES: Dict[str, List[str]] = {
    "agency": [],
    "stops": [],
    "routes": [],
    "trips": [],
    "stop_times": [],
    "calendar": [],
    "calendar_dates": [],
    "shapes": [],
    "stop_areas": [],
    "areas": [],
    "transfers": [],
}


def download_gtfs_zip(dest_path: Path) -> Path:
    url = f"https://opendata.samtrafiken.se/gtfs-sweden/sweden.zip?key={settings.trafiklab_api_key}"
    logger.info("Downloading GTFS Sweden 3 feed...")
    response = requests.get(url, timeout=120, headers={"Accept-Encoding": "gzip"})
    response.raise_for_status()
    dest_path.write_bytes(response.content)
    logger.info("Downloaded GTFS archive to %s", dest_path)
    return dest_path


def unzip_feed(zip_path: Path, dest_dir: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(dest_dir)
    logger.info("Extracted GTFS feed to %s", dest_dir)


def load_csv_to_table(csv_path: Path, table_name: str, chunksize: int = 20000) -> None:
    if not csv_path.exists():
        logger.warning("File %s not found; skipping", csv_path.name)
        return

    logger.info("Loading %s into %s", csv_path.name, table_name)
    # Idempotent: drop-and-append to avoid reflection issues in duckdb pandas writer
    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name};"))
    if_exists_mode = "append"

    # Use smaller chunks for very large files to avoid parameter explosion in DuckDB
    heavy_tables = {"stop_times", "shapes"}
    table_chunksize = 5000 if table_name in heavy_tables else chunksize

    for chunk in pd.read_csv(csv_path, chunksize=table_chunksize, dtype=str):
        chunk.columns = [col.strip() for col in chunk.columns]

        if table_name == "calendar":
            day_cols = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            for col in day_cols:
                if col in chunk.columns:
                    chunk[col] = chunk[col].astype(bool)
            if "start_date" in chunk.columns:
                chunk["start_date"] = pd.to_datetime(chunk["start_date"], format="%Y%m%d")
            if "end_date" in chunk.columns:
                chunk["end_date"] = pd.to_datetime(chunk["end_date"], format="%Y%m%d")

        if table_name == "calendar_dates":
            if "date" in chunk.columns:
                chunk["date"] = pd.to_datetime(chunk["date"], format="%Y%m%d")

        if table_name == "stops":
            expected = [
                "stop_id",
                "stop_name",
                "stop_lat",
                "stop_lon",
                "location_type",
                "parent_station",
                "platform_code",
            ]
            for col in expected:
                if col not in chunk.columns:
                    chunk[col] = None
            chunk = chunk[expected]
            for col in ("stop_lat", "stop_lon"):
                if col in chunk.columns:
                    chunk[col] = pd.to_numeric(chunk[col], errors="coerce")
            if "location_type" in chunk.columns:
                chunk["location_type"] = pd.to_numeric(chunk["location_type"], errors="coerce").astype("Int64")

        # Deduplicate for tables that may carry duplicate natural keys
        if table_name == "stop_areas":
            chunk = chunk.drop_duplicates(subset=["area_id", "stop_id"])
        chunk.to_sql(table_name, engine, if_exists=if_exists_mode, index=False)
        if_exists_mode = "append"
    logger.info("Finished loading %s", table_name)


def materialize_rail_subset() -> None:
    """
    Create rail-only tables and indexes to slim the dataset for rail-focused queries.
    """
    whitelist = ",".join(str(x) for x in sorted(RAIL_ROUTE_TYPES))
    logger.info("Creating rail-only tables with route_type in (%s)", whitelist)

    stmts = [
        "DROP TABLE IF EXISTS routes_rail",
        f"""
        CREATE TABLE routes_rail AS
        SELECT * FROM routes WHERE route_type IN ({whitelist})
        """,
        "DROP TABLE IF EXISTS trips_rail",
        """
        CREATE TABLE trips_rail AS
        SELECT t.*
        FROM trips t
        JOIN routes_rail r ON r.route_id = t.route_id
        """,
        "DROP TABLE IF EXISTS stop_times_rail",
        """
        CREATE TABLE stop_times_rail AS
        SELECT st.*
        FROM stop_times st
        JOIN trips_rail t ON t.trip_id = st.trip_id
        """,
        "DROP TABLE IF EXISTS shapes_rail",
        """
        CREATE TABLE shapes_rail AS
        SELECT s.*
        FROM shapes s
        WHERE EXISTS (
            SELECT 1 FROM trips_rail t WHERE t.shape_id = s.shape_id
        )
        """,
        "DROP TABLE IF EXISTS stops_rail",
        """
        CREATE TABLE stops_rail AS
        SELECT DISTINCT s.*
        FROM stops s
        JOIN stop_times_rail st ON st.stop_id = s.stop_id
        """,
        "DROP TABLE IF EXISTS transfers_rail",
        """
        CREATE TABLE transfers_rail AS
        SELECT tr.*
        FROM transfers tr
        WHERE tr.from_stop_id IN (SELECT DISTINCT stop_id FROM stop_times_rail)
          AND tr.to_stop_id   IN (SELECT DISTINCT stop_id FROM stop_times_rail)
        """,
        # Readability helper with agency names
        "DROP VIEW IF EXISTS routes_rail_with_agency",
        """
        CREATE VIEW routes_rail_with_agency AS
        SELECT r.*, a.agency_name, a.agency_url, a.agency_timezone
        FROM routes_rail r
        LEFT JOIN agency a ON a.agency_id = r.agency_id
        """,
    ]

    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_routes_rail_type ON routes_rail(route_type)",
        "CREATE INDEX IF NOT EXISTS idx_routes_rail_agency ON routes_rail(agency_id)",
        "CREATE INDEX IF NOT EXISTS idx_trips_rail_route ON trips_rail(route_id)",
        "CREATE INDEX IF NOT EXISTS idx_trips_rail_service ON trips_rail(service_id)",
        "CREATE INDEX IF NOT EXISTS idx_trips_rail_shape ON trips_rail(shape_id)",
        "CREATE INDEX IF NOT EXISTS idx_stop_times_rail_trip ON stop_times_rail(trip_id)",
        "CREATE INDEX IF NOT EXISTS idx_stop_times_rail_stop_seq ON stop_times_rail(stop_id, stop_sequence)",
        "CREATE INDEX IF NOT EXISTS idx_stop_times_rail_departure ON stop_times_rail(departure_time)",
        "CREATE INDEX IF NOT EXISTS idx_shapes_rail_seq ON shapes_rail(shape_id, shape_pt_sequence)",
    ]

    with engine.begin() as conn:
        for stmt in stmts:
            conn.execute(text(stmt))
        for idx in indexes:
            conn.execute(text(idx))

    logger.info("Rail-only tables created.")


def ingest(include_rail: bool = True):
    Base.metadata.create_all(bind=engine)

    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        zip_path = tmpdir / "sweden.zip"
        download_gtfs_zip(zip_path)
        unzip_feed(zip_path, tmpdir)

        load_csv_to_table(tmpdir / "agency.txt", "agency")
        load_csv_to_table(tmpdir / "stops.txt", "stops")
        load_csv_to_table(tmpdir / "routes.txt", "routes")
        load_csv_to_table(tmpdir / "trips.txt", "trips")
        load_csv_to_table(tmpdir / "stop_times.txt", "stop_times")
        load_csv_to_table(tmpdir / "calendar.txt", "calendar")
        load_csv_to_table(tmpdir / "calendar_dates.txt", "calendar_dates")
        load_csv_to_table(tmpdir / "shapes.txt", "shapes")
        load_csv_to_table(tmpdir / "stop_areas.txt", "stop_areas")
        load_csv_to_table(tmpdir / "areas.txt", "areas")
        load_csv_to_table(tmpdir / "transfers.txt", "transfers")

    logger.info("GTFS Sweden 3 ingestion completed.")

    if include_rail:
        materialize_rail_subset()


if __name__ == "__main__":
    logging.basicConfig(level=settings.log_level)
    ingest()


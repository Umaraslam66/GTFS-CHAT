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
}


def download_gtfs_zip(dest_path: Path) -> Path:
    url = f"https://opendata.samtrafiken.se/gtfs-sweden/sweden.zip?key={settings.trafiklab_api_key}"
    logger.info("Downloading GTFS Sweden 3 feed...")
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    dest_path.write_bytes(response.content)
    logger.info("Downloaded GTFS archive to %s", dest_path)
    return dest_path


def unzip_feed(zip_path: Path, dest_dir: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(dest_dir)
    logger.info("Extracted GTFS feed to %s", dest_dir)


def load_csv_to_table(csv_path: Path, table_name: str, chunksize: int = 50000) -> None:
    if not csv_path.exists():
        logger.warning("File %s not found; skipping", csv_path.name)
        return

    logger.info("Loading %s into %s", csv_path.name, table_name)
    with engine.begin() as conn:
        # Clear existing data for deterministic reloads
        conn.execute(text(f"TRUNCATE TABLE {table_name};"))

    for chunk in pd.read_csv(csv_path, chunksize=chunksize):
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

        chunk.to_sql(table_name, engine, if_exists="append", index=False, method="multi")
    logger.info("Finished loading %s", table_name)


def ingest():
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

    logger.info("GTFS Sweden 3 ingestion completed.")


if __name__ == "__main__":
    logging.basicConfig(level=settings.log_level)
    ingest()


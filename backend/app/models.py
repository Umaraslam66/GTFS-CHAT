from datetime import date, time
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Float,
    Integer,
    String,
    Time,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Agency(Base):
    __tablename__ = "agency"

    agency_id = Column(String, primary_key=True)
    agency_name = Column(String, nullable=False)
    agency_url = Column(String, nullable=True)
    agency_timezone = Column(String, nullable=True)
    agency_lang = Column(String, nullable=True)
    agency_phone = Column(String, nullable=True)
    agency_fare_url = Column(String, nullable=True)
    agency_email = Column(String, nullable=True)


class Stop(Base):
    __tablename__ = "stops"

    stop_id = Column(String, primary_key=True)
    stop_code = Column(String)
    stop_name = Column(String, nullable=False, index=True)
    stop_desc = Column(String)
    stop_lat = Column(Float)
    stop_lon = Column(Float)
    location_type = Column(Integer)
    parent_station = Column(String)
    zone_id = Column(String)
    platform_code = Column(String)
    stop_timezone = Column(String)
    wheelchair_boarding = Column(Integer)

    __table_args__ = (Index("idx_stops_name", "stop_name"),)


class Route(Base):
    __tablename__ = "routes"

    route_id = Column(String, primary_key=True)
    agency_id = Column(String)
    route_short_name = Column(String)
    route_long_name = Column(String, index=True)
    route_desc = Column(String)
    route_type = Column(Integer, index=True)
    route_url = Column(String)
    route_color = Column(String)
    route_text_color = Column(String)


class Trip(Base):
    __tablename__ = "trips"

    route_id = Column(String, index=True)
    service_id = Column(String, index=True)
    trip_id = Column(String, primary_key=True)
    trip_headsign = Column(String)
    trip_short_name = Column(String)
    direction_id = Column(Integer, index=True)
    block_id = Column(String)
    shape_id = Column(String, index=True)
    wheelchair_accessible = Column(Integer)
    bikes_allowed = Column(Integer)

    __table_args__ = (
        Index("idx_trips_route_service", "route_id", "service_id"),
    )


class StopTime(Base):
    __tablename__ = "stop_times"

    trip_id = Column(String, primary_key=True)
    arrival_time = Column(String)
    departure_time = Column(String)
    stop_id = Column(String, primary_key=True, index=True)
    stop_sequence = Column(Integer, primary_key=True)
    stop_headsign = Column(String)
    pickup_type = Column(Integer)
    drop_off_type = Column(Integer)
    timepoint = Column(Integer)
    shape_dist_traveled = Column(Float)

    __table_args__ = (
        Index("idx_stoptimes_stop_seq", "stop_id", "stop_sequence"),
    )


class Calendar(Base):
    __tablename__ = "calendar"

    service_id = Column(String, primary_key=True)
    monday = Column(Boolean)
    tuesday = Column(Boolean)
    wednesday = Column(Boolean)
    thursday = Column(Boolean)
    friday = Column(Boolean)
    saturday = Column(Boolean)
    sunday = Column(Boolean)
    start_date = Column(Date)
    end_date = Column(Date)


class CalendarDate(Base):
    __tablename__ = "calendar_dates"
    __table_args__ = (UniqueConstraint("service_id", "date"),)

    service_id = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)
    exception_type = Column(Integer)  # 1 added, 2 removed


class Shape(Base):
    __tablename__ = "shapes"
    __table_args__ = (UniqueConstraint("shape_id", "shape_pt_sequence"),)

    shape_id = Column(String, primary_key=True)
    shape_pt_lat = Column(Float)
    shape_pt_lon = Column(Float)
    shape_pt_sequence = Column(Integer, primary_key=True)
    shape_dist_traveled = Column(Float)


class StopArea(Base):
    __tablename__ = "stop_areas"

    area_id = Column(String, primary_key=True)
    stop_id = Column(String, index=True)


class Area(Base):
    __tablename__ = "areas"

    area_id = Column(String, primary_key=True)
    area_name = Column(String, nullable=False)
    area_type = Column(String)


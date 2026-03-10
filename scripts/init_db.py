import os
import psycopg

DDL = """
create schema if not exists raw;
create schema if not exists analytics;

create table if not exists raw.gbfs_station_information_snapshot (
  snapshot_ts timestamptz not null,
  last_updated bigint not null,
  ttl integer,
  station_id text not null,
  name text,
  lat double precision,
  lon double precision,
  capacity integer,
  payload jsonb,
  primary key (snapshot_ts, station_id)
);

create table if not exists raw.gbfs_station_status_snapshot (
  snapshot_ts timestamptz not null,
  last_updated bigint not null,
  ttl integer,
  station_id text not null,
  num_bikes_available integer,
  num_docks_available integer,
  is_installed integer,
  is_renting integer,
  is_returning integer,
  last_reported bigint,
  payload jsonb,
  primary key (snapshot_ts, station_id)
);

create table if not exists raw.weather_hourly (
  hour_ts timestamptz not null,
  temperature_c double precision,
  precipitation_mm double precision,
  wind_speed double precision,
  weather_code integer,
  payload jsonb,
  primary key (hour_ts)
);

create index if not exists idx_status_station_time
  on raw.gbfs_station_status_snapshot (station_id, snapshot_ts);

create index if not exists idx_info_station_time
  on raw.gbfs_station_information_snapshot (station_id, snapshot_ts);
"""

def main() -> None:
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise SystemExit("DATABASE_URL is not set")

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()

    print("ok, schemas and tables are ready")

if __name__ == "__main__":
    main()

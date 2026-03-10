import os
import json
from datetime import datetime, timezone

import requests
import psycopg
from psycopg.types.json import Jsonb


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def fetch_json(url: str) -> dict:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

def as_int01(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return 1 if value else 0
    return int(value)

def get_feed_urls(gbfs_root_url: str, preferred_language: str | None = None) -> tuple[dict, str]:
    doc = fetch_json(gbfs_root_url)
    data = doc.get("data", {})

    if not data:
        raise SystemExit("gbfs.json has no data section")

    if preferred_language and preferred_language in data:
        language = preferred_language
    elif "en" in data:
        language = "en"
    else:
        language = next(iter(data.keys()))

    feeds = data[language]["feeds"]
    out = {}
    for f in feeds:
        out[f["name"]] = f["url"]

    return out, language


def insert_station_information(
    conn,
    snapshot_ts: datetime,
    last_updated: int,
    ttl: int | None,
    stations: list[dict],
) -> None:
    sql = """
    insert into raw.gbfs_station_information_snapshot
    (snapshot_ts, last_updated, ttl, station_id, name, lat, lon, capacity, payload)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    on conflict (snapshot_ts, station_id) do nothing
    """
    rows = []
    for s in stations:
        rows.append(
            (
                snapshot_ts,
                last_updated,
                ttl,
                s.get("station_id"),
                s.get("name"),
                s.get("lat"),
                s.get("lon"),
                s.get("capacity"),
                Jsonb(s),
            )
        )
    with conn.cursor() as cur:
        cur.executemany(sql, rows)


def insert_station_status(
    conn,
    snapshot_ts: datetime,
    last_updated: int,
    ttl: int | None,
    stations: list[dict],
) -> None:
    sql = """
    insert into raw.gbfs_station_status_snapshot
    (snapshot_ts, last_updated, ttl, station_id,
     num_bikes_available, num_docks_available,
     is_installed, is_renting, is_returning, last_reported, payload)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    on conflict (snapshot_ts, station_id) do nothing
    """
    rows = []
    for s in stations:
        rows.append(
            (
                snapshot_ts,
                last_updated,
                ttl,
                s.get("station_id"),
                s.get("num_bikes_available"),
                s.get("num_docks_available"),
                as_int01(s.get("is_installed")),
                as_int01(s.get("is_renting")),
                as_int01(s.get("is_returning")),
                s.get("last_reported"),
                Jsonb(s),
            )
        )
    with conn.cursor() as cur:
        cur.executemany(sql, rows)


def main() -> None:
    gbfs_root_url = os.environ.get("GBFS_ROOT_URL")
    db_url = os.environ.get("DATABASE_URL")

    if not gbfs_root_url:
        raise SystemExit("GBFS_ROOT_URL is not set")
    if not db_url:
        raise SystemExit("DATABASE_URL is not set")

    preferred_language = os.environ.get("GBFS_LANGUAGE")
    feeds, language_used = get_feed_urls(gbfs_root_url, preferred_language=preferred_language)
    print("gbfs_language_used", language_used)

    info_url = feeds.get("station_information")
    status_url = feeds.get("station_status")

    if not info_url or not status_url:
        raise SystemExit("Could not find station_information or station_status in gbfs.json")

    info = fetch_json(info_url)
    status = fetch_json(status_url)

    snapshot_ts = utc_now()

    with psycopg.connect(db_url) as conn:
        insert_station_information(
            conn,
            snapshot_ts,
            int(info["last_updated"]),
            info.get("ttl"),
            info["data"]["stations"],
        )
        insert_station_status(
            conn,
            snapshot_ts,
            int(status["last_updated"]),
            status.get("ttl"),
            status["data"]["stations"],
        )
        conn.commit()

    print("ok, inserted snapshot at", snapshot_ts.isoformat())


if __name__ == "__main__":
    main()

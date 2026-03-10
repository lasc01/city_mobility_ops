import os
import psycopg

CHECKS = [
    (
        "raw status has no null station_id",
        "select count(*) from raw.gbfs_station_status_snapshot where station_id is null;",
        0,
    ),
    (
        "raw status has no negative counts",
        """
        select count(*)
        from raw.gbfs_station_status_snapshot
        where num_bikes_available < 0 or num_docks_available < 0;
        """,
        0,
    ),
    (
        "fact snapshots do not exceed capacity",
        """
        select count(*)
        from analytics.fact_station_snapshot
        where capacity is not null
          and (
            num_bikes_available > capacity
            or num_docks_available > capacity
            or (num_bikes_available + num_docks_available) > capacity
          );
        """,
        0,
    ),
    (
        "weather is present in fact table",
        "select count(*) from analytics.fact_station_snapshot where temperature_c is null;",
        0,
    ),
    (
        "freshness, latest snapshot within 15 minutes",
        """
        select
          case
            when max(snapshot_ts) is null then 1
            when extract(epoch from age(current_timestamp, max(snapshot_ts))) > 900 then 1
            else 0
          end as fail
        from raw.gbfs_station_status_snapshot;
        """,
        0,
    ),
]

def main() -> None:
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise SystemExit("DATABASE_URL is not set")

    failures = []

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            for name, sql, expected in CHECKS:
                cur.execute(sql)
                value = cur.fetchone()[0]
                ok = value == expected
                print(name, "value", value, "expected", expected, "ok", ok)
                if not ok:
                    failures.append((name, value, expected))

    if failures:
        print("quality checks failed")
        for name, value, expected in failures:
            print("failed", name, "value", value, "expected", expected)
        raise SystemExit(1)

    print("all quality checks passed")

if __name__ == "__main__":
    main()

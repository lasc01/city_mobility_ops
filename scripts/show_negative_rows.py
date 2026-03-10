import os
import psycopg

def main():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise SystemExit("DATABASE_URL is not set")

    sql = """
    select
      snapshot_ts,
      station_id,
      num_bikes_available,
      num_docks_available
    from raw.gbfs_station_status_snapshot
    where num_bikes_available < 0
       or num_docks_available < 0
    order by snapshot_ts desc
    limit 25;
    """

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()

    for r in rows:
        print(r)

if __name__ == "__main__":
    main()

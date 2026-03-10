import os
import psycopg

def main() -> None:
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise SystemExit("DATABASE_URL is not set")

    sql = """
    select
      (select count(*) from raw.gbfs_station_information_snapshot) as info_rows,
      (select count(*) from raw.gbfs_station_status_snapshot) as status_rows,
      (select max(snapshot_ts) from raw.gbfs_station_status_snapshot) as latest_snapshot
    ;
    """

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            row = cur.fetchone()

    print("info_rows", row[0])
    print("status_rows", row[1])
    print("latest_snapshot", row[2])

if __name__ == "__main__":
    main()

import os
import psycopg

def main():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise SystemExit("DATABASE_URL is not set")

    sql = """
    select
      count(*) as weather_rows,
      min(hour_ts) as first_hour,
      max(hour_ts) as latest_hour
    from raw.weather_hourly
    ;
    """

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            row = cur.fetchone()

    print("weather_rows", row[0])
    print("first_hour", row[1])
    print("latest_hour", row[2])

if __name__ == "__main__":
    main()

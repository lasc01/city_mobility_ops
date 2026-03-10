import os
import psycopg

def main() -> None:
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise SystemExit("DATABASE_URL is not set")

    sql = """
    select
      (select count(*) from analytics.dim_station) as dim_station_rows,
      (select count(*) from analytics.fact_station_snapshot) as fact_rows,
      (select count(*) from analytics.mart_station_hourly) as station_hourly_rows,
      (select count(*) from analytics.mart_city_hourly) as city_hourly_rows
    ;
    """

    sample_sql = """
    select
      station_id,
      snapshot_hour_local,
      empty_rate,
      full_rate,
      service_level,
      avg_bikes_available,
      avg_docks_available
    from analytics.mart_station_hourly
    order by snapshot_hour_local desc, empty_rate desc
    limit 5
    ;
    """

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            print("counts", cur.fetchone())

            cur.execute(sample_sql)
            rows = cur.fetchall()

    for r in rows:
        print(r)

if __name__ == "__main__":
    main()

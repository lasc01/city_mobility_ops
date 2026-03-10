import os
from datetime import datetime, timezone

import requests
import psycopg
from psycopg.types.json import Jsonb


def fetch_json(url, params):
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def utc_from_unix(ts):
    return datetime.fromtimestamp(int(ts), tz=timezone.utc)


def upsert_weather_points(conn, points):
    sql = """
    insert into raw.weather_hourly
      (hour_ts, temperature_c, precipitation_mm, wind_speed, weather_code, payload)
    values
      (%s,%s,%s,%s,%s,%s)
    on conflict (hour_ts) do update set
      temperature_c = excluded.temperature_c,
      precipitation_mm = excluded.precipitation_mm,
      wind_speed = excluded.wind_speed,
      weather_code = excluded.weather_code,
      payload = excluded.payload
    ;
    """

    rows = []
    for p in points:
        hour_ts = utc_from_unix(p["dt"])

        main = p.get("main") or {}
        wind = p.get("wind") or {}

        temp_c = main.get("temp")
        wind_speed = wind.get("speed")

        weather_code = None
        weather_list = p.get("weather") or []
        if weather_list:
            weather_code = weather_list[0].get("id")

        precipitation_mm = 0.0
        rain = p.get("rain") or {}
        snow = p.get("snow") or {}
        if rain.get("3h") is not None:
            precipitation_mm += float(rain["3h"])
        if snow.get("3h") is not None:
            precipitation_mm += float(snow["3h"])

        rows.append(
            (
                hour_ts,
                temp_c,
                precipitation_mm,
                wind_speed,
                weather_code,
                Jsonb(p),
            )
        )

    with conn.cursor() as cur:
        cur.executemany(sql, rows)


def main():
    db_url = os.environ.get("DATABASE_URL")
    api_key = os.environ.get("OWM_API_KEY")
    base_url = os.environ.get("WEATHER_BASE_URL")
    city = os.environ.get("WEATHER_CITY", "Dublin")
    country = os.environ.get("WEATHER_COUNTRY", "IE")

    if not db_url:
        raise SystemExit("DATABASE_URL is not set")
    if not api_key:
        raise SystemExit("OWM_API_KEY is not set")
    if not base_url:
        raise SystemExit("WEATHER_BASE_URL is not set")

    params = {
        "q": f"{city},{country}",
        "appid": api_key,
        "units": "metric",
    }

    payload = fetch_json(base_url, params=params)
    points = payload.get("list") or []
    if not points:
        raise SystemExit("No forecast points returned")

    with psycopg.connect(db_url) as conn:
        upsert_weather_points(conn, points)
        conn.commit()

    print("ok, upserted forecast points", len(points))


if __name__ == "__main__":
    main()
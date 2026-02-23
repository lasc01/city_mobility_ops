import os
import psycopg

def main() -> None:
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise SystemExit("DATABASE_URL is not set")

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("select now()")
            row = cur.fetchone()
            print("db_time", row[0])

if __name__ == "__main__":
    main()

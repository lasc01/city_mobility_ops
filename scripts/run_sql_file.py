import os
import sys
import psycopg

def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/run_sql_file.py path_to_sql_file")

    path = sys.argv[1]
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise SystemExit("DATABASE_URL is not set")

    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()

    print("ok, executed", path)

if __name__ == "__main__":
    main()

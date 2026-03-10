import os
import psycopg

def main() -> None:
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise SystemExit("DATABASE_URL is not set")

    sql = """
    select table_schema, table_name
    from information_schema.tables
    where table_schema in ('raw', 'analytics')
    order by table_schema, table_name;
    """

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()

    for schema, name in rows:
        print(schema, name)

if __name__ == "__main__":
    main()

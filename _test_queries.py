"""Test both query styles against PG."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
load_dotenv()

url = os.environ.get('POSTGRES_DATABASE_URL', '')
engine = create_engine(url)

with engine.connect() as conn:
    # Simulate mdb_conn.execute_query translated SQL (unquoted table name)
    translated_sql = 'SELECT * FROM Educators LIMIT 5000'
    try:
        result = conn.execute(text(translated_sql))
        rows = [dict(r) for r in result.mappings().all()]
        print(f"mdb-style (unquoted) query returned {len(rows)} rows")
        if rows:
            r = rows[0]
            keys = list(r.keys())
            print(f"Keys: {keys[:15]}")
            print(f"actual = {r.get('actual')}")
            print(f"fname = {r.get('fname')}")
            print(f"natureofapointment = {r.get('natureofapointment')}")
    except Exception as e:
        print(f"mdb-style query ERROR: {e}")

    # Direct quoted query (pg_repo._rows path)
    result = conn.execute(text('SELECT * FROM "Educators"'))
    rows = [dict(r) for r in result.mappings().all()]
    print(f"\nDirect quoted query returned {len(rows)} rows")
    if rows:
        r = rows[0]
        keys = list(r.keys())
        print(f"Keys: {keys[:15]}")
        print(f"Actual = {r.get('Actual')}")
        print(f"NatureofApointment = {r.get('NatureofApointment')}")
        print(f"FName = {r.get('FName')}")

print("Done.")

"""Test what _management_build_staff_payload produces by simulating the backend."""
import os
from datetime import date
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
load_dotenv()

url = os.environ.get('POSTGRES_DATABASE_URL', '')
engine = create_engine(url)

# Simulate the SQL translation
print("=== Testing SQL translation ===")
sql = "SELECT TOP 5000 * FROM Educators"

# This is what _translate_access_to_postgres does:
import re
def _bracket_to_pg(match):
    ident = str(match.group(1) or "").strip()
    return '"' + ident.replace('"', '""') + '"'
q = re.sub(r"\[([^\]]+)\]", _bracket_to_pg, sql)
q = re.sub(r"^\s*SELECT\s+TOP\s+\d+\s+", "SELECT ", q, count=1, flags=re.IGNORECASE)
if not re.search(r"\bLIMIT\b", q, flags=re.IGNORECASE):
    q = q.rstrip().rstrip(";") + " LIMIT 5000"
print(f"Translated SQL: {q}")

# Execute it directly
with engine.connect() as conn:
    try:
        result = conn.execute(text(q))
        rows = [dict(r) for r in result.mappings().all()]
        print(f"Direct query returned {len(rows)} rows from Educators")
        if rows:
            print(f"Sample: {rows[0]}")
    except Exception as e:
        print(f"Direct query ERROR: {e}")

    # Test the fallback query
    try:
        result = conn.execute(text('SELECT * FROM "Educators"'))
        fallback_rows = [dict(r) for r in result.mappings().all()]
        print(f"\nFallback query returned {len(fallback_rows)} rows from Educators")
        if fallback_rows:
            print(f"Sample: EdID={fallback_rows[0].get('EdID')} FName={fallback_rows[0].get('FName')} SName={fallback_rows[0].get('SName')} Actual={fallback_rows[0].get('Actual')}")
    except Exception as e:
        print(f"Fallback query ERROR: {e}")

print("\nDone.")

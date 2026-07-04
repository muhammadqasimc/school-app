"""Check actual column names and data in PG Educators table."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
load_dotenv()

url = os.environ.get('POSTGRES_DATABASE_URL', '')
engine = create_engine(url)

with engine.connect() as conn:
    # Check columns
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'Educators'
        ORDER BY ordinal_position
    """))
    print("Educators columns:")
    for row in result:
        print(f"  {row[0]} ({row[1]})")
    
    # Sample data
    result = conn.execute(text('SELECT * FROM "Educators" LIMIT 3'))
    print("\nSample rows:")
    for row in result:
        print(f"  {dict(row)}")
    
    # Same for StaffMembers
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'StaffMembers'
        ORDER BY ordinal_position
    """))
    print("\nStaffMembers columns:")
    for row in result:
        print(f"  {row[0]} ({row[1]})")

print("Done.")

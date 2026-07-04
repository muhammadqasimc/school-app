"""Check if educators data exists in PostgreSQL (using SQLAlchemy to match the app)."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
load_dotenv()

url = os.environ.get('POSTGRES_DATABASE_URL', '')
print(f"Connecting to DB...")
engine = create_engine(url)

with engine.connect() as conn:
    # Check tables
    result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'Educators')"))
    exists = result.scalar()
    print(f"Educators table exists: {exists}")
    
    if exists:
        result = conn.execute(text('SELECT COUNT(*) FROM "Educators"'))
        print(f"Educators row count: {result.scalar()}")
    
    result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'StaffMembers')"))
    exists = result.scalar()
    print(f"StaffMembers table exists: {exists}")
    
    if exists:
        result = conn.execute(text('SELECT COUNT(*) FROM "StaffMembers"'))
        print(f"StaffMembers row count: {result.scalar()}")

    # Check sync_log
    result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sync_log')"))
    print(f"sync_log table exists: {result.scalar()}")

print("Done.")

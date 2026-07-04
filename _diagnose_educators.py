"""Diagnose why educator staff profile shows 0 records."""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Check PostgreSQL
try:
    import psycopg2
    url = os.environ.get('POSTGRES_DATABASE_URL', '')
    # Convert SQLAlchemy URL to psycopg2 URL
    pg_url = url.replace('postgresql+psycopg2://', 'postgresql://')
    print(f"PostgreSQL URL (original): {url}")
    print(f"PostgreSQL URL (psycopg2): {pg_url}")
    if '+psycopg2' in pg_url:
        pg_url = pg_url.replace('+psycopg2', '')
    conn = psycopg2.connect(pg_url)
    conn = psycopg2.connect(url)
    cur = conn.cursor()

    cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'Educators')")
    print(f"\nEducators table exists: {cur.fetchone()[0]}")

    cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'StaffMembers')")
    print(f"StaffMembers table exists: {cur.fetchone()[0]}")

    cur.execute('SELECT COUNT(*) FROM "Educators"')
    print(f"Educator count: {cur.fetchone()[0]}")

    cur.execute('SELECT COUNT(*) FROM "StaffMembers"')
    print(f"StaffMembers count: {cur.fetchone()[0]}")

    # Sample educator data
    cur.execute('SELECT "EdID", "FName", "SName", "Actual", "Status", "NatureofApointment", "Remuneration", "BirthDate" FROM "Educators" LIMIT 10')
    rows = cur.fetchall()
    print(f"\nEducator samples ({len(rows)}):")
    for r in rows:
        print(f"  EdID={r[0]} FName={r[1]} SName={r[2]} Actual={r[3]} Status={r[4]} Appointment={r[5]} Remuneration={r[6]} BirthDate={r[7]}")

    # Sample staff data
    cur.execute('SELECT "StaffID", "FName", "SName", "PersonnelCategory", "Status", "EmployType", "Remuneration", "BirthDate" FROM "StaffMembers" LIMIT 10')
    rows = cur.fetchall()
    print(f"\nStaffMember samples ({len(rows)}):")
    for r in rows:
        print(f"  StaffID={r[0]} FName={r[1]} SName={r[2]} PersonnelCategory={r[3]} Status={r[4]} EmployType={r[5]} Remuneration={r[6]} BirthDate={r[7]}")

    # Check distinct Actual roles in Educators
    cur.execute('SELECT DISTINCT "Actual" FROM "Educators"')
    roles = cur.fetchall()
    print(f"\nDistinct Actual roles in Educators: {[r[0] for r in roles]}")

    # Check distinct PersonnelCategory in StaffMembers
    cur.execute('SELECT DISTINCT "PersonnelCategory" FROM "StaffMembers"')
    cats = cur.fetchall()
    print(f"\nDistinct PersonnelCategory in StaffMembers: {[r[0] for r in cats]}")

    # Check distinct Status values
    cur.execute('SELECT DISTINCT "Status" FROM "Educators"')
    statuses = cur.fetchall()
    print(f"\nDistinct Status in Educators: {[r[0] for r in statuses]}")

    cur.execute('SELECT DISTINCT "Status" FROM "StaffMembers"')
    statuses = cur.fetchall()
    print(f"\nDistinct Status in StaffMembers: {[r[0] for r in statuses]}")

    # Check distinct NatureofApointment
    cur.execute('SELECT DISTINCT "NatureofApointment" FROM "Educators"')
    apps = cur.fetchall()
    print(f"\nDistinct NatureofApointment in Educators: {[r[0] for r in apps]}")

    # Check distinct Remuneration
    cur.execute('SELECT DISTINCT "Remuneration" FROM "Educators"')
    rems = cur.fetchall()
    print(f"\nDistinct Remuneration in Educators: {[r[0] for r in rems]}")

    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Check if MDB file exists
mdb_paths = [
    "K:\\KISMET SECONDARY 2026  JAN (1).mdb",
    "C:\\Users\\User\\Documents\\Reporting_app\\Reporting App\\KISMET SECONDARY 2026  JAN (1).mdb",
    "K:\\",
]
for p in mdb_paths:
    exists = os.path.exists(p)
    print(f"\nMDB path exists? {p} -> {exists}")
    if exists and os.path.isdir(p):
        try:
            files = [f for f in os.listdir(p) if f.lower().endswith('.mdb')]
            print(f"  MDB files in dir: {files}")
        except:
            pass

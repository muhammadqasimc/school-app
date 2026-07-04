"""Query the MDB file directly for educator data."""
import pyodbc

mdb_path = r"C:\Users\User\Documents\Reporting_app\Reporting App\KISMET SECONDARY 2026  JAN (1).mdb"
password = "Sit@dbe"

conn = pyodbc.connect(
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    f"DBQ={mdb_path};"
    f"PWD={password};"
)
cur = conn.cursor()

print("=== Educators table ===")
cur.execute("SELECT COUNT(*) FROM Educators")
print(f"Total rows: {cur.fetchone()[0]}")

cur.execute("SELECT EdID, FName, SName, Actual, NatureofApointment, Remuneration, Status, BirthDate FROM Educators ORDER BY SName, FName")
rows = cur.fetchall()
print(f"All rows ({len(rows)}):")
for r in rows:
    print(f"  EdID={r[0]} FName={r[1]} SName={r[2]} Actual={r[3]} Appointment={r[4]} Remuneration={r[5]} Status={r[6]} BirthDate={r[7]}")

print("\n=== StaffMembers table ===")
cur.execute("SELECT COUNT(*) FROM StaffMembers")
print(f"Total rows: {cur.fetchone()[0]}")

cur.execute("SELECT StaffID, FName, SName, PersonnelCategory, EmployType, Remuneration, Status, BirthDate FROM StaffMembers ORDER BY SName, FName")
rows = cur.fetchall()
print(f"First 30 rows:")
for r in rows[:30]:
    print(f"  StaffID={r[0]} FName={r[1]} SName={r[2]} PersonnelCategory={r[3]} EmployType={r[4]} Remuneration={r[5]} Status={r[6]} BirthDate={r[7]}")

print(f"\n... and remaining {max(0, len(rows)-30)} more rows")
if len(rows) > 30:
    print(f"--- Remaining rows (not shown) ---")
    for r in rows[30:]:
        print(f"  StaffID={r[0]} FName={r[1]} SName={r[2]} PersonnelCategory={r[3]} EmployType={r[4]} Remuneration={r[5]} Status={r[6]} BirthDate={r[7]}")

# Key question: what status values do we have?
cur.execute("SELECT DISTINCT Status FROM Educators")
print(f"\nDistinct Status in Educators: {[r[0] for r in cur.fetchall()]}")

cur.execute("SELECT DISTINCT Status FROM StaffMembers")
print(f"Distinct Status in StaffMembers: {[r[0] for r in cur.fetchall()]}")

cur.execute("SELECT DISTINCT Actual FROM Educators")
print(f"Distinct Actual (role) in Educators: {[r[0] for r in cur.fetchall()]}")

cur.execute("SELECT DISTINCT PersonnelCategory FROM StaffMembers")
print(f"Distinct PersonnelCategory in StaffMembers: {[r[0] for r in cur.fetchall()]}")

cur.execute("SELECT DISTINCT NatureofApointment FROM Educators")
print(f"Distinct NatureofApointment in Educators: {[r[0] for r in cur.fetchall()]}")

cur.execute("SELECT DISTINCT Remuneration FROM Educators")
print(f"Distinct Remuneration in Educators: {[r[0] for r in cur.fetchall()]}")

cur.execute("SELECT DISTINCT EmployType FROM StaffMembers")
print(f"Distinct EmployType in StaffMembers: {[r[0] for r in cur.fetchall()]}")

cur.close()
conn.close()

"""Check key data points for debugging."""
import psycopg2

conn = psycopg2.connect('postgresql://postgres:postgres@127.0.0.1:5432/reporting_app')
cur = conn.cursor()

# Check Yusraa's ReportMarks to see latest year
print("=== Yusraa (ID=90) ReportMarks dates ===")
cur.execute('SELECT DISTINCT "Datayear" FROM "ReportMarks" WHERE "LearnerID" = 90 ORDER BY "Datayear"')
for row in cur.fetchall():
    print(f"  Year={row[0]}")

# Check DebtorsTrans for DebAcc matching learner ID 90 or 1256
print("\n=== DebtorsTrans for DebAcc = 90 or DebAcc = 1256 ===")
cur.execute('SELECT * FROM "DebtorsTrans" WHERE "DebAcc" = 90 OR "DebAcc" = 1256 LIMIT 10')
cols = [desc[0] for desc in cur.description]
print(f"Columns: {cols}")
for row in cur.fetchall():
    print(f"  {row}")

# Check what DebAcc values exist
print("\n=== DebtorsTrans sample DebAcc values ===")
cur.execute('SELECT DISTINCT "DebAcc" FROM "DebtorsTrans" LIMIT 20')
for row in cur.fetchall():
    print(f"  DebAcc={row[0]}")

# Check Yusraa's AccessionNo
print("\n=== Yusraa AccessionNo ===")
cur.execute('SELECT "ID", "LearnerID", "AccessionNo" FROM "Learner_Info" WHERE "ID" = 90')
for row in cur.fetchall():
    print(f"  ID={row[0]}, LearnerID={row[1]}, AccessionNo={row[2]}")

# Check DisciplinaryRecords for Learnerid=90
print("\n=== DisciplinaryRecords for Learnerid=90 ===")
cur.execute('SELECT * FROM "DisciplinaryRecords" WHERE "Learnerid" = 90 ORDER BY "Date" DESC LIMIT 10')
cols = [desc[0] for desc in cur.description]
print(f"Columns: {cols}")
for row in cur.fetchall():
    print(f"  Date={row[2]}, Desc={row[6]}, Demerit={row[19]}, Merit={row[20]}, Year={row[18]}")

# Check Absentees for Learnerid=90  
print("\n=== Absentees for Learnerid=90 (with reasons) ===")
cur.execute("""
    SELECT a."DateAbsent", a."ReasonID", a."ReasonOther", ar."Reason"
    FROM "Absentees" a
    LEFT JOIN "AbsenteesReasons" ar ON ar."ReasonID" = a."ReasonID"
    WHERE a."Learnerid" = 90
    ORDER BY a."DateAbsent" DESC
    LIMIT 10
""")
for row in cur.fetchall():
    print(f"  Date={row[0]}, ReasonID={row[1]}, ReasonOther={row[2]}, Reason={row[3]}")

conn.close()

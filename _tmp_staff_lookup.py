import pyodbc

path = r"C:\Users\User\Documents\Reporting_app\Reporting App\KISMET SECONDARY 2026  JAN (1).mdb"
conn = pyodbc.connect(r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + path + ";PWD=Sit@dbe;")
cur = conn.cursor()

print("Educators sample")
cur.execute("SELECT TOP 20 EdID, FName, SName, Actual, Status FROM Educators WHERE Status='C' ORDER BY SName, FName")
for row in cur.fetchall():
    print(tuple(row))

print("\nStaffMembers educator-like sample")
cur.execute("SELECT TOP 200 StaffID, FName, SName, PersonnelCategory, Status FROM StaffMembers WHERE Status='C' ORDER BY SName, FName")
cats = ("educator", "teaching staff", "cs educator", "educator assistant", "teacher", "hod", "principal")
for row in cur.fetchall():
    c = str(row[3] or "").lower()
    if any(k in c for k in cats):
        print(tuple(row))
conn.close()

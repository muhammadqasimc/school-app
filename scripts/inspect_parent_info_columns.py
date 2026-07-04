import os
import pyodbc


def main() -> int:
    mdb_path = os.path.abspath(os.environ.get("MDB_FILE_PATH", "KISMET SECONDARY 2026  JAN (1).mdb"))
    password = os.environ.get("MDB_PASSWORD", "Sit@dbe")
    conn_str = r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + mdb_path + ";"
    if password:
        conn_str += "PWD=" + password + ";"
    con = pyodbc.connect(conn_str)
    cur = con.cursor()

    cur.execute("SELECT TOP 1 * FROM Parent_Info")
    cols = [d[0] for d in cur.description]
    print("Parent_Info columns:", len(cols))
    spouse_cols = [c for c in cols if any(k in c.lower() for k in ["spouse", "wife", "husband", "partner"])]
    print("Spouse-related columns:", spouse_cols)

    try:
        row = cur.execute("SELECT TOP 1 * FROM Parent_Info WHERE ParentID = ?", (1597,)).fetchone()
        if row:
            vals = dict(zip(cols, row))
            out = {k: vals.get(k) for k in cols if k in ("ParentID", "FName", "SName") or "spouse" in k.lower()}
            print("ParentID 1597 fields:", out)
    except Exception as e:
        print("Could not fetch ParentID 1597:", e)

    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

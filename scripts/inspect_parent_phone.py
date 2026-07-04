import os
import re

import pyodbc


def mask_phone(value: object) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    digits = re.sub(r"\D", "", s)
    if not digits:
        return None
    if len(digits) <= 4:
        return ("*" * max(0, len(digits) - 1)) + digits[-1:]
    return ("+" if s.startswith("+") else "") + ("*" * (len(digits) - 4)) + digits[-4:]


def main() -> None:
    mdb_path = os.environ.get("MDB_FILE_PATH", "KISMET SECONDARY 2026  JAN (1).mdb")
    password = os.environ.get("MDB_PASSWORD", "Sit@dbe")
    abs_path = os.path.abspath(mdb_path)

    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        r"DBQ=" + abs_path + ";"
    )
    if password:
        conn_str += r"PWD=" + password + ";"

    conn = pyodbc.connect(conn_str)
    cur = conn.cursor()

    # We saw these columns exist from /admin/inspect-mdb.
    for col in ["SpouseCell", "Tel1", "Tel2", "Tel3"]:
        try:
            sql = f"SELECT TOP 1 [{col}] FROM [Parent_Info] WHERE [{col}] IS NOT NULL AND Len(Trim([{col}])) > 0"
            row = cur.execute(sql).fetchone()
            if row and row[0]:
                print(f"Parent_Info.{col} -> {mask_phone(row[0])}")
                break
        except Exception:
            continue
    else:
        print("No non-empty values found in Parent_Info phone fields")

    conn.close()


if __name__ == "__main__":
    main()


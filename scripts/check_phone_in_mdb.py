import os
import re
import sys

import pyodbc


def normalize_sa_phone(raw: str) -> str:
    s = str(raw or "").strip()
    s = re.sub(r"[\s\-()]+", "", s)
    if s.startswith("00"):
        s = "+" + s[2:]
    if s.startswith("+"):
        return "+" + re.sub(r"\D", "", s[1:])
    return re.sub(r"\D", "", s)


def phone_variants(raw: str) -> list[str]:
    n = normalize_sa_phone(raw)
    if not n:
        return []
    out: list[str] = []

    def add(v: str):
        v = str(v).strip()
        if v and v not in out:
            out.append(v)

    add(n)
    digits = re.sub(r"\D", "", n)
    if digits:
        add(digits)

    # SA transforms
    if n.startswith("+27") and len(n) >= 12:
        add(n[1:])  # 27...
        add("0" + n[3:])  # 0...
    elif digits.startswith("0") and len(digits) == 10:
        add("+27" + digits[1:])
        add("27" + digits[1:])
    elif digits.startswith("27") and len(digits) == 11:
        add("+" + digits)
        add("0" + digits[2:])

    return out


def mask(v: object) -> str:
    s = str(v).strip()
    d = re.sub(r"\D", "", s)
    if len(d) <= 4:
        return ("*" * max(0, len(d) - 1)) + d[-1:]
    return ("+" if s.startswith("+") else "") + ("*" * (len(d) - 4)) + d[-4:]


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: py scripts\\check_phone_in_mdb.py <phone>")
        return 2

    raw = sys.argv[1]
    variants = phone_variants(raw)
    if not variants:
        print("Invalid/empty phone input.")
        return 2

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

    hits: list[tuple[str, str, str]] = []

    # Likely places based on your schema
    targets = [
        ("Parent_Info", "SpouseCell"),
        ("Parent_Info", "Tel1"),
        ("Parent_Info", "Tel2"),
        ("Parent_Info", "Tel3"),
        ("Learner_Info", "Tel1"),
        ("Learner_Info", "Tel2"),
        ("Learner_Info", "Tel3"),
    ]

    for table, col in targets:
        for v in variants:
            try:
                sql = f"SELECT TOP 1 [{col}] AS V FROM [{table}] WHERE [{col}] = ?"
                row = cur.execute(sql, (v,)).fetchone()
                if row and row[0] is not None:
                    hits.append((table, col, mask(row[0])))
                    break
            except Exception:
                continue
        if hits:
            break

    # If still no direct hit, try Parent_Child join (ParentId -> Parent_Info.ParentID)
    if not hits:
        for v in variants:
            try:
                sql = (
                    "SELECT TOP 1 pi.SpouseCell "
                    "FROM Parent_Child pc INNER JOIN Parent_Info pi ON pc.ParentId = pi.ParentID "
                    "WHERE pi.SpouseCell = ?"
                )
                row = cur.execute(sql, (v,)).fetchone()
                if row and row[0] is not None:
                    hits.append(("Parent_Info (via Parent_Child)", "SpouseCell", mask(row[0])))
                    break
            except Exception:
                continue

    conn.close()

    if hits:
        print("FOUND")
        for t, c, m in hits:
            print(f"- {t}.{c} -> {m}")
        return 0

    print("NOT FOUND (searched variants: " + ", ".join(variants) + ")")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())


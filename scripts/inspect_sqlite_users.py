import os
import sqlite3


def main() -> None:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(base, "dashboard.db")
    print("DB:", db_path)

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
    print("tables:", tables)

    try:
        rows = cur.execute(
            "SELECT id, username, phone, is_parent, first_login, created_at FROM user ORDER BY id DESC LIMIT 20"
        ).fetchall()
        print("users:", len(rows))
        for r in rows:
            print(r)
    except Exception as e:
        print("user query error:", e)

    con.close()


if __name__ == "__main__":
    main()


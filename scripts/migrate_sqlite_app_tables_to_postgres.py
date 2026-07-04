import os
import sqlite3

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


APP_TABLES = [
    "user",
    "user_learner",
    "otp_challenge",
    "profile_change_request",
    "profile_change_item",
    "teacher_audit_log",
    "teacher_term_lock",
    "teacher_announcement",
    "teacher_write_event",
    "user_teacher_assignment",
    "chat_thread",
    "chat_participant",
    "chat_message",
    "chat_attachment",
    "chat_message_receipt",
    "detention_notice",
]


def qident(name: str) -> str:
    return '"' + str(name).replace('"', '""') + '"'


def sqlite_columns(con: sqlite3.Connection, table: str) -> list[str]:
    rows = con.execute(f'PRAGMA table_info("{table}")').fetchall()
    return [r[1] for r in rows]


def pg_columns(conn, table: str) -> list[str]:
    rows = conn.execute(
        text(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema='public' AND table_name=:t
            ORDER BY ordinal_position
            """
        ),
        {"t": table},
    ).fetchall()
    return [r[0] for r in rows]


def pg_column_types(conn, table: str) -> dict[str, str]:
    rows = conn.execute(
        text(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema='public' AND table_name=:t
            """
        ),
        {"t": table},
    ).fetchall()
    return {r[0]: str(r[1]).lower() for r in rows}


def coerce_value(value, pg_type: str):
    if value is None:
        return None
    t = str(pg_type or "").lower()
    if t == "boolean":
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        s = str(value).strip().lower()
        if s in {"1", "true", "t", "yes", "y", "on"}:
            return True
        if s in {"0", "false", "f", "no", "n", "off", ""}:
            return False
        return bool(s)
    return value


def table_exists_sqlite(con: sqlite3.Connection, table: str) -> bool:
    row = con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (table,),
    ).fetchone()
    return bool(row)


def main():
    load_dotenv()
    pg_url = os.environ.get("POSTGRES_DATABASE_URL", "").strip()
    if not pg_url:
        raise RuntimeError("POSTGRES_DATABASE_URL is required")
    sqlite_path = os.path.abspath("dashboard.db")
    if not os.path.exists(sqlite_path):
        raise RuntimeError(f"SQLite source not found: {sqlite_path}")

    sqlite_con = sqlite3.connect(sqlite_path)
    sqlite_con.row_factory = sqlite3.Row
    engine = create_engine(pg_url, future=True)

    with engine.begin() as pg:
        for table in APP_TABLES:
            if not table_exists_sqlite(sqlite_con, table):
                print(f"{table}: skip (missing in sqlite)")
                continue
            dest_cols = pg_columns(pg, table)
            dest_types = pg_column_types(pg, table)
            if not dest_cols:
                print(f"{table}: skip (missing in postgres)")
                continue
            src_cols = sqlite_columns(sqlite_con, table)
            common = [c for c in src_cols if c in dest_cols]
            if not common:
                print(f"{table}: skip (no compatible columns)")
                continue

            src_sql = f'SELECT {", ".join(qident(c) for c in common)} FROM {qident(table)}'
            src_rows = sqlite_con.execute(src_sql).fetchall()

            pg.execute(text(f"TRUNCATE TABLE {qident(table)} RESTART IDENTITY CASCADE"))

            if src_rows:
                placeholders = ", ".join(f":{c}" for c in common)
                insert_sql = text(
                    f'INSERT INTO {qident(table)} ({", ".join(qident(c) for c in common)}) VALUES ({placeholders})'
                )
                batch = []
                for row in src_rows:
                    rec = {}
                    for c in common:
                        rec[c] = coerce_value(row[c], dest_types.get(c, ""))
                    batch.append(rec)
                pg.execute(insert_sql, batch)
            print(f"{table}: migrated {len(src_rows)} rows")

    sqlite_con.close()
    print("SQLite -> Postgres app-table migration complete")


if __name__ == "__main__":
    main()

import os
import shutil
from datetime import date, datetime, time
from decimal import Decimal

import pyodbc
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def qident(name: str) -> str:
    return '"' + str(name).replace('"', '""') + '"'


def resolve_latest_mdb(path_value: str) -> str:
    raw = str(path_value or "").strip()
    if len(raw) == 2 and raw[1] == ":":
        raw = raw + os.sep
    path = os.path.abspath(raw)
    recursive = os.environ.get("MDB_AUTOSELECT_RECURSIVE", "false").strip().lower() in {"1", "true", "yes", "on"}

    def latest_in_dir(base: str) -> str | None:
        latest = None
        latest_mtime = -1.0
        if recursive:
            for root, _, files in os.walk(base):
                for fname in files:
                    low = fname.lower()
                    if not (low.endswith(".mdb") or low.endswith(".accdb")):
                        continue
                    fpath = os.path.join(root, fname)
                    try:
                        mtime = os.path.getmtime(fpath)
                    except Exception:
                        continue
                    if mtime > latest_mtime:
                        latest_mtime = mtime
                        latest = fpath
        else:
            with os.scandir(base) as entries:
                for entry in entries:
                    if not entry.is_file():
                        continue
                    low = entry.name.lower()
                    if not (low.endswith(".mdb") or low.endswith(".accdb")):
                        continue
                    try:
                        mtime = entry.stat().st_mtime
                    except Exception:
                        continue
                    if mtime > latest_mtime:
                        latest_mtime = mtime
                        latest = entry.path
        return latest

    if os.path.isdir(path):
        latest = latest_in_dir(path)
        if latest:
            return latest
    if os.path.isfile(path):
        return path
    parent = os.path.dirname(path)
    if os.path.isdir(parent):
        latest = latest_in_dir(parent)
        if latest:
            return latest
    return path


def infer_pg_type(values) -> str:
    detected = set()
    for v in values:
        if v is None:
            continue
        if isinstance(v, bool):
            detected.add("boolean")
        elif isinstance(v, int):
            detected.add("bigint")
        elif isinstance(v, float):
            detected.add("double precision")
        elif isinstance(v, Decimal):
            detected.add("numeric")
        elif isinstance(v, datetime):
            detected.add("timestamp")
        elif isinstance(v, date):
            detected.add("date")
        elif isinstance(v, time):
            detected.add("time")
        elif isinstance(v, (bytes, bytearray, memoryview)):
            detected.add("bytea")
        else:
            detected.add("text")

    if not detected:
        return "text"
    if "text" in detected:
        return "text"
    if "bytea" in detected and len(detected) > 1:
        return "text"
    if "timestamp" in detected:
        return "timestamp"
    if "date" in detected and "time" not in detected:
        return "date"
    if "time" in detected and "date" not in detected:
        return "time"
    if "double precision" in detected:
        return "double precision"
    if "numeric" in detected:
        return "numeric"
    if "bigint" in detected:
        return "bigint"
    if "boolean" in detected:
        return "boolean"
    if "bytea" in detected:
        return "bytea"
    return "text"


CORE_TABLES = [
    "Learner_Info",
    "Parent_Info",
    "Parent_Child",
    "ReportMarks",
    "Subjects",
    "ReportCycles",
    "DisciplinaryRecords",
    "DisciplinaryLearnerMisconduct",
    "Absentees",
    "Educators",
    "StaffMembers",
    "Fees",
    "DebtorsTrans",
    "Journals",
    "Receipt_Info",
    "LearnerPromotion",
]


def copy_mdb_local(source_path: str) -> str:
    cache_dir = os.environ.get("MDB_LOCAL_CACHE_DIR", r"C:\mdb-cache")
    os.makedirs(cache_dir, exist_ok=True)
    basename = os.path.basename(source_path)
    if not basename:
        basename = "latest.mdb"
    target = os.path.join(cache_dir, basename)
    print(f"Copying MDB to local cache: {target}")
    shutil.copy2(source_path, target)
    return target


def choose_tables(all_tables: list[str]) -> list[str]:
    if os.environ.get("FULL_BOOTSTRAP", "false").strip().lower() in {"1", "true", "yes", "on"}:
        return all_tables
    raw = os.environ.get("BOOTSTRAP_TABLES", "").strip()
    if raw:
        requested = [x.strip() for x in raw.split(",") if x.strip()]
    else:
        requested = CORE_TABLES
    existing = {t.lower(): t for t in all_tables}
    chosen = []
    for name in requested:
        hit = existing.get(name.lower())
        if hit:
            chosen.append(hit)
    return chosen


def create_core_indexes(pg_conn) -> None:
    index_sql = [
        'CREATE INDEX IF NOT EXISTS idx_learner_info_id ON "Learner_Info" ("ID")',
        'CREATE INDEX IF NOT EXISTS idx_learner_info_learnerid ON "Learner_Info" ("LearnerID")',
        'CREATE INDEX IF NOT EXISTS idx_learner_info_accession ON "Learner_Info" ("AccessionNo")',
        'CREATE INDEX IF NOT EXISTS idx_parent_child_parent ON "Parent_Child" ("ParentId")',
        'CREATE INDEX IF NOT EXISTS idx_parent_child_child ON "Parent_Child" ("ChildId")',
        'CREATE INDEX IF NOT EXISTS idx_report_marks_learner ON "ReportMarks" ("LearnerID")',
        'CREATE INDEX IF NOT EXISTS idx_report_marks_year ON "ReportMarks" ("Datayear")',
        'CREATE INDEX IF NOT EXISTS idx_report_marks_subject ON "ReportMarks" ("SubjectId")',
        'CREATE INDEX IF NOT EXISTS idx_absentees_learner ON "Absentees" ("Learnerid")',
        'CREATE INDEX IF NOT EXISTS idx_absentees_year ON "Absentees" ("DataYear")',
        'CREATE INDEX IF NOT EXISTS idx_disc_records_learner ON "DisciplinaryRecords" ("Learnerid")',
        'CREATE INDEX IF NOT EXISTS idx_disc_records_year ON "DisciplinaryRecords" ("Datayear")',
        'CREATE INDEX IF NOT EXISTS idx_educators_edid ON "Educators" ("EdID")',
        'CREATE INDEX IF NOT EXISTS idx_staffmembers_staffid ON "StaffMembers" ("StaffID")',
    ]
    for sql in index_sql:
        try:
            pg_conn.execute(text(sql))
        except Exception:
            continue


def main():
    load_dotenv()
    pg_url = os.environ.get("POSTGRES_DATABASE_URL", "").strip()
    if not pg_url:
        raise RuntimeError("POSTGRES_DATABASE_URL is required")
    mdb_file = resolve_latest_mdb(os.environ.get("MDB_FILE_PATH", ""))
    if not os.path.exists(mdb_file):
        raise RuntimeError(f"MDB file not found: {mdb_file}")
    if os.environ.get("MDB_USE_LOCAL_CACHE", "true").strip().lower() in {"1", "true", "yes", "on"}:
        mdb_file = copy_mdb_local(mdb_file)

    password = os.environ.get("MDB_PASSWORD", "Sit@dbe")
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={mdb_file};"
    )
    if password:
        conn_str += f"PWD={password};"

    print(f"Using MDB: {mdb_file}")
    mdb_conn = pyodbc.connect(conn_str)
    mdb_cur = mdb_conn.cursor()

    engine = create_engine(pg_url, future=True)

    all_tables = [r.table_name for r in mdb_cur.tables(tableType="TABLE")]
    tables = choose_tables(all_tables)
    print(f"Found {len(all_tables)} MDB tables; bootstrapping {len(tables)} selected tables")

    batch_size = max(500, int(os.environ.get("BOOTSTRAP_BATCH_SIZE", "5000")))
    for idx, table in enumerate(tables, start=1):
        with engine.begin() as pg_conn:
            qtable = qident(table)
            print(f"[{idx}/{len(tables)}] {table}")
            try:
                mdb_cur.execute(f"SELECT * FROM [{table}]")
                col_names = [d[0] for d in mdb_cur.description]
            except Exception as exc:
                print(f"  skip: cannot read table ({exc})")
                continue

            rows = mdb_cur.fetchmany(batch_size)
            samples_by_col = {c: [] for c in col_names}
            for row in rows:
                for i, c in enumerate(col_names):
                    samples_by_col[c].append(row[i])

            col_defs = []
            for c in col_names:
                pg_type = infer_pg_type(samples_by_col[c])
                col_defs.append(f"{qident(c)} {pg_type}")

            pg_conn.execute(text(f"DROP TABLE IF EXISTS {qtable} CASCADE"))
            pg_conn.execute(text(f"CREATE TABLE {qtable} ({', '.join(col_defs)})"))

            insert_cols = ", ".join(qident(c) for c in col_names)
            insert_vals = ", ".join(f":c{i}" for i in range(len(col_names)))
            insert_sql = text(f"INSERT INTO {qtable} ({insert_cols}) VALUES ({insert_vals})")

            total = 0
            batch = []
            for row in rows:
                batch.append({f"c{i}": row[i] for i in range(len(col_names))})
            if batch:
                pg_conn.execute(insert_sql, batch)
                total += len(batch)

            while True:
                rows = mdb_cur.fetchmany(batch_size)
                if not rows:
                    break
                batch = [{f"c{i}": r[i] for i in range(len(col_names))} for r in rows]
                pg_conn.execute(insert_sql, batch)
                total += len(batch)

            print(f"  inserted rows: {total}")

    with engine.begin() as pg_conn:
        create_core_indexes(pg_conn)
    print("Created/verified core indexes")

    mdb_cur.close()
    mdb_conn.close()
    print("Bootstrap complete")


if __name__ == "__main__":
    main()


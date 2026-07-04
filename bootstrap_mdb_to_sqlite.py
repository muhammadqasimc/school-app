"""
bootstrap_mdb_to_sqlite.py
Convert all MDB tables to a local SQLite database for fast queries.
MDB is read-only once at startup; all subsequent queries hit SQLite.
"""

import json
import logging
import os
import sqlite3
import subprocess
import sys
from datetime import datetime

MDB_PATH = os.environ.get(
    "MDB_FILE_PATH",
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "KISMET_JUNE_2026.mdb"),
)
SQLITE_PATH = os.environ.get(
    "SCHOOL_DATA_DB",
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "school_data.db"),
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("bootstrap")

# Tables the app actually needs
REQUIRED_TABLES = {
    "Learner_Info", "ReportMarks", "Absentees", "DisciplinaryRecords",
    "Parent_Info", "Parent_Child", "Educators", "StaffMembers",
    "DebtorsTrans", "Fees", "Subjects", "Classes", "SchoolTerms",
    "ReportCycles", "LearnerClasses", "SubjectSets", "LearnerSubjects",
    "LearnerCass", "17_3_0_ReportMarks", "17_3_0_LearnerCass",
    "DemeritMeritSettings", "Disciplinarycodelist",
    "LearnerPromotion", "17_3_0_LearnerPromotion",
    "LearnerAttendance", "FeederSchools",
    "EducatorSubjectsTaught", "AcademicYear",
    "SubjectsOfficial", "GradeSubjectSets",
    "Colours", "DisciplinaryConsequences",
    "FormLetters", "SchoolInfo", "Settings",
    "Journals", "ChartAccountsTable",
    "ReasonCodes", "TransactionTypes",
}


def get_all_tables(mdb_path: str) -> list[str]:
    """Get all user tables from the MDB."""
    try:
        proc = subprocess.run(
            ["mdb-tables", "-1", mdb_path],
            capture_output=True, text=True, timeout=30,
        )
        if proc.returncode != 0:
            log.error("mdb-tables failed: %s", proc.stderr)
            return []
        tables = [t.strip() for t in proc.stdout.splitlines() if t.strip()]
        return [t for t in tables if not t.startswith("MSys")]
    except Exception as e:
        log.error("Failed to list tables: %s", e)
        return []


def export_table(mdb_path: str, table_name: str) -> list[dict]:
    """Export a single table using mdb-json."""
    try:
        proc = subprocess.run(
            ["mdb-json", mdb_path, table_name],
            capture_output=True, text=True, timeout=120,
        )
        if proc.returncode != 0:
            log.warning("mdb-json failed for %s: %s", table_name, proc.stderr[:200])
            return []
        rows = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                rows.append(row)
            except json.JSONDecodeError:
                continue
        return rows
    except Exception as e:
        log.warning("Error exporting %s: %s", table_name, e)
        return []


def detect_column_type(values: list) -> str:
    """Detect the best SQLite column type from sample values."""
    types_found = set()
    for v in values:
        if v is None:
            continue
        if isinstance(v, bool):
            types_found.add("INTEGER")
        elif isinstance(v, int):
            types_found.add("INTEGER")
        elif isinstance(v, float):
            types_found.add("REAL")
        elif isinstance(v, str):
            types_found.add("TEXT")
        else:
            types_found.add("TEXT")
    if "REAL" in types_found:
        return "REAL"
    if "INTEGER" in types_found:
        return "INTEGER"
    return "TEXT"


def create_table_from_rows(conn: sqlite3.Connection, table_name: str, rows: list[dict]):
    """Create a SQLite table from a list of dicts, infer types from data."""
    if not rows:
        log.warning("No data for %s, skipping", table_name)
        return

    # Collect all column names (preserving order from first row)
    all_keys = list(rows[0].keys())
    # Some tables have extra columns in later rows
    for row in rows[1:]:
        for k in row:
            if k not in all_keys:
                all_keys.append(k)

    # Detect type per column from ALL rows
    col_types = {}
    for key in all_keys:
        vals = [row.get(key) for row in rows]
        col_types[key] = detect_column_type(vals)

    # Sanitize column names (brackets, spaces, etc.)
    def sanitize(name: str) -> str:
        return name.replace("[", "").replace("]", "").replace(" ", "_").replace("/", "_").replace("-", "_")

    col_defs = []
    col_map = {}  # original -> sanitized
    for key in all_keys:
        sk = sanitize(key)
        col_map[key] = sk
        col_defs.append(f'"{sk}" {col_types[key]}')

    # Drop existing table
    table_name_clean = table_name.replace("[", "").replace("]", "")
    conn.execute(f'DROP TABLE IF EXISTS "{table_name_clean}"')

    # Create table
    joined_defs = ",\n  ".join(col_defs)
    create_sql = f'CREATE TABLE "{table_name_clean}" (\n  {joined_defs}\n)'
    try:
        conn.execute(create_sql)
    except Exception as e:
        log.error("Failed to create table %s: %s", table_name_clean, e)
        log.error("SQL: %s", create_sql[:500])
        return

    # Insert data in batches
    placeholders = ", ".join(["?" for _ in all_keys])
    cols_quoted = ", ".join(f'"{col_map[k]}"' for k in all_keys)
    insert_sql = f'INSERT INTO "{table_name_clean}" ({cols_quoted}) VALUES ({placeholders})'

    batch = []
    for row in rows:
        values = []
        for key in all_keys:
            v = row.get(key)
            # Convert types for SQLite
            if v is not None and col_types.get(key) == "INTEGER" and not isinstance(v, (int, bool)):
                try:
                    v = int(v)
                except (ValueError, TypeError):
                    v = 0
            elif v is not None and col_types.get(key) == "REAL" and not isinstance(v, (int, float)):
                try:
                    v = float(v)
                except (ValueError, TypeError):
                    v = 0.0
            elif v is not None and col_types.get(key) == "TEXT":
                v = str(v)[:10000]  # Cap text length
            values.append(v)
        batch.append(tuple(values))

        if len(batch) >= 1000:
            conn.executemany(insert_sql, batch)
            batch = []

    if batch:
        conn.executemany(insert_sql, batch)

    conn.commit()
    count = len(rows)
    log.info("  %s: %d rows", table_name_clean, count)


def main():
    log.info("MDB path: %s", MDB_PATH)
    log.info("SQLite path: %s", SQLITE_PATH)

    if not os.path.isfile(MDB_PATH):
        log.error("MDB file not found: %s", MDB_PATH)
        sys.exit(1)

    all_tables = get_all_tables(MDB_PATH)
    log.info("Found %d tables in MDB", len(all_tables))

    # Connect to SQLite (WAL mode for better concurrent reads)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=OFF")  # Fast bulk insert
    conn.execute("PRAGMA temp_store=MEMORY")

    # First export required tables
    priority_tables = REQUIRED_TABLES & set(all_tables)
    other_tables = [t for t in all_tables if t not in priority_tables]

    log.info("Exporting %d priority tables...", len(priority_tables))
    for i, table in enumerate(sorted(priority_tables)):
        log.info("[%d/%d] Exporting %s...", i + 1, len(priority_tables), table)
        try:
            rows = export_table(MDB_PATH, table)
            create_table_from_rows(conn, table, rows)
        except Exception as e:
            log.error("Failed on %s: %s", table, e)

    log.info("Exporting remaining %d tables...", len(other_tables))
    for i, table in enumerate(sorted(other_tables)):
        log.info("[%d/%d] Exporting %s...", i + 1, len(other_tables), table)
        try:
            rows = export_table(MDB_PATH, table)
            create_table_from_rows(conn, table, rows)
        except Exception as e:
            log.error("Failed on %s: %s", table, e)

    conn.close()

    db_size = os.path.getsize(SQLITE_PATH)
    log.info("Done! SQLite database: %s (%d MB)", SQLITE_PATH, db_size // (1024 * 1024))


if __name__ == "__main__":
    start = datetime.now()
    main()
    elapsed = (datetime.now() - start).total_seconds()
    log.info("Total time: %.1f seconds", elapsed)

# MDB <-> PostgreSQL Sync and Flask Cutover

This project now supports a PostgreSQL runtime cutover while keeping the legacy Microsoft Access MDB file as the source of truth for the Windows app.

## What changed

- Flask SQLAlchemy now reads `POSTGRES_DATABASE_URL` for the main app DB.
- `mdb_conn` calls in `app.py` run in PostgreSQL compatibility mode (`POSTGRES_MDB_COMPAT_MODE=true` by default), so existing route code executes against PostgreSQL.
- A bidirectional sync worker (`sync_service.py`) keeps MDB and PostgreSQL in sync every 2 minutes.
- Sync uses Last-Write-Wins based on `updated_at` and tracks deltas in a `sync_log` table.

## Required environment variables

- `POSTGRES_DATABASE_URL`  
  Example: `postgresql+psycopg2://user:password@host:5432/dbname`

- `MDB_FILE_PATH`  
  Full path to `.mdb` file (network path over Tailscale/SMB is supported).

- `MDB_PASSWORD`  
  Set if the MDB file is password-protected.

- `SYNC_TABLE_CONFIG`  
  JSON array describing table sync mappings.

Example:

```json
[
  {
    "table_name": "Learner_Info",
    "primary_key": "ID",
    "updated_at_col": "updated_at",
    "columns": ["ID", "LearnerID", "FName", "SName", "Grade", "updated_at"],
    "mode": "delta",
    "bidirectional": true
  },
  {
    "table_name": "DisciplinaryRecords",
    "primary_key": "id",
    "updated_at_col": "updated_at",
    "columns": ["id", "Learnerid", "Datayear", "Comment", "Demerit", "Merit", "updated_at"],
    "mode": "delta",
    "bidirectional": true
  },
  {
    "table_name": "AbsenteesReasons",
    "primary_key": "ReasonID",
    "updated_at_col": "",
    "columns": ["ReasonID", "Reason"],
    "mode": "full_refresh",
    "bidirectional": false
  },
  {
    "table_name": "Staff_CalendarTerms",
    "primary_key": "TermID",
    "updated_at_col": "",
    "columns": ["TermID", "CurrentYear", "Term", "StartDate", "EndDate"],
    "mode": "full_refresh",
    "bidirectional": false
  },
  {
    "table_name": "Staff_CalendarWeekSetup",
    "primary_key": "WeekID",
    "updated_at_col": "",
    "columns": ["WeekID", "TermID", "Holiday"],
    "mode": "full_refresh",
    "bidirectional": false
  }
]
```

## Optional environment variables

- `POSTGRES_MDB_COMPAT_MODE` (default `true`)  
  Keep `true` to run existing MDB-style queries against PostgreSQL.

- `ENABLE_SYNC_THREAD` (default `false`)  
  If `true`, starts sync worker thread during Flask startup.

- `SYNC_INTERVAL_SECONDS` (default `120`)
- `SYNC_MDB_MAX_RETRIES` (default `5`)
- `SYNC_MDB_RETRY_BASE_MS` (default `300`)
- `MDB_USE_LOCAL_CACHE` (default `true`)  
  Copies latest MDB from `K:` (or configured path) to local disk for faster readonly sync scans.
- `MDB_LOCAL_CACHE_DIR` (default `C:\\mdb-cache`)

## Running sync

### One-off sync burst

```bash
flask sync-once
```

### Foreground daemon sync

```bash
flask sync-daemon
```

### Embedded background thread

Set:

- `ENABLE_SYNC_THREAD=true`
- `SYNC_INTERVAL_SECONDS=120`

Then run Flask normally.

## Conflict handling

- Sync is bidirectional:
  - MDB delta -> PostgreSQL upsert
  - PostgreSQL delta -> MDB upsert
- Last-Write-Wins compares `updated_at` timestamps.
- Watermarks are stored per direction/per table in PostgreSQL table `sync_log`.

## MDB lock handling and network share notes

- MDB reads use read-only mode to reduce lock contention.
- MDB connections are opened for short bursts and closed immediately.
- Writes retry on lock/sharing errors with exponential backoff.
- For Tailscale/SMB paths:
  - keep sync interval at 120s or higher,
  - avoid running multiple sync workers against the same MDB file,
  - ensure the service account has stable file-share permissions.

## Recommended rollout

1. Seed PostgreSQL tables from current MDB snapshot.
2. Start with `flask sync-once` and verify row counts.
3. Enable `flask sync-daemon` (or background thread).
4. Point app runtime to `POSTGRES_DATABASE_URL`.
5. Monitor logs for lock retries and translation failures.

## Important limitations

- `POSTGRES_MDB_COMPAT_MODE` translates common Access SQL patterns (`TOP`, `CSTR`, `UCASE`, bracket identifiers, etc.) to PostgreSQL syntax.
- If a specific legacy query uses uncommon Access-only functions, add a targeted translation rule in `MDBConnection._translate_access_to_postgres`.

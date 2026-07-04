# MDB Write Safety Protocol

This project shares a live Microsoft Access `.mdb` file with SAMS.  
To reduce corruption risk and lock contention, **all MDB writes must follow one path and one policy**.

## Golden Rule

- Use `MDBConnection.execute_non_query(...)` for **every** MDB write.
- Do not call `pyodbc` write operations directly from routes/services.
- Keep MDB write SQL to `INSERT` and `UPDATE` only.

## Current Safety Controls (Already Enforced in Code)

- Global in-process lock for MDB operations (serializes access per app process).
- Write kill-switch with environment variable:
  - `MDB_WRITES_ENABLED=true|false` (default `true`)
- Write allowlist (table-level):
  - `DisciplinaryLearnerMisconduct`
  - `DisciplinaryRecords`
  - `Learner_Info`
  - `Parent_Info`
  - `Absentees`
  - `ReportMarks`
- Lock-aware retries for transient Access lock errors with exponential backoff:
  - `MDB_WRITE_MAX_RETRIES` (default `4`)
  - `MDB_WRITE_RETRY_BASE_MS` (default `250`)
- Connection reset between retries to recover stale lock handles.

## Required Pattern For New MDB Writes

1. Validate permissions and input in route/service.
2. Build parameterized SQL (`?` placeholders).
3. Call `mdb_conn.execute_non_query(sql, params)`.
4. Handle `0` rows safely (do not assume success).
5. Return a user-safe message; avoid exposing internal DB errors.

## Example

```python
sql = "UPDATE ReportMarks SET Mark=?, CASS=?, ExamMark=?, TotalMark=? WHERE Id=?"
affected = mdb_conn.execute_non_query(sql, (mark, mark, 0, total_mark, row_id))
if affected <= 0:
    return jsonify({"error": "Unable to save at the moment. Please retry."}), 503
```

## If You Need A New Writable MDB Table

Before writing to a new table:

1. Add the table to `MDBConnection._SAFE_WRITE_TABLES` in `app.py`.
2. Document why write access is needed.
3. Keep query parameterized and minimal (single row where possible).
4. Test while SAMS is active to confirm lock-retry behavior.

## Production Recommendations

- Prefer running a **single app instance** when writing to shared MDB.
- Keep frequent backups of the MDB file.
- Use least-privilege filesystem permissions for the app account.
- If lock failures rise, temporarily disable writes with:
  - `MDB_WRITES_ENABLED=false`

## What Not To Do

- Do not run DDL (`CREATE`, `ALTER`, `DROP`) against live MDB.
- Do not concatenate user input into SQL.
- Do not bypass `execute_non_query`.


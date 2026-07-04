import json
import logging
import os
import re
import shutil
import threading
import time
from dataclasses import dataclass
from dataclasses import field
from datetime import date
from datetime import datetime, timezone
from datetime import time as dt_time
from decimal import Decimal
from typing import Any, Callable

import pyodbc
from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, LargeBinary, MetaData, Numeric, String, Table, create_engine, insert, inspect, select, update

logger = logging.getLogger(__name__)


LOCK_TOKENS = ("locked", "could not lock file", "file already in use", "sharing violation", "database is locked")


@dataclass
class TableSyncConfig:
    table_name: str
    primary_key: str = ""
    updated_at_col: str = ""
    columns: list[str] = field(default_factory=list)
    mode: str = "delta"  # delta | full_refresh
    bidirectional: bool = True


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo:
            return value.astimezone(timezone.utc)
        return value.replace(tzinfo=timezone.utc)
    return None


def parse_sync_config(raw: str | None) -> list[TableSyncConfig]:
    if not raw:
        return []
    data = json.loads(raw)
    out: list[TableSyncConfig] = []
    for item in data:
        out.append(
            TableSyncConfig(
                table_name=str(item["table_name"]),
                primary_key=str(item.get("primary_key", "")),
                updated_at_col=str(item.get("updated_at_col", "")),
                columns=[str(c) for c in (item.get("columns") or [])],
                mode=str(item.get("mode", "delta") or "delta").strip().lower(),
                bidirectional=bool(item.get("bidirectional", True)),
            )
        )
    return out


class SyncService:
    def __init__(
        self,
        *,
        mdb_path: str,
        postgres_url: str,
        table_configs: list[TableSyncConfig],
        mdb_password: str | None = None,
        max_retries: int = 4,
        retry_base_ms: int = 300,
        progress_log: Callable[[str, str], None] | None = None,
    ):
        self.mdb_path = mdb_path
        self.mdb_password = mdb_password
        self.postgres_url = postgres_url
        self.table_configs = table_configs
        self.max_retries = max(0, int(max_retries))
        self.retry_base_ms = max(50, int(retry_base_ms))
        self.stop_event = threading.Event()
        self.engine = create_engine(postgres_url, pool_pre_ping=True, future=True)
        self.progress_log = progress_log
        self._pg_table_cache: dict[str, Table] = {}
        self.use_local_cache = os.environ.get("MDB_USE_LOCAL_CACHE", "false").strip().lower() in {"1", "true", "yes", "on"}
        self.local_cache_dir = os.environ.get("MDB_LOCAL_CACHE_DIR", r"C:\mdb-cache")
        self._source_mdb_path = ""
        self._cached_mdb_path = ""
        self.meta = MetaData()
        self.sync_log = Table(
            "sync_log",
            self.meta,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("sync_key", String(255), nullable=False, unique=True),
            Column("last_sync_timestamp", DateTime(timezone=True), nullable=False),
            Column("updated_at", DateTime(timezone=True), nullable=False),
        )
        self.meta.create_all(self.engine, tables=[self.sync_log])

    def _progress(self, message: str, level: str = "info") -> None:
        lvl = (level or "info").lower()
        if lvl == "error":
            logger.error("%s", message)
        elif lvl == "warning":
            logger.warning("%s", message)
        else:
            logger.info("%s", message)
        pl = self.progress_log
        if pl:
            try:
                pl(message, level)
            except Exception:
                pass

    def _get_pg_table(self, table_name: str) -> Table:
        """
        Reflect table metadata once per name. Re-using reflection on every row was
        pathologically slow (often looks like a hang after "Sync thread starting").
        """
        if table_name not in self._pg_table_cache:
            self._pg_table_cache[table_name] = Table(table_name, MetaData(), autoload_with=self.engine)
        return self._pg_table_cache[table_name]

    def _is_lock_error(self, exc: Exception) -> bool:
        msg = str(exc or "").lower()
        return any(token in msg for token in LOCK_TOKENS)

    @staticmethod
    def _latest_mdb_in_dir(directory: str, recursive: bool = False) -> str | None:
        latest_path = None
        latest_mtime = -1.0
        try:
            if recursive:
                for root, _, files in os.walk(directory):
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
                            latest_path = fpath
            else:
                with os.scandir(directory) as entries:
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
                            latest_path = entry.path
        except Exception:
            return None
        return latest_path

    def _resolve_mdb_path(self) -> str:
        raw_path = str(self.mdb_path or "").strip()
        if re.fullmatch(r"[A-Za-z]:", raw_path):
            raw_path = raw_path + os.sep
        path = os.path.abspath(raw_path)
        recursive = os.environ.get("MDB_AUTOSELECT_RECURSIVE", "false").strip().lower() in {"1", "true", "yes", "on"}
        if os.path.isdir(path):
            latest = self._latest_mdb_in_dir(path, recursive=recursive)
            if latest:
                return latest
        if os.path.isfile(path):
            return path
        parent = os.path.dirname(path)
        if os.path.isdir(parent):
            latest = self._latest_mdb_in_dir(parent, recursive=recursive)
            if latest:
                return latest
        return path

    def _refresh_local_cache(self) -> None:
        """Copy latest network MDB to local disk for faster readonly scans."""
        self._source_mdb_path = self._resolve_mdb_path()
        self._cached_mdb_path = self._source_mdb_path
        if not self.use_local_cache:
            return
        if not os.path.isfile(self._source_mdb_path):
            return
        try:
            os.makedirs(self.local_cache_dir, exist_ok=True)
            base = os.path.basename(self._source_mdb_path) or "latest.mdb"
            target = os.path.join(self.local_cache_dir, base)
            src_mtime = os.path.getmtime(self._source_mdb_path)
            dst_mtime = os.path.getmtime(target) if os.path.exists(target) else -1
            if (not os.path.exists(target)) or src_mtime > dst_mtime:
                self._progress(
                    f"Copying MDB to local cache (slow on network shares): {base}…",
                    "info",
                )
                shutil.copy2(self._source_mdb_path, target)
                logger.info("mdb cache refreshed: %s", target)
            self._cached_mdb_path = target
        except Exception as exc:
            logger.warning("mdb cache refresh failed, using source path: %s", exc)
            self._cached_mdb_path = self._source_mdb_path

    @staticmethod
    def _build_conn_str(db_path: str, readonly: bool, password: str | None) -> str:
        conn_str = (
            r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
            f"DBQ={db_path};"
        )
        if password:
            conn_str += f"PWD={password};"
        return conn_str

    def _mdb_connect(self, readonly: bool) -> pyodbc.Connection:
        if not self._source_mdb_path:
            self._refresh_local_cache()
        resolved_path = self._cached_mdb_path if (readonly and self.use_local_cache) else self._source_mdb_path

        def _connect(path: str, password: str | None):
            return pyodbc.connect(self._build_conn_str(path, readonly, password), autocommit=False)

        try:
            return _connect(resolved_path, self.mdb_password)
        except pyodbc.Error as exc:
            msg = str(exc or "").lower()
            # Cached copy can occasionally be invalid/corrupt while source file is fine.
            if readonly and resolved_path != self._source_mdb_path and (
                "unrecognized database format" in msg
                or "-1206" in msg
                or "no read permission" in msg
                or "-1907" in msg
            ):
                logger.warning("cached MDB access failed; retrying from source MDB path")
                return _connect(self._source_mdb_path, self.mdb_password)
            # Some environments store MDB without password; retry plain DSN once.
            if self.mdb_password and ("no read permission" in msg or "-1907" in msg):
                logger.warning("MDB read permission denied with configured password; retrying without password")
                if readonly and resolved_path != self._source_mdb_path:
                    try:
                        return _connect(self._source_mdb_path, None)
                    except pyodbc.Error:
                        pass
                return _connect(resolved_path, None)
            raise

    def _run_retry(self, fn, label: str):
        for attempt in range(self.max_retries + 1):
            try:
                return fn()
            except pyodbc.Error as exc:
                if (not self._is_lock_error(exc)) or attempt >= self.max_retries:
                    raise
                delay = (self.retry_base_ms * (2 ** attempt)) / 1000.0
                logger.warning("%s lock contention, retrying in %.2fs", label, delay)
                time.sleep(delay)

    def _sync_key(self, direction: str, table: str) -> str:
        return f"{direction}:{table}"

    def _get_last_sync(self, key: str) -> datetime:
        with self.engine.begin() as conn:
            row = conn.execute(select(self.sync_log.c.last_sync_timestamp).where(self.sync_log.c.sync_key == key)).first()
            if row and row[0]:
                return as_utc(row[0]) or datetime(1970, 1, 1, tzinfo=timezone.utc)
            return datetime(1970, 1, 1, tzinfo=timezone.utc)

    def _set_last_sync(self, key: str, ts: datetime) -> None:
        ts = as_utc(ts) or utcnow()
        now = utcnow()
        with self.engine.begin() as conn:
            exists = conn.execute(select(self.sync_log.c.id).where(self.sync_log.c.sync_key == key)).first()
            if exists:
                conn.execute(
                    update(self.sync_log)
                    .where(self.sync_log.c.sync_key == key)
                    .values(last_sync_timestamp=ts, updated_at=now)
                )
            else:
                conn.execute(
                    insert(self.sync_log).values(sync_key=key, last_sync_timestamp=ts, updated_at=now)
                )

    def _fetch_mdb_delta(self, cfg: TableSyncConfig, since_ts: datetime) -> list[dict]:
        def _op():
            conn = self._mdb_connect(readonly=True)
            try:
                cur = conn.cursor()
                sql = (
                    f"SELECT {', '.join(f'[{c}]' for c in cfg.columns)} "
                    f"FROM [{cfg.table_name}] WHERE [{cfg.updated_at_col}] > ? "
                    f"ORDER BY [{cfg.updated_at_col}] ASC"
                )
                cur.execute(sql, (since_ts.replace(tzinfo=None),))
                cols = [d[0] for d in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
            finally:
                conn.close()

        return self._run_retry(_op, f"mdb_read_{cfg.table_name}") or []

    def _fetch_all_mdb_rows(self, cfg: TableSyncConfig) -> tuple[list[str], list[dict]]:
        def _op():
            conn = self._mdb_connect(readonly=True)
            try:
                cur = conn.cursor()
                sql = f"SELECT * FROM [{cfg.table_name}]"
                # Prefer explicit subset columns only when they are known-good.
                if cfg.columns:
                    try:
                        sql_subset = f"SELECT {', '.join(f'[{c}]' for c in cfg.columns)} FROM [{cfg.table_name}]"
                        cur.execute(sql_subset)
                    except pyodbc.Error:
                        cur = conn.cursor()
                        cur.execute(sql)
                else:
                    cur.execute(sql)
                cols = [d[0] for d in cur.description]
                return cols, [dict(zip(cols, row)) for row in cur.fetchall()]
            finally:
                conn.close()

        return self._run_retry(_op, f"mdb_full_read_{cfg.table_name}") or ([], [])

    def _fetch_pg_delta(self, cfg: TableSyncConfig, since_ts: datetime) -> list[dict]:
        table = self._get_pg_table(cfg.table_name)
        with self.engine.begin() as conn:
            rows = conn.execute(
                select(*[table.c[c] for c in cfg.columns])
                .where(table.c[cfg.updated_at_col] > since_ts)
                .order_by(table.c[cfg.updated_at_col].asc())
            ).mappings().all()
        return [dict(r) for r in rows]

    def _upsert_pg(self, cfg: TableSyncConfig, row: dict) -> None:
        table = self._get_pg_table(cfg.table_name)
        pk = cfg.primary_key
        up = cfg.updated_at_col
        incoming_ts = as_utc(row.get(up)) or datetime(1970, 1, 1, tzinfo=timezone.utc)
        with self.engine.begin() as conn:
            existing = conn.execute(select(table.c[up]).where(table.c[pk] == row.get(pk))).first()
            if not existing:
                conn.execute(insert(table).values({c: row.get(c) for c in cfg.columns}))
                return
            current_ts = as_utc(existing[0]) or datetime(1970, 1, 1, tzinfo=timezone.utc)
            if incoming_ts >= current_ts:
                conn.execute(
                    update(table).where(table.c[pk] == row.get(pk)).values({c: row.get(c) for c in cfg.columns if c != pk})
                )

    def _upsert_mdb(self, cfg: TableSyncConfig, row: dict) -> None:
        def _op():
            conn = self._mdb_connect(readonly=False)
            try:
                cur = conn.cursor()
                pk = cfg.primary_key
                up = cfg.updated_at_col
                cur.execute(f"SELECT [{up}] FROM [{cfg.table_name}] WHERE [{pk}] = ?", (row.get(pk),))
                existing = cur.fetchone()
                incoming_ts = as_utc(row.get(up)) or datetime(1970, 1, 1, tzinfo=timezone.utc)
                if existing:
                    current_ts = as_utc(existing[0]) or datetime(1970, 1, 1, tzinfo=timezone.utc)
                    if incoming_ts < current_ts:
                        conn.rollback()
                        return
                    cols = [c for c in cfg.columns if c != pk]
                    set_clause = ", ".join(f"[{c}] = ?" for c in cols)
                    values = [row.get(c) for c in cols] + [row.get(pk)]
                    cur.execute(f"UPDATE [{cfg.table_name}] SET {set_clause} WHERE [{pk}] = ?", values)
                else:
                    cols = cfg.columns
                    placeholders = ", ".join("?" for _ in cols)
                    values = [row.get(c) for c in cols]
                    cur.execute(
                        f"INSERT INTO [{cfg.table_name}] ({', '.join(f'[{c}]' for c in cols)}) VALUES ({placeholders})",
                        values,
                    )
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

        self._run_retry(_op, f"mdb_write_{cfg.table_name}")

    def sync_table_once(self, cfg: TableSyncConfig) -> None:
        if cfg.mode == "full_refresh":
            self.sync_table_full_refresh(cfg)
            return
        if not str(cfg.updated_at_col or "").strip():
            logger.warning(
                "delta mode skipped for %s (missing updated_at_col); using full_refresh fallback",
                cfg.table_name,
            )
            self.sync_table_full_refresh(cfg)
            return
        m2p_key = self._sync_key("mdb_to_pg", cfg.table_name)
        p2m_key = self._sync_key("pg_to_mdb", cfg.table_name)

        m2p_watermark = self._get_last_sync(m2p_key)
        m2p_now = utcnow()
        try:
            for row in self._fetch_mdb_delta(cfg, m2p_watermark):
                self._upsert_pg(cfg, row)
        except pyodbc.Error as exc:
            msg = str(exc or "").lower()
            if "too few parameters" in msg:
                logger.warning(
                    "delta query failed for %s (likely schema mismatch); using full_refresh fallback",
                    cfg.table_name,
                )
                self.sync_table_full_refresh(cfg)
                return
            raise
        self._set_last_sync(m2p_key, m2p_now)

        if cfg.bidirectional:
            p2m_watermark = self._get_last_sync(p2m_key)
            p2m_now = utcnow()
            for row in self._fetch_pg_delta(cfg, p2m_watermark):
                self._upsert_mdb(cfg, row)
            self._set_last_sync(p2m_key, p2m_now)

    def sync_table_full_refresh(self, cfg: TableSyncConfig) -> None:
        """
        One-way full refresh for tables without reliable updated_at in MDB.
        """
        columns, rows = self._fetch_all_mdb_rows(cfg)
        if not columns:
            logger.warning("full refresh skipped for %s (no columns detected)", cfg.table_name)
            return
        self._ensure_pg_table_exists(cfg, columns, rows)
        table = self._get_pg_table(cfg.table_name)
        with self.engine.begin() as conn:
            conn.execute(table.delete())
            if rows:
                payload = [{c: r.get(c) for c in columns} for r in rows]
                conn.execute(insert(table), payload)
        self._set_last_sync(self._sync_key("mdb_to_pg_full", cfg.table_name), utcnow())

    @staticmethod
    def _infer_pg_column_type(values: list[Any]):
        detected = set()
        for v in values:
            if v is None:
                continue
            if isinstance(v, bool):
                detected.add("bool")
            elif isinstance(v, int):
                detected.add("int")
            elif isinstance(v, float):
                detected.add("float")
            elif isinstance(v, Decimal):
                detected.add("numeric")
            elif isinstance(v, datetime):
                detected.add("datetime")
            elif isinstance(v, date):
                detected.add("date")
            elif isinstance(v, dt_time):
                detected.add("time")
            elif isinstance(v, (bytes, bytearray, memoryview)):
                detected.add("bytes")
            else:
                detected.add("text")
        if not detected:
            return String()
        if "text" in detected:
            return String()
        if "bytes" in detected and len(detected) == 1:
            return LargeBinary()
        if "datetime" in detected:
            return DateTime()
        if "date" in detected and "time" not in detected:
            return Date()
        if "time" in detected and "date" not in detected:
            return DateTime()
        if "float" in detected:
            return Float()
        if "numeric" in detected:
            return Numeric()
        if "int" in detected and "bool" not in detected:
            return Integer()
        if "bool" in detected and len(detected) == 1:
            return Boolean()
        return String()

    def _ensure_pg_table_exists(self, cfg: TableSyncConfig, columns: list[str], rows: list[dict]) -> None:
        if inspect(self.engine).has_table(cfg.table_name):
            return
        sample_limit = 200
        col_samples: dict[str, list[Any]] = {c: [] for c in columns}
        for row in (rows or [])[:sample_limit]:
            for c in columns:
                col_samples[c].append(row.get(c))
        md = MetaData()
        table_cols = []
        for col_name in columns:
            is_pk = bool(cfg.primary_key and col_name == cfg.primary_key)
            table_cols.append(
                Column(
                    col_name,
                    self._infer_pg_column_type(col_samples.get(col_name) or []),
                    primary_key=is_pk,
                )
            )
        Table(cfg.table_name, md, *table_cols)
        md.create_all(self.engine)
        self._pg_table_cache.pop(cfg.table_name, None)

    def sync_once(self) -> None:
        n = len(self.table_configs)
        self._progress("Refreshing MDB path / local cache…")
        self._refresh_local_cache()
        path_hint = self._cached_mdb_path or self._source_mdb_path or "(unknown)"
        self._progress(f"MDB path ready: {path_hint}; syncing {n} table(s)")
        for i, cfg in enumerate(self.table_configs, start=1):
            self._progress(f"[{i}/{n}] {cfg.table_name} ({cfg.mode})…")
            self.sync_table_once(cfg)
        self._progress("sync_once finished")

    def run_forever(self, interval_seconds: int = 120) -> None:
        while not self.stop_event.is_set():
            started = time.time()
            try:
                self.sync_once()
                logger.info("sync cycle complete")
            except Exception as exc:
                logger.exception("sync cycle failed: %s", exc)
            elapsed = time.time() - started
            wait_for = max(1, int(interval_seconds - elapsed))
            self.stop_event.wait(wait_for)

    def stop(self) -> None:
        self.stop_event.set()

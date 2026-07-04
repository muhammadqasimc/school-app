import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def q(name: str) -> str:
    return '"' + str(name).replace('"', '""') + '"'


def main():
    load_dotenv()
    pg_url = os.environ.get("POSTGRES_DATABASE_URL", "").strip()
    if not pg_url:
        raise RuntimeError("POSTGRES_DATABASE_URL is required")

    engine = create_engine(pg_url, future=True)
    with engine.begin() as conn:
        tables = conn.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='public' AND table_type='BASE TABLE'
                ORDER BY table_name
                """
            )
        ).fetchall()

        created = 0
        skipped = 0
        for (table_name,) in tables:
            orig = str(table_name)
            lower_name = orig.lower()
            # Only create alias views where names differ by case or punctuation-style casing.
            if orig == lower_name:
                skipped += 1
                continue

            cols = conn.execute(
                text(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema='public' AND table_name=:t
                    ORDER BY ordinal_position
                    """
                ),
                {"t": orig},
            ).fetchall()
            if not cols:
                skipped += 1
                continue

            select_cols = []
            for (col_name,) in cols:
                c = str(col_name)
                select_cols.append(f"{q(c)} AS {q(c.lower())}")
            select_list = ", ".join(select_cols)

            conn.execute(text(f"DROP VIEW IF EXISTS {q(lower_name)} CASCADE"))
            conn.execute(text(f"CREATE VIEW {q(lower_name)} AS SELECT {select_list} FROM {q(orig)}"))
            created += 1

    print(f"compat views created: {created}, skipped: {skipped}")


if __name__ == "__main__":
    main()

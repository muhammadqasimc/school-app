import json
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def main():
    load_dotenv()
    engine = create_engine(os.getenv("POSTGRES_DATABASE_URL"), future=True)
    tables = [
        "user",
        "user_learner",
        "Learner_Info",
        "Parent_Info",
        "Parent_Child",
        "ReportMarks",
    ]
    out = {}
    with engine.begin() as conn:
        for table in tables:
            out[table] = conn.execute(text(f'SELECT COUNT(*) FROM "{table}"')).scalar() or 0
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

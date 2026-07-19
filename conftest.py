"""
Repo-level conftest: ensures the project root is on sys.path so that
`import app` and `import management_report_handlers` work when running
`pytest` directly (not just via `python -m pytest`).
"""
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

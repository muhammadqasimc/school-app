"""Verify that legacy Model.query.get() and Model.query.get_or_404() calls
have been replaced with modern db.session.get(Model, id) and
db.get_or_404(Model, id) patterns.

Regression test for the SQLAlchemy 2.0 deprecation-warning fix.
"""

import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Files that are in scope for the replacement
TARGET_FILES = [
    "app.py",
    "admin_routes.py",
    "inventory_routes.py",
]


def _all_py_files():
    for f in TARGET_FILES:
        yield PROJECT_ROOT / f


def _find_query_get_calls(tree: ast.AST) -> list[tuple[int, int, str]]:
    """Return (lineno, col_offset, snippet) for every .query.get( call found."""
    hits = []

    class QueryGetVisitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call):
            # Pattern: <something>.query.get(...)
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and isinstance(node.func.value, ast.Attribute)
                and node.func.value.attr == "query"
            ):
                # Reconstruct a rough snippet
                snippet = f"...{node.func.value.value.id if isinstance(node.func.value.value, ast.Name) else 'expr'}.query.get(...)"
                hits.append((node.lineno, node.col_offset, snippet))
            # Pattern: <something>.query.get_or_404(...)
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "get_or_404"
                and isinstance(node.func.value, ast.Attribute)
                and node.func.value.attr == "query"
            ):
                snippet = f"...{node.func.value.value.id if isinstance(node.func.value.value, ast.Name) else 'expr'}.query.get_or_404(...)"
                hits.append((node.lineno, node.col_offset, snippet))
            self.generic_visit(node)

    QueryGetVisitor().visit(tree)
    return hits


def test_no_legacy_query_get_calls():
    """Fail if any .query.get( or .query.get_or_404( calls remain in target files."""
    all_hits = []
    for path in _all_py_files():
        if not path.is_file():
            continue
        source = path.read_text()
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {path.name}: {e}")
        hits = _find_query_get_calls(tree)
        for lineno, col, snippet in hits:
            all_hits.append(f"  {path.name}:{lineno}:{col}: {snippet}")

    if all_hits:
        msg = (
            f"Found {len(all_hits)} legacy .query.get() or .query.get_or_404() call(s):\n"
            + "\n".join(all_hits)
            + "\n\nReplace with db.session.get(Model, id) or db.get_or_404(Model, id)."
        )
        pytest.fail(msg)


# Import pytest only when the module is actually run by pytest
import pytest

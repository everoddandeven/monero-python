#!/usr/bin/env python3
"""Checks the Python code of the docs against the stubs of src/monero with pyright: the blocks of the pages of docs/mkdocs/docs and the
sample code of README.md, not the pieces of the code of the tests that the pages of the tests show. A call that the library does not
have, an argument of the wrong type, a property that can not be set or an import that is missing fails it, as it would fail who runs
the example. The module is not needed, the stubs say what it has.

The blocks of a page are checked as one file, in their order: a block uses what the ones before it made. An error is reported at its
line of the page.

    python3 bin/check_examples.py

CI runs it in .github/workflows/docs.yml, with the pyright of docs/mkdocs/requirements.in.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional

ROOT: Path = Path(__file__).resolve().parent.parent
DOCS: Path = ROOT / "docs" / "mkdocs" / "docs" / "en"
# the pages of the tests show pieces of the code of tests/, which the type checker of the repository checks where they are
PAGES: list[Path] = sorted(page for page in DOCS.rglob("*.md") if not page.is_relative_to(DOCS / "tests")) + [ROOT / "README.md"]
OPEN: re.Pattern[str] = re.compile(r"^(?P<indent>[ \t]*)```python[ \t]*$")


def read_code(page: Path) -> tuple[list[str], list[Optional[int]]]:
    """The code of the blocks of a page, and the line of the page of each of its lines (None for the lines between the blocks)."""
    code: list[str] = []
    lines: list[Optional[int]] = []
    indent: Optional[str] = None
    for number, line in enumerate(page.read_text(encoding="utf-8").splitlines(), start=1):
        if indent is None:
            match = OPEN.match(line)
            if match:
                indent = match.group("indent")
                if code:
                    code.append("")
                    lines.append(None)
        elif line.strip() == "```" and line.startswith(indent):
            indent = None
        else:
            # a block in a list is indented as the list: its code is not
            code.append(line[len(indent):] if line.startswith(indent) else line.lstrip())
            lines.append(number)
    return code, lines


def main() -> int:
    with tempfile.TemporaryDirectory() as folder:
        sources: dict[str, tuple[Path, list[Optional[int]]]] = {}
        for index, page in enumerate(PAGES):
            code, lines = read_code(page)
            if code:
                source: Path = Path(folder) / f"page_{index}.py"
                source.write_text("\n".join(code) + "\n", encoding="utf-8")
                sources[str(source.resolve())] = (page, lines)
        config: dict[str, Any] = {
            "stubPath": str(ROOT / "src"),
            "typeCheckingMode": "standard",
            "pythonVersion": "3.10",
            # the module is compiled, the stubs are all there is of it
            "reportMissingModuleSource": "none",
        }
        (Path(folder) / "pyrightconfig.json").write_text(json.dumps(config), encoding="utf-8")
        run = subprocess.run([sys.executable, "-m", "pyright", "--outputjson"], cwd=folder, capture_output=True, text=True)
        try:
            report: dict[str, Any] = json.loads(run.stdout)
        except json.JSONDecodeError:
            print(run.stdout + run.stderr, file=sys.stderr)
            return 2

    errors: int = 0
    for diagnostic in report.get("generalDiagnostics", []):
        page, lines = sources[str(Path(diagnostic["file"]).resolve())]
        start: dict[str, int] = diagnostic["range"]["start"]
        line: Optional[int] = lines[start["line"]] if start["line"] < len(lines) else None
        where: str = f"{page.relative_to(ROOT)}:{line}:{start['character'] + 1}"
        print(f"{where}: {diagnostic['severity']}: {diagnostic['message']}")
        errors += diagnostic["severity"] == "error"
    print(f"{len(sources)} pages checked, {errors} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

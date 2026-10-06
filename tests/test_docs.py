"""Every Python example in the README and docs must run and show true output.

The examples themselves run in CI's docs job, which has the transport
libraries installed. The checks here keep the docs complete and in step with
the code.
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import List, Set

import pytest

import jsonrpcclient
from jsonrpcclient import id_generators

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "docs"
FILES = [ROOT / "README.md", *sorted(DOCS.rglob("*.md"))]


@pytest.mark.parametrize("path", FILES, ids=lambda path: str(path.relative_to(ROOT)))
def test_doc_examples(path: Path) -> None:
    # A fresh interpreter per file, so request ids start at 1 like they do
    # for a reader.
    result = subprocess.run(
        [sys.executable, str(ROOT / "tests" / "doc_examples.py"), str(path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def python_block(text: str, after: str) -> str:
    start = text.index("```python\n", text.index(after)) + len("```python\n")
    return text[start : text.index("```", start)]


def test_readme_quickstart_is_the_tested_example() -> None:
    """check_examples.py runs quickstart.py, so the README must match it."""
    readme = (ROOT / "README.md").read_text()
    example = (DOCS / "examples" / "quickstart.py").read_text()
    assert python_block(readme, "## Quickstart") == example


def test_every_included_example_is_checked() -> None:
    included: Set[str] = set()
    for path in DOCS.rglob("*.md"):
        included.update(
            re.findall(r'--8<-- "docs/examples/(\w+\.py)"', path.read_text())
        )
    checker = (DOCS / "examples" / "check_examples.py").read_text()
    checked = set(re.findall(r'"(\w+\.py)"', checker))
    assert included
    assert included <= checked


def public_names() -> List[str]:
    generators = [
        f"id_generators.{name}"
        for name in dir(id_generators)
        if not name.startswith("_")
        and callable(getattr(id_generators, name))
        and getattr(id_generators, name).__module__ == id_generators.__name__
    ]
    return [*jsonrpcclient.__all__, "__version__", *generators, "utils.compose"]


@pytest.mark.parametrize("name", public_names())
def test_reference_documents_every_public_name(name: str) -> None:
    reference = (DOCS / "reference.md").read_text()
    if name.startswith("id_generators."):
        assert "::: jsonrpcclient.id_generators" in reference
        assert f"        - {name.split('.')[1]}\n" in reference
    else:
        assert f"::: jsonrpcclient.{name}\n" in reference


def test_python_versions_badge_matches_classifiers() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text()
    versions = re.findall(r'"Programming Language :: Python :: (3\.\d+)"', pyproject)
    readme = (ROOT / "README.md").read_text()
    badge = re.search(r"img\.shields\.io/badge/python-([^-]+)-blue", readme)
    assert badge
    assert badge.group(1).split("%20%7C%20") == versions

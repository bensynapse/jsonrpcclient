# Contributing

Bug reports and pull requests are welcome. For a bigger change, open an issue
first so we can agree on the approach.

## Setting up

```sh
python -m venv .venv
. .venv/bin/activate
pip install -e . -r requirements/test.txt -r requirements/lint.txt
```

## Checks

CI runs these, and a pull request needs all of them to pass:

```sh
pytest --cov          # tests, 100% line and branch coverage required
ruff check .
ruff format --check .
mypy
pyright
```

To run the tests on every Python version you have installed, use `tox`.

If you change the docs, build them with
`pip install -r requirements/docs.txt && mkdocs serve`. The API reference is
generated from the docstrings, so document a new public function there.

Every Python example in the README and the docs runs in CI, so keep the shown
output accurate:

- `tests/doc_examples.py FILE.md` runs the code blocks in one page. `>>>`
  blocks are doctests, and a block followed by a `text title="Output"` block
  must print exactly that. HTML comments before a block can mark it as needing
  a package (`<!-- requires: requests -->`), a test server on port 8000
  (`<!-- server -->`) or a newer Python (`<!-- min-python: 3.10 -->`). The
  docstring at the top of that file lists them all.
- `docs/examples/check_examples.py` runs the transport examples in
  `docs/examples/` against test servers. A new example file needs a line in
  its `CASES`.

To run all of them, install the example libraries first:

```sh
pip install -r requirements/examples.txt
for f in README.md $(find docs -name '*.md' | sort); do
  python tests/doc_examples.py "$f"
done
python docs/examples/check_examples.py
```

## Pull requests

- Keep each pull request to one change, with a test for it.
- Add a line to CHANGELOG.md if users will notice the change.
- The library has no dependencies and supports Python 3.8 and later. Please
  keep it that way.

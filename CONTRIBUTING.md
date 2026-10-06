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
`pip install -r requirements/docs.txt && mkdocs serve`. Every Python example in
the docs is run by `tests/test_docs.py`, so keep the shown output accurate.

## Pull requests

- Keep each pull request to one change, with a test for it.
- Add a line to CHANGELOG.md if users will notice the change.
- The library has no dependencies and supports Python 3.8 and later. Please
  keep it that way.

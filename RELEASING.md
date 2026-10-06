# Releasing

Releases are published by `.github/workflows/release.yml` when a tag like
`v4.0.4` is pushed. It builds and checks the sdist and wheel, and attests
their build provenance. Then it uploads them to PyPI with Trusted Publishing
and creates the GitHub release from the CHANGELOG entry. Nobody needs a PyPI
token.

## One-time setup on PyPI

This needs an Owner or Maintainer role on the `jsonrpcclient` project on PyPI.

1. Open https://pypi.org/manage/project/jsonrpcclient/settings/publishing/
2. Under "Add a new publisher", choose **GitHub** and fill in exactly:

   | Field | Value |
   |---|---|
   | Owner | `bensynapse` |
   | Repository name | `jsonrpcclient` |
   | Workflow name | `release.yml` |
   | Environment name | `pypi` |

3. Click "Add".

The `pypi` environment already exists in the GitHub repo settings. It only
accepts deployments from tags matching `v*`. To require a manual approval
before each upload, add yourself under "Required reviewers" in
Settings → Environments → pypi.

## Each release

1. Merge a pull request that gets the version ready:
   - `__version__` in `jsonrpcclient/__init__.py` is the new version.
   - Its CHANGELOG.md heading has the release date instead of "not released
     yet": `## 4.1.0 (2026-10-20)`.
   - The `unreleased` and `pypi_version` lines under `extra` in mkdocs.yml are
     deleted. They show the "not on PyPI yet" banner on every docs page.
     Merging this redeploys the docs, so merge it just before you tag.
   - The paragraph under "Install" in README.md that says the version isn't
     released yet is deleted. The README becomes the PyPI page.

   The release workflow checks all of this. It stops if the version and tag
   don't match or the CHANGELOG heading has no date. It also stops if
   mkdocs.yml or README.md still say the version isn't released.

   4.0.4 and 4.1.0 are both marked "not released yet". 4.0.4 can still be
   tagged on its own at `6a1569a`, before 4.1.0. A tag runs the workflow
   from the tagged commit, so that tag gets the older checks. It also
   publishes that commit's undated `## 4.0.4` CHANGELOG text as the notes. If you skip it, move its
   CHANGELOG entries into the 4.1.0 section. Then change "New in 4.0.4" in the
   docs to "New in 4.1.0" (`grep -rn "4\.0\.4" docs` finds them).
2. Tag the merge commit on main and push the tag:

   ```sh
   git fetch origin
   git tag -a v4.0.4 <commit> -m "4.0.4"
   git push origin v4.0.4
   ```

3. Watch the "Release" workflow in the Actions tab.
4. Check the result:

   ```sh
   curl -s https://pypi.org/pypi/jsonrpcclient/json | python3 -c \
     "import sys, json; i = json.load(sys.stdin)['info']; print(i['version'], i['project_urls'])"
   ```

## If the upload fails

- `invalid-publisher`: the PyPI publisher settings above don't match. Check
  every field, including the `.yml` in the workflow name.
- `File already exists`: that version is already on PyPI, and PyPI never
  allows the same file twice. Bump the version and tag again.

A failed run can be re-run from the Actions tab once the cause is fixed. If the
tag itself was wrong, delete it locally and on GitHub
(`git push origin :refs/tags/v4.0.4`) before tagging again. Never delete a tag
whose version reached PyPI.

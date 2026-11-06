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
     The docs deploy when you push the tag, so merging this changes nothing
     users see until then.
   - The paragraph under "Install" in README.md that says the version isn't
     released yet is deleted. The README becomes the PyPI page.

   The release workflow checks all of this. It stops if the version and tag
   don't match or the CHANGELOG heading has no date. It also stops if
   mkdocs.yml or README.md still say the version isn't released.

   A patch for an older line goes on a `release/` branch, as 4.0.4 did
   (`release/4.0.x`, tagged before 4.1.0).
2. Wait until CI has passed on the merge commit. Then tag it and push the tag.
   The release workflow refuses a commit that isn't on main or a `release/`
   branch, and one that "CI OK" hasn't passed on:

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

## Docs

The docs site deploys from `.github/workflows/docs.yml` when a release tag is
pushed, so it always describes the version on PyPI. To publish a docs-only fix
between releases, run the Docs workflow by hand on main. If main is ahead of
PyPI by then, set `unreleased` in mkdocs.yml first, so a banner says so.

# Release Process Guide for PyPI

This document outlines the steps needed to release a new version to PyPI.

## Pre-release Checklist

1. **Update version number** in:

   - `pyproject.toml`
   - `scrape_cli/__init__.py`

2. **Update the CHANGELOG**:

   - Add a new section for the upcoming version, with the release date.
   - Document all significant changes.

3. **Update `LOG.md`** with a one-line entry for the release.

4. **Run the test suite** with the working venv:

   ```bash
   source .venv/bin/activate
   pytest tests/
   ```

   All tests must pass.

## Build Process

1. **Activate the working virtual environment** (`.venv`, uv-managed):

   ```bash
   source .venv/bin/activate
   ```

2. **Make sure `build` and `twine` are installed** in the venv:

   ```bash
   uv pip install build twine
   ```

3. **Clean previous builds**:

   ```bash
   rm -rf build/ dist/ scrape_cli.egg-info
   ```

4. **Build the distribution packages**:

   ```bash
   python3 -m build
   ```

5. **Verify the built distributions**:

   ```bash
   twine check dist/*
   ```

6. **Local install smoke test** (optional, recommended).
   Always install inside an active venv, otherwise PEP 668 may block the install:

   ```bash
   pip install --force-reinstall dist/scrape_cli-<version>-py3-none-any.whl
   scrape --version
   ```

## Final Release

1. **Commit all release-related changes** (`pyproject.toml`, `__init__.py`, `CHANGELOG.md`, `LOG.md`, code, docs). Stage files by name, so that unrelated work in the tree stays out, and check the staged list:

   ```bash
   git add pyproject.toml scrape_cli/ tests/ CHANGELOG.md LOG.md README.md
   git diff --cached --stat
   git commit -m "v<version>: <short description>"
   git push origin master
   ```

2. **Tag the release** (annotated tag, after the commit is pushed):

   ```bash
   git tag -a v<version> -m "Release <version>"
   git push origin v<version>
   ```

3. **Upload the distribution packages to PyPI**:

   ```bash
   twine upload dist/*
   ```

   PyPI does not allow re-uploading the same version. If you need to fix
   anything after this point, bump to the next patch version and start over.

4. **Verify Installation**:

   ```bash
   uv tool install --force scrape-cli
   # or
   pipx install --force scrape-cli
   scrape --version
   ```

## Post-release Checklist

1. **Manually create the GitHub release**:

   - Open https://github.com/aborruso/scrape-cli/releases
   - Click "Draft a new release"
   - Select the tag you just pushed (e.g. `v1.3.1`)
   - Title: `v<version>` (or copy from CHANGELOG)
   - Body: copy the matching CHANGELOG section
   - Publish

2. **Update README badges and docs** if needed.
   If you change `README.md` after the PyPI upload, you cannot re-upload the
   same version: bump the patch number, rebuild, and upload the new version.

## Rollback

PyPI does not support deletion of a published version (and `twine delete`
does not exist). If a release is broken:

1. Yank the version on PyPI via the web UI (this hides it from new
   installs but keeps existing installs working).
2. Bump the patch version, fix the issue, and release the next version.

If you need to roll back the git tag locally:

```bash
git tag -d v<version>
git push origin :refs/tags/v<version>
```

## Automation

A simple end-to-end script (run from the project root, with `.venv`
activated):

```bash
#!/bin/bash
set -e

VERSION="$1"
[ -z "$VERSION" ] && { echo "usage: $0 <version>"; exit 1; }

source .venv/bin/activate
pytest tests/
rm -rf build/ dist/ scrape_cli.egg-info
python3 -m build
twine check dist/*

git add pyproject.toml scrape_cli/ tests/ CHANGELOG.md LOG.md README.md
git commit -m "v${VERSION}: release"
git push origin master

git tag -a "v${VERSION}" -m "Release ${VERSION}"
git push origin "v${VERSION}"

twine upload dist/*

# Then create the GitHub release manually from the pushed tag.
```

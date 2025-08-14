# Release Process Guide for PyPI

This document outlines the steps needed to release a new version to PyPI.

## Pre-release Checklist

1. **Update version number** in the following files:

   - `pyproject.toml`
   - `scrape_cli/__init__.py`

2. **Update the CHANGELOG**:

   - Add a new section for the upcoming version.
   - Document all significant changes.
   - Include the release date.

3. **Install Dependencies**:

   - Ensure all dependencies are installed properly:
     ```
     pip install -r requirements.txt
     ```

## Build Process

1. **Activate the virtual environment** (if not already activated):

   ```
   source venv/bin/activate  # Linux/MacOS
   ```

2. **Clean previous builds**:

   ```
   rm -rf build/ dist/ *.egg-info
   ```

3. **Build the distribution packages**:

   ```
   python3 -m build
   ```

4. **Verify the built distributions**:

   ```
   twine check dist/*
   ```

5. **Local Installation Test** (optional but recommended):

   - Install the built package locally to verify it:
     ```
     pip install dist/<package-name>.tar.gz
     ```

## Final Release

1. **Upload the distribution packages to PyPI**:

   ```
   twine upload dist/*
   ```

2. **Verify Installation**:

   ```
   pip install <package-name>
   ```

## Post-release Checklist

1. **Tag the Release in Git**:

   ```
   git tag -a <version> -m "Release <version>"
   git push origin <version>
   ```

2. **Manually create the GitHub release**:

   - Go to the releases page on GitHub: https://github.com/aborruso/scrape-cli/releases
   - Click "Draft a new release".
   - Select the tag you just created (e.g. v1.1.9).
   - Enter the title and release notes (you can copy from the CHANGELOG).
   - Publish the release.

3. **Update Documentation**:

   - Update relevant parts of the documentation.
   - Post announcements in channels such as Slack or mailing lists (if applicable).
   - Update the version badge in the README if present (e.g. PyPI badge or version badge).

## Rollback Process (Optional)

1. **Remove the release from PyPI** if issues are found:

   ```
   twine delete <package-name> <version>
   ```

2. **Revert the Git Tag**:

   ```
   git tag -d <version>
   git push origin :refs/tags/<version>
   ```

## Automate the Release Process (Optional)

To save time and reduce the chance of manual errors, consider using a script like the one below for automation:

```bash
#!/bin/bash
set -e

# Activate the virtual environment
source venv/bin/activate

# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build the package
python3 -m build

# Check the build
twine check dist/*

# Upload to PyPI
twine upload dist/*

# Tag the release
git tag -a $1 -m "Release $1"
git push origin $1

# Crea manualmente la release su GitHub dopo il push del tag.
```

This script simplifies many of the steps and ensures that all commands run in sequence.

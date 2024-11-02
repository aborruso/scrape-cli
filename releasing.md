# Release Process Guide for PyPI

This document outlines the steps needed to release a new version to PyPI.

## Pre-release Checklist

1. Activate virtual environment:

```
python -m venv venv
source venv/bin/activate  # Linux/MacOS
```

2. Update version number in:
   - `setup.py`
   - `scrape_cli/__init__.py`

3. Update CHANGELOG.md
   - Add new version section
   - Document all significant changes
   - Date the release

## Build Process

1. Clean previous builds:

```
rm -rf build/ dist/ *.egg-info
```

2. Build the distribution packages:

```
python3 -m build
```

3. Check the built distributions:

```
twine check dist/*
```

## Final Release

1. Upload the distribution packages to PyPI:

```
twine upload dist/*
```

2. Verify installation:

```
pip install <package-name>
```

## Post-release Checklist

1. Create a new GitHub release

```
git tag -a <version> -m "Release <version>"
git push origin <version>
```

2. Create a GitHub release (if using GitHub)
  - Navigate to releases page
  - Create new release using the tag
  - Add release notes
  - Announce release (if applicable)

3. Update documentation website
  - Post announcements in relevant channels

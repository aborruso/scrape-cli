# Release Guide for scrape-cli

This guide details the steps to release a new version of scrape-cli.

## 1. Update Version Numbers

Update version in both files:

1. In `scrape_cli/__init__.py`:
```python
__version__ = "X.Y.Z"  # update version number
```

2. In `setup.py`:
```python
setup(
    name="scrape-cli",
    version="X.Y.Z",  # update version number
    // ...
)
```

## 2. Update CHANGELOG.md

Add new entry at the top of `CHANGELOG.md`:

```markdown
# YYYY-MM-DD

- Add your changes here
```

## 3. Commit and Push Changes

```bash
git add .
git commit -m "feat: description of changes"
git push origin master
```

## 4. Create and Push Tag

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

## 5. Create GitHub Release

```bash
gh release create vX.Y.Z --title "vX.Y.Z" --notes "## What's Changed

### Features
* Description of new features
  - Point 1
  - Point 2
  - etc."
```

## 6. Publish to PyPI

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Create package
python3 -m build

# Check package
twine check dist/*

# Upload to PyPI (will ask for credentials)
twine upload dist/*
```

## 7. Create Linux Binary (Optional)

Se vuoi distribuire un binario precompilato per Linux:

```bash
# Installa PyInstaller se non già presente
pip install pyinstaller

# Crea il binario
pyinstaller --onefile --name scrape scrape_cli/main.py

# Il binario sarà in dist/scrape
# Testalo
./dist/scrape --version
```

### Upload Binary to GitHub Release

```bash
# Aggiungi il binario alla release GitHub esistente
gh release upload vX.Y.Z dist/scrape --clobber
```

Oppure includi il binario durante la creazione della release al punto 5:

```bash
gh release create vX.Y.Z dist/scrape --title "vX.Y.Z" --notes "## What's Changed

### Features
* Description of new features
  - Point 1
  - Point 2
  - etc.

### Downloads
- \`scrape\` - Linux x64 binary"
```

## 8. Verify Installation

```bash
# Verify package is available and installable
pip install --no-cache-dir scrape-cli==X.Y.Z

# Verify version
scrape --version
```

## Important Notes

- Replace `X.Y.Z` with the new version number
- Ensure PyPI credentials are configured
- GitHub CLI (`gh`) must be installed and configured
- Keep `CHANGELOG.md` up to date
- Follow semantic commit conventions (feat:, fix:, etc.)

## Requirements

- GitHub CLI (`gh`)
- `build`
- `twine`
- PyPI credentials
- Git configured
- `pyinstaller` (per creare il binario Linux precompilato)

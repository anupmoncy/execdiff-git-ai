#!/bin/bash

# Deprecate checkod-ai and push to git and PyPI

set -e

# Stage all changes
git add .

# Commit changes
git commit -m "Deprecate checkod-ai and migrate to execdiff-git-ai"

# Ensure remote is set (replace <your-repo-url> if needed)
if ! git remote | grep -q origin; then
    git remote add origin <your-repo-url>
fi

# Push to main branch
git push origin main

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build

# Upload to PyPI (requires twine and PyPI credentials)
twine upload dist/*

#!/bin/bash

# List of files added/modified (one per line)
# (Add file paths here as needed)

ruff format
ruff check --fix > out.txt

# For each modified file, commit
# Assuming files are listed in a variable or from git status
# For simplicity, example commits (replace with actual files)
# git add newfile.py
# git commit -m 'summary of edits for newfile.py'
# git commit -m 'summary of edits for modifiedfile.py'

uv run pytest -v >> out.txt

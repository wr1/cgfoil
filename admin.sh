#!/bin/bash

# Files added/modified:
# src/cgfoil/core/generate_mesh.py
# src/cgfoil/utils/summary.py
# admin.sh

ruff format
ruff check --fix > out.txt

git add src/cgfoil/core/generate_mesh.py
git commit src/cgfoil/core/generate_mesh.py -m 'Add post-meshing filtering to remove degenerate near-collinear triangles in generate_mesh.py'

git add src/cgfoil/utils/summary.py
git commit src/cgfoil/utils/summary.py -m 'Update summary.py to compute areas correctly'

git add admin.sh
git commit admin.sh -m 'Add admin.sh script for formatting, checking, and committing changes'

uv run pytest -v >> out.txt

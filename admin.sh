#!/bin/bash

ruff format
ruff check --fix > out.txt

git add src/cgfoil/models/thickness.py
git commit -m 'refactor thickness model into separate file'

git add src/cgfoil/models/ply.py
git commit -m 'refactor ply model into separate file'

git add src/cgfoil/models/web.py
git commit -m 'refactor web model into separate file'

git add src/cgfoil/models/skin.py
git commit -m 'refactor skin model into separate file'

git add src/cgfoil/models/airfoil_mesh.py
git commit -m 'refactor airfoil_mesh model into separate file'

git add src/cgfoil/models/mesh_result.py
git commit -m 'refactor mesh_result model into separate file'

git add src/cgfoil/models/__init__.py
git commit -m 'update models __init__.py'

git add src/cgfoil/core/generate_mesh.py
git commit -m 'split generate_mesh into separate file'

git add src/cgfoil/core/plot_mesh.py
git commit -m 'split plot_mesh into separate file'

git add src/cgfoil/core/run_cgfoil.py
git commit -m 'split run_cgfoil into separate file'

uv run pytest -v >> out.txt
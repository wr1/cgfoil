#!/bin/bash

# List of files to commit
files=(
  "pyproject.toml"
  "src/cgfoil/__init__.py"
  "src/cgfoil/models.py"
  "src/cgfoil/cli/summary.py"
  "src/cgfoil/cli/full.py"
  "src/cgfoil/cli/mesh.py"
  "src/cgfoil/cli/__init__.py"
  "src/cgfoil/cli/plot.py"
  "src/cgfoil/cli/run.py"
  "src/cgfoil/cli/export.py"
  "src/cgfoil/cli/cli.py"
  "src/cgfoil/core/normals.py"
  "src/cgfoil/core/main.py"
  "src/cgfoil/core/mesh.py"
  "src/cgfoil/core/__init__.py"
  "src/cgfoil/core/trim.py"
  "src/cgfoil/core/offset.py"
  "src/cgfoil/utils/summary.py"
  "src/cgfoil/utils/logger.py"
  "src/cgfoil/utils/io.py"
  "src/cgfoil/utils/__init__.py"
  "src/cgfoil/utils/plot.py"
  "src/cgfoil/utils/geometry.py"
  "examples/example_list.py"
  "examples/example.py"
  "examples/yaml_example.py"
  "examples/__init__.py"
  "examples/example_vtp_multi_ply.py"
  "examples/example_vtp_section.py"
  "examples/example_vtp_multi_section.py"
  "examples/example_list_web2.py"
  "examples/example_list_web.py"
  "tests/test_cli.py"
  "tests/test_basic.py"
  "tests/test_export.py"
  "tests/test_examples.py"
  "tests/__init__.py"
  "tests/test_validation.py"
)

ruff format
ruff check --fix > out.txt
uv run pytest -v >> out.txt

for file in "${files[@]}"; do
  if [ ! -f "$file" ]; then
    git add "$file"
  fi
  git commit "$file" -m "summary of edits for $file"
done

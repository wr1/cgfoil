#!/bin/bash

# List of files added/modified
files=(
  "examples/example_m2.py"
)

# Run ruff format
ruff format

# Run ruff check and pipe to out.txt
ruff check --fix > out.txt

# Run pytest and append to out.txt
uv run pytest -v >> out.txt

# Git add, commit for each file
for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    git add "$file"
    git commit -m "Change reverse_point_order_triangles to sort_points_by_y"
  fi
done

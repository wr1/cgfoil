# admin.sh
ruff format
ruff check --fix > out.txt
git add admin.sh
git commit admin.sh -m 'add admin.sh'
git commit tests/test_cli.py -m 'change from os.path to Path in test_cli'
uv run pytest -v >> out.txt

# cgfoil

A CGAL-based airfoil meshing tool for generating constrained Delaunay triangulations of airfoils with plies and webs.

## Installation

Install with uv:

```bash
uv pip install .
```

Or with pip:

```bash
pip install .
```

## Usage

Run the CLI:

```bash
cgfoil --plot --vtk output.vtk
```

Options:
- `-p, --plot`: Plot the triangulation
- `-v, --vtk FILE`: Output VTK file

## Development

Use uv for dependency management:

```bash
uv sync
```

Run tests:

```bash
uv run pytest
```

Format code:

```bash
uv run ruff format
```

Lint:

```bash
uv run ruff check
```

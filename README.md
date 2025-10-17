# cgfoil

A CGAL-based airfoil meshing tool for generating constrained Delaunay triangulations of airfoils with plies and webs.

## Installation

Install with uv:

```bash
uv pip install .
```

## Usage

Run the CLI:

```bash
cgfoil mesh --plot --vtk output.vtk
```

Options:
- `-p, --plot`: Plot the triangulation
- `-v, --vtk FILE`: Output VTK file
- `-f, --file FILE`: Path to airfoil data file (.dat), default: naca0018.dat
- `-s, --split`: Enable split view plotting
- `--plot-file FILE`: Save plot to file instead of showing

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

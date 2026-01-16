"""Plot command functionality."""

import pickle
from pathlib import Path

from cgfoil.core.main import plot_mesh


def plot_existing_mesh(mesh_file: str, plot_filename=None, split=False):
    """Plot an existing mesh from file."""
    with Path(mesh_file).open("rb") as f:
        mesh_result = pickle.load(f)  # noqa: S301
    plot_mesh(mesh_result, plot_filename, split)

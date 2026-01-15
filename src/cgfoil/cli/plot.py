"""Plot command functionality."""

from __future__ import annotations

import pickle

from cgfoil.core.main import plot_mesh


def plot_existing_mesh(
    mesh_file: str, plot_filename: str | None = None, split: bool = False
):
    """Plot an existing mesh from file."""
    with open(mesh_file, "rb") as f:
        mesh_result = pickle.load(f)
    plot_mesh(mesh_result, plot_filename, split)

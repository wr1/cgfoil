"""Export utilities for cgfoil."""

import json
import pickle
from pathlib import Path

from cgfoil.core.anba import build_anba_data
from cgfoil.utils.io import save_mesh_to_vtk


def export_mesh_to_vtk(mesh_file: str, vtk_file: str) -> None:
    """Export mesh result to VTK file."""
    with Path(mesh_file).open("rb") as f:
        mesh_result = pickle.load(f)  # noqa: S301
    save_mesh_to_vtk(mesh_result, None, vtk_file)


def export_mesh_to_anba(mesh_file: str, anba_file: str, matdb=None) -> None:
    """Export mesh result to ANBA JSON format."""
    with Path(mesh_file).open("rb") as f:
        mesh_result = pickle.load(f)  # noqa: S301
    if isinstance(matdb, str):
        with Path(matdb).open() as f:
            matdb = json.load(f)
    data = build_anba_data(mesh_result, matdb)
    with Path(anba_file).open("w") as f:
        json.dump(data, f, indent=2)

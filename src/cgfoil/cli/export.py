"""Export utilities for cgfoil."""

import json
import pickle
from ..core.anba import build_anba_data
from ..utils.io import save_mesh_to_vtk


def export_mesh_to_vtk(mesh_file: str, vtk_file: str) -> None:
    """Export mesh result to VTK file."""
    with open(mesh_file, "rb") as f:
        mesh_result = pickle.load(f)
    save_mesh_to_vtk(mesh_result, None, vtk_file)


def export_mesh_to_anba(mesh_file: str, anba_file: str, matdb=None) -> None:
    """Export mesh result to ANBA JSON format."""
    with open(mesh_file, "rb") as f:
        mesh_result = pickle.load(f)
    if isinstance(matdb, str):
        with open(matdb, "r") as f:
            matdb = json.load(f)
    data = build_anba_data(mesh_result, matdb)
    with open(anba_file, "w") as f:
        json.dump(data, f, indent=2)

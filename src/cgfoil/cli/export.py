"""Export command functionalities."""

import pickle
import json
from cgfoil.utils.logger import logger


def export_mesh_to_vtk(mesh_file: str, vtk_file: str):
    """Export mesh to VTK file."""
    with open(mesh_file, "rb") as f:
        mesh_result = pickle.load(f)
    try:
        from cgfoil.core.vtk import build_vtk_mesh
        mesh_obj = build_vtk_mesh(mesh_result)
        mesh_obj.save(vtk_file)
        logger.info(f"Mesh exported to {vtk_file}")
    except ImportError:
        logger.warning("pyvista not available")


def export_mesh_to_anba(mesh_file: str, anba_file: str):
    """Export mesh to ANBA format (JSON)."""
    with open(mesh_file, "rb") as f:
        mesh_result = pickle.load(f)
    from cgfoil.core.anba import build_anba_data
    data = build_anba_data(mesh_result)
    with open(anba_file, "w") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Mesh exported to {anba_file}")

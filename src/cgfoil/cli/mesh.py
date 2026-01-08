"""Mesh command functionality."""

import pickle
import yaml
import sys
from cgfoil.core.main import generate_mesh
from cgfoil.models import AirfoilMesh
from cgfoil.utils.logger import logger
from cgfoil.utils.io import save_mesh_to_vtk


def mesh_from_yaml(yaml_file: str, output_mesh: str = None, vtk_file: str = None):
    """Generate mesh from YAML file."""
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)
    mesh = AirfoilMesh(**data)
    try:
        mesh_result = generate_mesh(mesh)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    if output_mesh:
        with open(output_mesh, "wb") as f:
            pickle.dump(mesh_result, f)
        logger.info(f"Mesh saved to {output_mesh}")
    if vtk_file:
        save_mesh_to_vtk(mesh_result, mesh, vtk_file)
    return mesh_result

"""Mesh command functionality."""

from __future__ import annotations

import pickle
import sys

import yaml

from cgfoil.core.main import generate_mesh
from cgfoil.models import AirfoilMesh
from cgfoil.utils.io import save_mesh_to_vtk
from cgfoil.utils.logger import logger


def mesh_from_yaml(
    yaml_file: str, output_mesh: str | None = None, vtk_file: str | None = None
):
    """Generate mesh from YAML file."""
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    mesh = AirfoilMesh(**data)
    try:
        mesh_result = generate_mesh(mesh)
    except ValueError:
        sys.exit(1)
    if output_mesh:
        with open(output_mesh, "wb") as f:
            pickle.dump(mesh_result, f)
        logger.info(f"Mesh saved to {output_mesh}")
    if vtk_file:
        save_mesh_to_vtk(mesh_result, mesh, vtk_file)
    return mesh_result

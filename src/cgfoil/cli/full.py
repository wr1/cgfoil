"""Full pipeline command functionality."""

import os
import pickle

import yaml

from cgfoil.cli.export import export_mesh_to_anba, export_mesh_to_vtk
from cgfoil.cli.plot import plot_existing_mesh
from cgfoil.cli.summary import summarize_mesh
from cgfoil.core.main import generate_mesh
from cgfoil.models import AirfoilMesh
from cgfoil.utils.logger import logger


def full_mesh(yaml_file: str, output_dir: str):
    """Run full meshing pipeline."""
    os.makedirs(output_dir, exist_ok=True)
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    mesh = AirfoilMesh(**data)
    mesh_result = generate_mesh(mesh)
    # Save mesh
    mesh_file = os.path.join(output_dir, "mesh.pck")
    with open(mesh_file, "wb") as f:
        pickle.dump(mesh_result, f)
    logger.info(f"Mesh saved to {mesh_file}")
    # Plot
    plot_filename = os.path.join(output_dir, "plot.png")
    plot_existing_mesh(mesh_file, plot_filename, True)
    # VTK
    vtk_file = os.path.join(output_dir, "mesh.vtk")
    export_mesh_to_vtk(mesh_file, vtk_file)
    # ANBA
    anba_file = os.path.join(output_dir, "mesh.json")
    export_mesh_to_anba(mesh_file, anba_file)
    # Summary
    summary_file = os.path.join(output_dir, "summary.csv")
    summarize_mesh(mesh_file, summary_file)

"""Main execution logic for cgfoil."""

from cgfoil.core.generate_mesh import generate_mesh
from cgfoil.core.plot_mesh import plot_mesh
from cgfoil.models import AirfoilMesh
from cgfoil.utils.io import save_mesh_to_vtk
from cgfoil.utils.logger import logger


def run_cgfoil(mesh: AirfoilMesh):
    mesh_result = generate_mesh(mesh)
    logger.info(f"Cross-sectional areas: {mesh_result.areas}")

    if mesh.vtk:
        save_mesh_to_vtk(mesh_result, mesh, mesh.vtk)

    if mesh.plot:
        plot_mesh(mesh_result, mesh.plot_filename, mesh.split_view)

    logger.info(f"Number of vertices: {len(mesh_result.vertices)}")
    logger.info(f"Number of faces: {len(mesh_result.faces)}")
    logger.info(f"Web Material ids: {mesh_result.web_material_ids}")
    logger.info(f"Skin Material ids: {mesh_result.skin_material_ids}")

"""Demonstrates airfoil meshing from a VTP file with multi-section processing."""

from __future__ import annotations

import multiprocessing
import os

from cgfoil.core.main import run_cgfoil
from cgfoil.models import AirfoilMesh, Ply, Skin, Thickness, Web

try:
    import pyvista as pv
except ImportError:
    msg = "pyvista is required for this example"
    raise ImportError(msg)

# Rotation angle around z-axis
ROTATION_ANGLE = 90


def process_single_section(args):
    """Process a single section_id."""
    section_id, vtp_file, output_base_dir = args
    try:
        # Load VTP file in each process to avoid serialization issues
        mesh_vtp = pv.read(vtp_file).rotate_z(ROTATION_ANGLE)

        # Create subdirectory
        section_dir = os.path.join(output_base_dir, f"section_{section_id}")
        os.makedirs(section_dir, exist_ok=True)

        # Filter mesh for this section_id
        section_mesh = mesh_vtp.threshold(
            value=(section_id, section_id),
            scalars="section_id",
        )

        # Extract airfoil (assuming panel_id logic similar to original)
        airfoil = section_mesh.threshold(value=(0, 12), scalars="panel_id")
        te = section_mesh.threshold(value=(-3, -3), scalars="panel_id")
        points_2d = airfoil.points[:, :2].tolist()[:-1] + te.points[:, :2].tolist()[1:]

        # Extract webs
        web1 = section_mesh.threshold(value=(-1, -1), scalars="panel_id")
        web2 = section_mesh.threshold(value=(-2, -2), scalars="panel_id")
        web_points_2d_1 = web1.points[:, :2].tolist()
        web_points_2d_2 = web2.points[:, :2].tolist()

        # Get thicknesses (assuming similar to original)
        ply_000001_plate_100_thickness = (
            list(
                (
                    airfoil.cell_data_to_point_data().point_data[
                        "ply_000001_plate_100_thickness"
                    ]
                    * 0.01
                )
                + 0.04,
            )[:-1]
            + list(
                te.cell_data_to_point_data().point_data[
                    "ply_000001_plate_100_thickness"
                ]
                * 1
                + 0.04,
            )[1:]
        )

        web_ply_thickness_1 = [0.004] * len(web_points_2d_1)
        web_ply_thickness_2 = [0.004] * len(web_points_2d_2)

        # Define skins
        skins = {
            "skin": Skin(
                thickness=Thickness(type="array", array=ply_000001_plate_100_thickness),
                material=1,
                sort_index=1,
            ),
        }

        # Define webs
        web_definition = {
            "web1": Web(
                coord_input=web_points_2d_1,
                plies=[
                    Ply(
                        thickness=Thickness(type="array", array=web_ply_thickness_1),
                        material=2,
                    ),
                ],
                normal_ref=[1, 0],
            ),
            "web2": Web(
                coord_input=web_points_2d_2,
                plies=[
                    Ply(
                        thickness=Thickness(type="array", array=web_ply_thickness_2),
                        material=3,
                    ),
                ],
                normal_ref=[-1, 0],
            ),
        }

        # Create AirfoilMesh
        mesh = AirfoilMesh(
            skins=skins,
            webs=web_definition,
            airfoil_input=points_2d,
            n_elem=None,
            plot=True,
            plot_filename=os.path.join(section_dir, "plot.png"),
            vtk=os.path.join(section_dir, "output.vtk"),
            split_view=True,
        )

        # Run the meshing
        run_cgfoil(mesh)
    except Exception:
        pass


def process_vtp_multi_section(
    vtp_file: str,
    output_base_dir: str,
    num_processes: int | None = None,
):
    """Process VTP file for all unique section_ids, outputting to subdirectories."""
    # Load VTP file to get unique ids
    mesh_vtp = pv.read(vtp_file).rotate_z(ROTATION_ANGLE)

    # Get unique section_ids
    if "section_id" not in mesh_vtp.cell_data:
        msg = "section_id not found in VTP file"
        raise ValueError(msg)
    unique_section_ids = mesh_vtp.cell_data["section_id"]
    unique_ids = sorted(set(unique_section_ids))
    total_sections = len(unique_ids)

    # Prepare arguments for multiprocessing
    args_list = [(section_id, vtp_file, output_base_dir) for section_id in unique_ids]

    # Use multiprocessing Pool
    if num_processes is None:
        num_processes = min(multiprocessing.cpu_count(), total_sections)
    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.map(process_single_section, args_list)


# Example usage
if __name__ == "__main__":
    vtp_file = "examples/airfoil_sections.vtp"  # Assume this file exists
    output_base_dir = "multi_section_output"
    process_vtp_multi_section(vtp_file, output_base_dir)

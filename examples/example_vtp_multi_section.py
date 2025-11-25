"""Example demonstrating airfoil meshing from a VTP file with multi-section processing."""

import os
import pyvista as pv
from cgfoil.core.main import run_cgfoil
from cgfoil.models import Skin, Web, Ply, AirfoilMesh, Thickness


def process_vtp_multi_section(vtp_file: str, output_base_dir: str):
    """Process VTP file for all unique section_ids, outputting to subdirectories."""
    # Load VTP file
    mesh_vtp = pv.read(vtp_file)

    # Get unique section_ids
    if "section_id" not in mesh_vtp.cell_data:
        raise ValueError("section_id not found in VTP file")
    unique_section_ids = mesh_vtp.cell_data["section_id"]
    unique_ids = set(unique_section_ids)

    for section_id in sorted(unique_ids):
        print(f"Processing section_id: {section_id}")
        # Create subdirectory
        section_dir = os.path.join(output_base_dir, f"section_{section_id}")
        os.makedirs(section_dir, exist_ok=True)

        # Filter mesh for this section_id
        section_mesh = mesh_vtp.threshold(
            value=(section_id, section_id), scalars="section_id"
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
                + 0.04
            )[:-1]
            + list(
                te.cell_data_to_point_data().point_data[
                    "ply_000001_plate_100_thickness"
                ]
                * 1
                + 0.04
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
                airfoil_input=web_points_2d_1,
                plies=[
                    Ply(
                        thickness=Thickness(type="array", array=web_ply_thickness_1),
                        material=2,
                    ),
                ],
                normal_ref=[1, 0],
            ),
            "web2": Web(
                airfoil_input=web_points_2d_2,
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
        )

        # Run the meshing
        run_cgfoil(mesh)


# Example usage
if __name__ == "__main__":
    vtp_file = "airfoil_sections.vtp"  # Assume this file exists
    output_base_dir = "multi_section_output"
    process_vtp_multi_section(vtp_file, output_base_dir)

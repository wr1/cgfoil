"""Example demonstrating airfoil meshing from a VTP file with section isolation."""

import argparse
import pyvista as pv
from cgfoil.core.main import run_cgfoil
from cgfoil.models import Skin, Web, Ply, AirfoilMesh, Thickness

parser = argparse.ArgumentParser(description="Process VTP file for airfoil meshing.")
parser.add_argument('--vtp-file', default='examples/airfoil_sections.vtp', help='Path to the VTP file')
parser.add_argument('--section-id', type=int, default=28, help='Section ID threshold')
args = parser.parse_args()

try:
    # Load VTP file containing multiple sections
    vtp_file = args.vtp_file
    mesh_vtp = (
        pv.read(vtp_file).rotate_z(90)
    )

    # First get the section by threshold section_id==args.section_id
    section_mesh = mesh_vtp.threshold(value=(args.section_id, args.section_id), scalars="section_id")

    airfoil = section_mesh.threshold(value=(0, 12), scalars="panel_id")

    te = section_mesh.threshold(value=(-3, -3), scalars="panel_id")

    web1 = section_mesh.threshold(value=(-1, -1), scalars="panel_id")
    web2 = section_mesh.threshold(value=(-2, -2), scalars="panel_id")

    # Extract points from the airfoil section
    points_2d = airfoil.points[:, :2].tolist()[:-1] + te.points[:, :2].tolist()[1:]
    # Take x, y coordinates

    # Extract points from the web sections
    web_points_2d_1 = web1.points[:, :2].tolist()
    web_points_2d_2 = web2.points[:, :2].tolist()

    if not points_2d:
        raise ValueError("No airfoil points extracted from VTP file")

    # Get thickness from VTP
    # preserve this particular numbering/indexing, the scaling is arbitrary
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
            te.cell_data_to_point_data().point_data["ply_000001_plate_100_thickness"] * 1
            + 0.04
        )[1:]
    )

    print(len(ply_000001_plate_100_thickness), len(points_2d))

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
            coord_input=web_points_2d_1,  # List of (x, y) tuples for the web
            plies=[
                Ply(
                    thickness=Thickness(type="array", array=web_ply_thickness_1), material=2
                ),
            ],
            normal_ref=[1, 0],
        ),
        "web2": Web(
            coord_input=web_points_2d_2,  # List of (x, y) tuples for the web
            plies=[
                    Ply(
                        thickness=Thickness(type="array", array=web_ply_thickness_2), material=3
                    ),
            ],
            normal_ref=[-1, 0],
        ),
    }

    # Create AirfoilMesh using the extracted points
    mesh = AirfoilMesh(
        skins=skins,
        webs=web_definition,
        # webs={},
        airfoil_input=points_2d,  # List of (x, y) tuples
        n_elem=None,  # Keep input spacing, do not resample
        plot=False,  # Disable plotting for headless CI
        plot_filename=None,
        vtk="output_vtp_section.vtk",
    )

    # Run the meshing
    run_cgfoil(mesh)
except Exception as e:
    print(f"Error in example_vtp_section: {e}")
    import sys
    sys.exit(1)

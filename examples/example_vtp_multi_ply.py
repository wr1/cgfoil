"""Example demonstrating airfoil meshing from a VTP file with multiple plies."""

import argparse
import pyvista as pv
import re
from cgfoil.core.main import run_cgfoil
from cgfoil.models import Skin, Web, Ply, AirfoilMesh, Thickness

parser = argparse.ArgumentParser(
    description="Process VTP file for multi-ply airfoil meshing."
)
parser.add_argument(
    "--vtp-file", default="examples/airfoil_sections.vtp", help="Path to the VTP file"
)
parser.add_argument("--section-id", type=int, default=28, help="Section ID threshold")
args = parser.parse_args()

# Load VTP file containing multiple sections
vtp_file = args.vtp_file
mesh_vtp = (
    pv.read(vtp_file)
    .threshold(value=(args.section_id, args.section_id), scalars="section_id")
    .rotate_z(-90)
    .rotate_x(180)
)

airfoil = mesh_vtp.threshold(value=(0, 12), scalars="panel_id")
web1 = mesh_vtp.threshold(value=(-1, -1), scalars="panel_id")
web2 = mesh_vtp.threshold(value=(-2, -2), scalars="panel_id")

# Extract points from the airfoil section
points_2d = airfoil.points[:, :2].tolist()

# Extract points from the web sections
web_points_2d_1 = web1.points[:, :2].tolist()
web_points_2d_2 = web2.points[:, :2].tolist()

# Function to get thickness arrays from mesh

def get_thickness_arrays(mesh):
    """Get all thickness arrays from mesh cell_data matching ply_*_thickness."""
    # Convert cell data to point data
    mesh_point = mesh.cell_data_to_point_data()
    thickness_keys = [
        k for k in mesh_point.point_data.keys() if re.match(r"ply_.*_thickness", k)
    ]
    print(f"Found thickness keys: {thickness_keys}")
    # Sort by the number in the name, assuming ply_XXXX_...
    thickness_keys.sort(key=lambda x: int(re.search(r"ply_(\d+)", x).group(1)))
    return {k: mesh_point.point_data[k] for k in thickness_keys}


# Get thicknesses for airfoil
airfoil_thicknesses = get_thickness_arrays(airfoil)

# Get thicknesses for webs
web1_thicknesses = get_thickness_arrays(web1)
web2_thicknesses = get_thickness_arrays(web2)

# Define skins (multiple layers from airfoil thicknesses)
skins = {}
material_id = 1
for i, (key, thickness_array) in enumerate(airfoil_thicknesses.items(), start=1):
    skins[f"skin{i}"] = Skin(
        thickness=Thickness(type="array", array=thickness_array),
        material=material_id,
        sort_index=i,
    )
    material_id += 1

# Define webs (multiple plies per web from their thicknesses)
web_definition = {}
web_meshes = [
    ("web1", web1_thicknesses, web_points_2d_1),
    ("web2", web2_thicknesses, web_points_2d_2),
]
for web_name, thicknesses, points in web_meshes:
    plies = []
    for key, thickness_array in thicknesses.items():
        plies.append(
            Ply(
                thickness=Thickness(type="array", array=thickness_array),
                material=material_id,
            )
        )
        material_id += 1
    normal_ref = [1, 0] if web_name == "web1" else [-1, 0]
    web_definition[web_name] = Web(
        coord_input=points,
        plies=plies,
        normal_ref=normal_ref,
    )

# Create AirfoilMesh using the extracted points
mesh = AirfoilMesh(
    skins=skins,
    webs=web_definition,
    airfoil_input=points_2d,  # List of (x, y) tuples
    n_elem=None,  # Keep input spacing, do not resample
    plot=True,
    plot_filename="example_vtp_multi_ply.png",
    vtk="output_vtp_multi_ply.vtk",
    split_view=True,
)

# Run the meshing
run_cgfoil(mesh)

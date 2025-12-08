"""Merged example with TE logic from vtp_section and generalized
ply logic from vtp_multi_ply."""

import argparse
import pyvista as pv
import re
from cgfoil.core.main import run_cgfoil
from cgfoil.models import Skin, Web, Ply, AirfoilMesh, Thickness

parser = argparse.ArgumentParser(
    description="Process VTP file for merged airfoil meshing."
)
parser.add_argument(
    "--vtp-file", default="examples/airfoil_sections.vtp", help="Path to the VTP file"
)
parser.add_argument("--section-id", type=int, default=28, help="Section ID threshold")
args = parser.parse_args()

# Load VTP file containing multiple sections with rotations
vtp_file = args.vtp_file
mesh_vtp = pv.read(vtp_file).rotate_z(-90).rotate_x(180)

# Filter for section
section_mesh = mesh_vtp.threshold(
    value=(args.section_id, args.section_id), scalars="section_id"
)


def sort_points_by_y(mesh: pv.PolyData) -> pv.PolyData:
    """
    For a triangular PolyData mesh:
    - Sort points by y-coordinate (min to max)
    - Update triangle connectivity
    - Keep point_data correctly aligned
    """
    mesh = mesh.copy()
    n = mesh.n_points

    # Sort by y-coordinate
    sorted_indices = sorted(range(n), key=lambda i: mesh.points[i, 1])
    mesh.points = mesh.points[sorted_indices]

    # Create mapping from old to new indices
    old_to_new = {old: new for new, old in enumerate(sorted_indices)}

    # Update connectivity
    cells = mesh.cells.copy()
    cells[1::4] = [old_to_new[cells[i]] for i in range(1, len(cells), 4)]
    cells[2::4] = [old_to_new[cells[i]] for i in range(2, len(cells), 4)]
    cells[3::4] = [old_to_new[cells[i]] for i in range(3, len(cells), 4)]
    mesh.cells = cells

    # Update point_data
    for key in mesh.point_data.keys():
        mesh.point_data[key] = mesh.point_data[key][sorted_indices]

    return mesh


# Select airfoil including TE: panel_id >= 0 (selects the airfoil) or
# panel_id == min(panel_id) (selects TE)
min_panel_id = section_mesh.cell_data["panel_id"].min()
airfoil = pv.merge(
    [
        section_mesh.threshold(
            value=(0, section_mesh.cell_data["panel_id"].max()), scalars="panel_id"
        ),
        sort_points_by_y(
            section_mesh.threshold(
                value=(min_panel_id, min_panel_id), scalars="panel_id"
            )
        ),
    ]
)

points_2d = airfoil.points[:, :2].tolist()

web1 = section_mesh.threshold(value=(-1, -1), scalars="panel_id")
web2 = section_mesh.threshold(value=(-2, -2), scalars="panel_id")

web_points_2d_1 = web1.points[:, :2].tolist()
web_points_2d_2 = web2.points[:, :2].tolist()


# Function to get thickness arrays from mesh
def get_thickness_arrays(mesh):
    mesh_point = mesh.cell_data_to_point_data()
    thickness_keys = [
        k for k in mesh_point.point_data.keys() if re.match(r"ply_.*_thickness", k)
    ]
    thickness_keys.sort(key=lambda x: int(re.search(r"ply_(\d+)", x).group(1)))
    return {k: mesh_point.point_data[k] for k in thickness_keys}


# Get thicknesses
airfoil_thicknesses = get_thickness_arrays(airfoil)

web1_thicknesses = get_thickness_arrays(web1)
web2_thicknesses = get_thickness_arrays(web2)

# Define skins
skins = {}
material_id = 1
for i, (key, thickness_array) in enumerate(airfoil_thicknesses.items(), start=1):
    skins[f"skin{i}"] = Skin(
        thickness=Thickness(type="array", array=list(thickness_array)),
        material=material_id,
        sort_index=i,
    )
    material_id += 1

# Define webs
web_definition = {}
web_meshes = [
    ("web1", web1_thicknesses, web_points_2d_1),
    ("web2", web2_thicknesses, web_points_2d_2),
]
for web_name, thicknesses, points in web_meshes:
    plies = [
        Ply(
            thickness=Thickness(type="array", array=list(thicknesses[key])),
            material=material_id + j,
        )
        for j, key in enumerate(thicknesses)
    ]
    material_id += len(thicknesses)
    normal_ref = [1, 0] if web_name == "web1" else [-1, 0]
    web_definition[web_name] = Web(
        coord_input=points, plies=plies, normal_ref=normal_ref
    )

# Create AirfoilMesh
mesh = AirfoilMesh(
    skins=skins,
    webs=web_definition,
    airfoil_input=points_2d,
    n_elem=None,
    plot=True,
    plot_filename="plot_m2.png",
    split_view=True,
    vtk="output_m2.vtk",
)

# Run the meshing
run_cgfoil(mesh)

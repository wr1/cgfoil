"""Example demonstrating airfoil meshing from a VTP file with section isolation."""

import pyvista as pv
from cgfoil.core.main import run_cgfoil
from cgfoil.models import Skin, Web, Ply, AirfoilMesh, Thickness

# Load VTP file containing multiple sections
vtp_file = "airfoil_sections.vtp"  # Assume this file exists with cell_data 'section_id' and 'panel_id'
mesh_vtp = (
    pv.read(vtp_file).threshold(value=(28, 28), scalars="section_id").rotate_z(90)
)

airfoil = mesh_vtp.threshold(value=(0, 12), scalars="panel_id")
web1 = mesh_vtp.threshold(value=(-1, -1), scalars="panel_id")
web2 = mesh_vtp.threshold(value=(-2, -2), scalars="panel_id")

# Extract points from the airfoil section
points_2d = airfoil.points[:, :2].tolist()  # Take x, y coordinates

# Extract points from the web sections
web_points_2d_1 = web1.points[:, :2].tolist()
web_points_2d_2 = web2.points[:, :2].tolist()

# Define skins
skins = {
    "skin": Skin(
        thickness=Thickness(type="constant", value=0.05),
        material=1,
        sort_index=1,
    ),
}

# Define webs
web_definition = {
    "web1": Web(
        airfoil_input=web_points_2d_1,  # List of (x, y) tuples for the web
        plies=[
            Ply(thickness=Thickness(type="constant", value=0.004), material=2),
        ],
        normal_ref=[1, 0],
    ),
    "web2": Web(
        airfoil_input=web_points_2d_2,  # List of (x, y) tuples for the web
        plies=[
            Ply(thickness=Thickness(type="constant", value=0.004), material=3),
        ],
        normal_ref=[-1, 0],
    ),
}

# Create AirfoilMesh using the extracted points
mesh = AirfoilMesh(
    skins=skins,
    webs=web_definition,
    airfoil_input=points_2d,  # List of (x, y) tuples
    plot=True,
    plot_filename="plot_vtp_section.png",
    vtk="output_vtp_section.vtk",
)

# Run the meshing
run_cgfoil(mesh)

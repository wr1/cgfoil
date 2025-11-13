"""Example demonstrating airfoil meshing from a VTP file with section isolation."""

import pyvista as pv
from cgfoil.core.main import run_cgfoil
from cgfoil.models import Skin, AirfoilMesh, Thickness

# Load VTP file containing multiple sections
vtp_file = "airfoil_sections.vtp"  # Assume this file exists with cell_data 'section_id'
mesh_vtp = (
    pv.read(vtp_file).threshold(value=(28, 28), scalars="section_id").rotate_z(90)
)

airfoil = mesh_vtp.threshold(value=(0, 12), scalars="panel_id")


# Isolate section with section_id = 28
# section_id = 28
# mask = mesh_vtp.cell_data["section_id"] == section_id
# section_mesh = mesh_vtp.extract_cells(mask)

# Extract points from the isolated section (assuming it's a line or polyline)
points_2d = airfoil.points[:, :2].tolist()  # Take x, y coordinates

# Define skins
skins = {
    "skin": Skin(
        thickness=Thickness(type="constant", value=0.05),
        material=1,
        sort_index=1,
    ),
}

# Create AirfoilMesh using the extracted points
mesh = AirfoilMesh(
    skins=skins,
    webs={},
    airfoil_input=points_2d,  # List of (x, y) tuples
    plot=True,
    plot_filename="plot_vtp_section.png",
    vtk="output_vtp_section.vtk",
)

# Run the meshing
run_cgfoil(mesh)

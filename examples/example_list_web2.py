"""Programmatic example demonstrating airfoil meshing with webs loaded from VTK and array thickness."""

import numpy as np
import pyvista as pv
from cgfoil.core.main import run_cgfoil
from cgfoil.models import Skin, Web, Ply, AirfoilMesh, Thickness

# Define skins
skins = {
    "outer_skin": Skin(
        thickness=Thickness(type="constant", value=0.005),
        material=1,
        sort_index=1,
    ),
    "inner_skin": Skin(
        thickness=Thickness(type="constant", value=0.005),
        material=1,
        sort_index=2,
    ),
}

# Create a VTK file for the web
# Define web points at x=0.3
web_points = [
    (0.3, -0.1),
    (0.3, -0.05),
    (0.3, 0.0),
    (0.3, 0.05),
    (0.3, 0.1),
]
points_3d = np.array([[x, y, 0.0] for x, y in web_points])
lines = np.hstack([[len(points_3d)], np.arange(len(points_3d))])
web_mesh = pv.PolyData(points_3d, lines=lines)
web_mesh.save("web.vtk")
print("Saved web to web.vtk")

# Define thickness array for the web points
thickness_array = [0.004 + 0.001 * abs(y) for x, y in web_points]  # Varying thickness

# Define web using VTK input and array thickness
web_definition = {
    "web_at_03": Web(
        airfoil_input="web.vtk",
        plies=[
            Ply(thickness=Thickness(type="array", array=thickness_array), material=2)
        ],
        normal_ref=[1, 0],
    ),
}

# Create AirfoilMesh
mesh = AirfoilMesh(
    skins=skins,
    webs=web_definition,
    airfoil_input="naca0018.dat",
    plot=True,
    plot_filename="plot_web2.png",
    vtk="output_web2.vtk",
)

# Run the meshing
run_cgfoil(mesh)

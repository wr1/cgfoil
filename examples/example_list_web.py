"""Programmatic example demonstrating airfoil meshing with webs."""

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

# Load airfoil points to find points at x=0.3
airfoil_points = []
with open("naca0018.dat", "r") as f:
    lines = f.readlines()
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) == 2:
            x = float(parts[0])
            y = float(parts[1])
            airfoil_points.append((x, y))

# Find points where x ≈ 0.3
upper_point = None
lower_point = None
for x, y in airfoil_points:
    if abs(x - 0.3) < 0.01:
        if y > 0:
            upper_point = (x, y)
        elif y < 0:
            lower_point = (x, y)

if upper_point and lower_point:
    # Define web between upper and lower points at x=0.3
    web_definition = {
        "web_at_03": Web(
            points=(lower_point, upper_point),
            plies=[Ply(thickness=0.004, material=2)],
            normal_ref=[1, 0],
            n_cell=10,  # 10 cells
        ),
    }
else:
    web_definition = {}
    print("Warning: Could not find points at x=0.3")

# Create AirfoilMesh
mesh = AirfoilMesh(
    skins=skins,
    webs=web_definition,
    airfoil_input="naca0018.dat",
    plot=True,
    plot_filename="plot_web.png",
    vtk="output_web.vtk",
)

# Run the meshing
run_cgfoil(mesh)

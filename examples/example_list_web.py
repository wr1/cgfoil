"""Programmatic example demonstrating airfoil meshing with webs."""

from pathlib import Path

from cgfoil.core.main import run_cgfoil
from cgfoil.models import AirfoilMesh, Ply, Skin, Thickness, Web

NUM_PARTS = 2
TOLERANCE = 0.01

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
with Path("examples/naca0018.dat").open() as f:
    lines = f.readlines()
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) == NUM_PARTS:
            x = float(parts[0])
            y = float(parts[1])
            airfoil_points.append((x, y))

# Find points where x ≈ 0.3
upper_point = None
lower_point = None
for x, y in airfoil_points:
    if abs(x - 0.3) < TOLERANCE:
        if y > 0:
            upper_point = (x, y)
        elif y < 0:
            lower_point = (x, y)

if upper_point and lower_point:
    # Define web between upper and lower points at x=0.3
    web_definition = {
        "web_at_03": Web(
            coord_input=[lower_point, upper_point],
            plies=[Ply(thickness=Thickness(type="constant", value=0.004), material=2)],
            normal_ref=[1, 0],
            n_elem=10,  # 10 cells
        ),
    }
else:
    web_definition = {}

# Create AirfoilMesh
mesh = AirfoilMesh(
    skins=skins,
    webs=web_definition,
    airfoil_input="examples/naca0018.dat",
    plot=True,
    plot_filename="example_list_web.png",
    vtk="output_web.vtk",
    split_view=True,
)

# Run the meshing
run_cgfoil(mesh)

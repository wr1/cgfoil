"""Programmatic example demonstrating different airfoil input types for cgfoil."""

import numpy as np
import pyvista as pv
from cgfoil.core.main import run_cgfoil
from cgfoil.models import Skin, AirfoilMesh, Thickness

# Simplified skins and webs for demonstration
skins = {
    "skin": Skin(
        thickness=Thickness(type="constant", value=0.005),
        material=1,
        sort_index=1,
    ),
}

web_definition = {}

# Example 1: Using a filename (string)
print("Example 1: Loading airfoil from .dat file")
mesh1 = AirfoilMesh(
    skins=skins,
    webs=web_definition,
    airfoil_input="naca0018.dat",  # Filename
    plot=False,  # Disable plotting for headless CI
    plot_filename=None,
    vtk="output1.vtk",
)
run_cgfoil(mesh1)

# Example 2: Using a list of tuples
print("Example 2: Providing airfoil points as a list of tuples")
airfoil_points_list = [
    (0.0, 0.0),
    (0.1, 0.01),
    (0.2, 0.02),
    (0.3, 0.03),
    (0.4, 0.04),
    (0.5, 0.05),
    (0.6, 0.04),
    (0.7, 0.03),
    (0.8, 0.02),
    (0.9, 0.01),
    (1.0, 0.0),
]  # Simplified airfoil points
mesh2 = AirfoilMesh(
    skins=skins,
    webs=web_definition,
    airfoil_input=airfoil_points_list,  # List of (x, y) tuples
    n_elem=50,  # Resample to 50 elements
    plot=False,  # Disable plotting for headless CI
    plot_filename=None,
    vtk="output2.vtk",
)
run_cgfoil(mesh2)

# Example 3: Using a NumPy array
print("Example 3: Providing airfoil points as a NumPy array")
airfoil_points_array = np.array(
    [
        [0.0, 0.0],
        [0.1, 0.01],
        [0.2, 0.02],
        [0.3, 0.03],
        [0.4, 0.04],
        [0.5, 0.05],
        [0.6, 0.04],
        [0.7, 0.03],
        [0.8, 0.02],
        [0.9, 0.01],
        [1.0, 0.0],
    ]
)  # NumPy array of shape (n, 2)
mesh3 = AirfoilMesh(
    skins=skins,
    webs=web_definition,
    airfoil_input=airfoil_points_array,  # NumPy array
    n_elem=50,  # Resample to 50 elements
    plot=False,  # Disable plotting for headless CI
    plot_filename=None,
    vtk="output3.vtk",
)
run_cgfoil(mesh3)

# Example 4: Using a VTK file created from .dat
print("Example 4: Converting .dat to VTK and using VTK file")
# Load points from .dat
points_2d = []
with open("naca0018.dat", "r") as f:
    lines = f.readlines()
    for line in lines[1:]:  # Skip header
        parts = line.strip().split()
        if len(parts) == 2:
            x = float(parts[0])
            y = float(parts[1])
            points_2d.append([x, y])
# Create pyvista PolyData for line
points_3d = np.array([[x, y, 0.0] for x, y in points_2d])
lines = np.hstack([[len(points_3d)], np.arange(len(points_3d))])
mesh_vtk = pv.PolyData(points_3d, lines=lines)
mesh_vtk.save("airfoil.vtk")
print("Saved airfoil to airfoil.vtk")
mesh4 = AirfoilMesh(
    skins=skins,
    webs=web_definition,
    airfoil_input="airfoil.vtk",  # VTK filename
    plot=False,  # Disable plotting for headless CI
    plot_filename=None,
    vtk="output4.vtk",
)
run_cgfoil(mesh4)

# Example 5: Using array thickness definition
print("Example 5: Using array thickness definition")
# Load airfoil points to get the number of points
airfoil_points = []
with open("naca0018.dat", "r") as f:
    lines = f.readlines()
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) == 2:
            x = float(parts[0])
            y = float(parts[1])
            airfoil_points.append((x, y))
# Define thickness array, e.g., varying thickness
thickness_array = [
    0.005 + 0.002 * abs(y) for x, y in airfoil_points
]  # Example: thicker at camber
skins_array = {
    "skin": Skin(
        thickness=Thickness(type="array", array=thickness_array),
        material=1,
        sort_index=1,
    ),
}
mesh5 = AirfoilMesh(
    skins=skins_array,
    webs=web_definition,
    airfoil_input="naca0018.dat",
    n_elem=None,  # Do not resample to match array length
    plot=False,  # Disable plotting for headless CI
    plot_filename=None,
    vtk="output5.vtk",
)
run_cgfoil(mesh5)

# Note: For VTK, ensure the file contains a line mesh with points in order.
# The code will extract the first two coordinates (x, y) from each point.

"""Programmatic example demonstrating different airfoil input types for cgfoil."""

import numpy as np
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
    plot=False,  # Disable plotting for demo
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
    plot=False,
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
    plot=False,
    vtk="output3.vtk",
)
run_cgfoil(mesh3)

# Example 4: Using a VTK file (assuming you have a VTK line mesh file)
print("Example 4: Loading airfoil from VTK file (commented out, requires VTK file)")
# mesh4 = AirfoilMesh(
#     skins=skins,
#     webs=web_definition,
#     airfoil_input="airfoil.vtk",  # VTK filename
#     plot=False,
#     vtk="output4.vtk",
# )
# run_cgfoil(mesh4)

# Note: For VTK, ensure the file contains a line mesh with points in order.
# The code will extract the first two coordinates (x, y) from each point.

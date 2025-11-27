"""Programmatic example for cgfoil."""

from cgfoil.core.main import run_cgfoil
from cgfoil.models import Skin, Web, Ply, AirfoilMesh, Thickness

# Define custom skins (shell definitions)
skins = {
    "outer_skin": Skin(
        thickness=Thickness(
            type="interp",
            coord="x",
            x=[0.0, 0.9, 1.0],
            y=[0.005, 0.005, 0.002],
        ),
        material=2,
        sort_index=1,
    ),
    "cap": Skin(
        thickness=Thickness(
            type="interp",
            coord="x",
            x=[0.2, 0.2001, 0.5, 0.5001],
            y=[0, 0.02, 0.02, 0],
        ),
        material=1,
        sort_index=2,
    ),
    "core": Skin(
        thickness=Thickness(
            type="interp",
            coord="x",
            x=[0.05, 0.1, 0.2, 0.20001, 0.5, 0.5001, 0.7, 0.9],
            y=[0, 0.01, 0.01, 0, 0, 0.02, 0.02, 0],
        ),
        material=3,
        sort_index=3,
    ),
    "te_ud": Skin(
        thickness=Thickness(
            type="interp",
            coord="x",
            x=[0.7, 0.75, 0.8, 0.85],
            y=[0, 0.01, 0.01, 0],
        ),
        material=4,
        sort_index=4,
    ),
    "inner_skin": Skin(
        thickness=Thickness(
            type="constant",
            coord="x",
            value=0.005,
        ),
        material=2,
        sort_index=5,
    ),
}

# Define custom web definition
web_definition = {
    "web1": Web(
        points=((0.25, -0.1), (0.25, 0.1)),
        plies=[
            Ply(thickness=Thickness(type="constant", value=0.004), material=5),
            Ply(
                thickness=Thickness(
                    type="interp",
                    coord="y",
                    x=[-0.04, -0.03, 0.03, 0.04],
                    y=[0, 0.01, 0.01, 0],
                ),
                material=3,
            ),
            Ply(thickness=Thickness(type="constant", value=0.004), material=5),
        ],
        normal_ref=[1, 0],
        n_cell=20,
    ),
    "web2": Web(
        points=((0.4, -0.1), (0.4, 0.1)),
        plies=[
            Ply(thickness=Thickness(type="constant", value=0.004), material=5),
            Ply(
                thickness=Thickness(
                    type="interp",
                    coord="y",
                    x=[-0.04, -0.03, 0.03, 0.04],
                    y=[0, 0.01, 0.01, 0],
                ),
                material=3,
            ),
            Ply(thickness=Thickness(type="constant", value=0.004), material=5),
        ],
        normal_ref=[-1, 0],
        n_cell=15,
    ),
    "web3": Web(
        points=((0.775, -0.1), (0.775, 0.1)),
        plies=[
            Ply(thickness=Thickness(type="constant", value=0.005), material=5),
            Ply(
                thickness=Thickness(type="constant", value=0.005),
                material=3,
            ),
            Ply(thickness=Thickness(type="constant", value=0.005), material=5),
        ],
        normal_ref=[-1, 0],
        n_cell=15,
    ),
}

# Create AirfoilMesh
mesh = AirfoilMesh(
    skins=skins,
    webs=web_definition,
    airfoil_input="naca0018.dat",
    plot=False,  # Disable plotting for headless CI
    vtk="output.vtk",
    scale_factor=1.05,
    split_view=True,
)

# Run the meshing
run_cgfoil(mesh)

# Alternatively, generate mesh separately
# mesh_result = generate_mesh(mesh)
# plot_mesh(mesh_result)

"""Command line interface for cgfoil."""

import numpy as np
from treeparse import cli, command, option
from cgfoil.core.main import run_cgfoil
from cgfoil.models import Skin, Web, Ply


def run(
    plot: bool = False,
    vtk: str = None,
    file: str = "naca0018.dat",
    split: bool = False,
    plot_file: str = None,
):
    # Default skins
    skins = {
        "outer_skin": Skin(
            thickness=lambda x: np.interp(x, [0.0, 0.9, 1], [0.005, 0.005, 0.002]),
            material=2,
            sort_index=1,
        ),
        "cap": Skin(
            thickness=lambda x: np.interp(
                x, [0.2, 0.2001, 0.5, 0.5001], [0, 0.02, 0.02, 0]
            ),
            material=1,
            sort_index=2,
        ),
        "core": Skin(
            thickness=lambda x: np.interp(
                x,
                [0.05, 0.1, 0.2, 0.20001, 0.5, 0.5001, 0.7, 0.9],
                [0, 0.01, 0.01, 0, 0, 0.02, 0.02, 0],
            ),
            material=3,
            sort_index=3,
        ),
        "te_ud": Skin(
            thickness=lambda x: np.interp(
                x, [0.7, 0.75, 0.8, 0.85], [0, 0.01, 0.01, 0]
            ),
            material=4,
            sort_index=4,
        ),
        "inner_skin": Skin(
            thickness=lambda x: np.interp(x, [0.0, 0.9, 1], [0.005, 0.005, 0.002]),
            material=2,
            sort_index=5,
        ),
    }

    # Default web definition
    web_definition = {
        "web1": Web(
            points=((0.25, -0.2), (0.25, 0.2)),
            plies=[
                Ply(thickness=0.004, material=5),
                Ply(
                    thickness=0.008,
                    # thickness=lambda y: np.interp(
                    #     y, [-0.04, -0.03, 0.03, 0.04], [0, 0.01, 0.01, 0]
                    # ),
                    material=3,
                ),
                Ply(thickness=0.004, material=5),
            ],
            normal_ref=[1, 0],
            n_cell=20,
        ),
        "web2": Web(
            points=((0.4, -0.2), (0.4, 0.2)),
            plies=[
                Ply(thickness=0.004, material=5),
                Ply(
                    thickness=0.008,
                    # lambda y: np.interp(
                    #     y, [-0.04, -0.03, 0.03, 0.04], [0, 0.01, 0.01, 0]
                    # ),
                    material=3,
                ),
                Ply(thickness=0.004, material=5),
            ],
            normal_ref=[-1, 0],
            n_cell=15,
        ),
        "web3": Web(
            points=((0.775, -0.1), (0.775, 0.1)),
            plies=[
                Ply(thickness=0.004, material=5),
                Ply(
                    thickness=0.008,
                    material=3,
                ),
                Ply(thickness=0.004, material=5),
            ],
            normal_ref=[-1, 0],
            n_cell=15,
        ),
    }

    run_cgfoil(
        skins,
        web_definition,
        airfoil_filename=file,
        plot=plot,
        vtk=vtk,
        split_view=split,
        plot_filename=plot_file,
    )


app = cli(
    name="cgfoil",
    help="CGAL-based airfoil meshing tool for generating constrained Delaunay triangulations of airfoils with plies and webs.",
    max_width=120,
    show_types=True,
    show_defaults=True,
    line_connect=True,
    theme="monochrome",
)

mesh_cmd = command(
    name="mesh",
    help="Run the meshing tool.",
    callback=run,
    options=[
        option(
            flags=["--plot", "-p"],
            arg_type=bool,
            default=False,
            help="Plot the triangulation",
            sort_key=0,
        ),
        option(
            flags=["--vtk", "-v"],
            arg_type=str,
            default=None,
            help="Output VTK file",
            sort_key=1,
        ),
        option(
            flags=["--file", "-f"],
            arg_type=str,
            default="naca0018.dat",
            help="Path to airfoil data file (.dat)",
            sort_key=2,
        ),
        option(
            flags=["--split", "-s"],
            arg_type=bool,
            default=False,
            help="Enable split view plotting",
            sort_key=3,
        ),
        option(
            flags=["--plot-file"],
            arg_type=str,
            default=None,
            help="Save plot to file instead of showing",
            sort_key=4,
        ),
    ],
)
app.commands.append(mesh_cmd)


def main():
    app.run()

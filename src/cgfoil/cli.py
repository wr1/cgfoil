"""Command line interface for cgfoil."""

import argparse
import numpy as np
from cgfoil.core.main import run_cgfoil
from cgfoil.models import Skin, Web, Ply


def main():
    parser = argparse.ArgumentParser(
        description="Mesh inside NACA 0018 airfoil, its offsets as hole, and adjusted line plies with proposed web definition, normal reference, and unique material ids."
    )
    parser.add_argument("-p", "--plot", action="store_true", help="Plot the triangulation")
    parser.add_argument("-v", "--vtk", type=str, help="Output VTK file")
    parser.add_argument("-f", "--file", type=str, default="naca0018.dat", help="Path to airfoil data file (.dat)")
    parser.add_argument("--split", action="store_true", help="Enable split view plotting")
    args = parser.parse_args()

    # Default skins
    skins = {
        "outer_skin": Skin(
            thickness=lambda x: np.interp(x, [0.0, 0.9, 1], [0.005, 0.005, 0.002]),
            material=2,
            sort_index=1,
        ),
        "cap": Skin(
            thickness=lambda x: np.interp(x, [0.2, 0.2001, 0.5, 0.5001], [0, 0.02, 0.02, 0]),
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
            thickness=lambda x: np.interp(x, [0.7, 0.75, 0.8, 0.85], [0, 0.01, 0.01, 0]),
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
            points=((0.25, -0.1), (0.25, 0.1)),
            plies=[
                Ply(thickness=0.004, material=5),
                Ply(
                    thickness=lambda y: np.interp(
                        y, [-0.04, -0.03, 0.03, 0.04], [0, 0.01, 0.01, 0]
                    ),
                    material=3,
                ),
                Ply(thickness=0.004, material=5),
            ],
            normal_ref=[1, 0],
            n_cell=20,
        ),
        "web2": Web(
            points=((0.4, -0.1), (0.4, 0.1)),
            plies=[
                Ply(thickness=0.004, material=5),
                Ply(
                    thickness=lambda y: np.interp(
                        y, [-0.04, -0.03, 0.03, 0.04], [0, 0.01, 0.01, 0]
                    ),
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
                Ply(thickness=0.005, material=5),
                Ply(
                    thickness=0.005,
                    material=3,
                ),
                Ply(thickness=0.005, material=5),
            ],
            normal_ref=[-1, 0],
            n_cell=15,
        ),
    }

    run_cgfoil(skins, web_definition, airfoil_filename=args.file, plot=args.plot, vtk=args.vtk, split_view=args.split)

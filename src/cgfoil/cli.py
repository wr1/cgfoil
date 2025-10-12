"""Command line interface for cgfoil."""

import argparse
from cgfoil.core.main import run_cgfoil


def main():
    parser = argparse.ArgumentParser(
        description="Mesh inside NACA 0018 airfoil, its offsets as hole, and adjusted line plies with proposed web definition, normal reference, and unique material ids."
    )
    parser.add_argument(
        "-p", "--plot", action="store_true", help="Plot the triangulation"
    )
    parser.add_argument("-v", "--vtk", type=str, help="Output VTK file")
    args = parser.parse_args()

    # Default skins
    skins = {
        "outer_skin": {
            "thickness": np.interp(x, [0.0, 0.9, 1], [0.005, 0.005, 0.002]),
            "material": 2,
            "sort_index": 1,
        },
        "cap": {
            "thickness": np.interp(x, [0.2, 0.2001, 0.5, 0.5001], [0, 0.02, 0.02, 0]),
            "material": 1,
            "sort_index": 2,
        },
        "core": {
            "thickness": np.interp(
                x,
                [0.05, 0.1, 0.2, 0.20001, 0.5, 0.5001, 0.7, 0.9],
                [0, 0.01, 0.01, 0, 0, 0.02, 0.02, 0],
            ),
            "material": 3,
            "sort_index": 3,
        },
        "teud": {
            "thickness": np.interp(
                x,
                [0.7, 0.8, 0.83, 0.93],
                [0, 0.02, 0.02, 0],
            ),
            "material": 3,
            "sort_index": 3,
        },
        "inner_skin": {
            "thickness": np.interp(x, [0.0, 0.9, 1], [0.005, 0.005, 0.002]),
            "material": 2,
            "sort_index": 4,
        },
    }

    # Default web definition
    web_definition = {
        "web1": {
            "points": ((0.25, -0.1), (0.25, 0.1)),
            "plies": [
                {"thickness": 0.004, "material": 4},
                {
                    "thickness": lambda y: np.interp(
                        y, [-0.04, -0.03, 0.03, 0.04], [0, 0.01, 0.01, 0]
                    ),
                    "material": 3,
                },
                {"thickness": 0.004, "material": 4},
            ],
            "normal_ref": [1, 0],
            "n_cell": 20,
        },
        "web2": {
            "points": ((0.4, -0.1), (0.4, 0.1)),
            "plies": [
                {"thickness": 0.01, "material": 4},
                {
                    "thickness": lambda y: np.interp(
                        y, [-0.04, -0.03, 0.03, 0.04], [0, 0.01, 0.01, 0]
                    ),
                    "material": 3,
                },
                {"thickness": 0.01, "material": 4},
            ],
            "normal_ref": [-1, 0],
            "n_cell": 15,
        },
        "web3": {
            "points": ((0.7, -0.1), (0.7, 0.1)),
            "plies": [
                {"thickness": 0.005, "material": 4},
                {
                    "thickness": 0.005,
                    "material": 4,
                },
                {"thickness": 0.005, "material": 4},
            ],
            "normal_ref": [-1, 0],
            "n_cell": 15,
        },
    }

    run_cgfoil(skins, web_definition, plot=args.plot, vtk=args.vtk)

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
    run_cgfoil(plot=args.plot, vtk=args.vtk)

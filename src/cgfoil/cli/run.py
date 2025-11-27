"""Run command functionality."""

from cgfoil.core.main import run_cgfoil
from cgfoil.models import Skin, Thickness, AirfoilMesh


def run_defaults(
    plot: bool = False, vtk: str = None, file: str = "naca0018.dat", split: bool = False
):
    """Run meshing with default skins and no webs."""
    skins = {
        "skin": Skin(
            thickness=Thickness(type="constant", value=0.005), material=1, sort_index=1
        )
    }
    web_definition = {}
    mesh = AirfoilMesh(
        skins=skins,
        webs=web_definition,
        airfoil_input=file,
        plot=plot,
        vtk=vtk,
        split_view=split,
    )
    run_cgfoil(mesh)

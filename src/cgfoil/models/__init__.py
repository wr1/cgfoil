"""Data models for cgfoil inputs and outputs."""

from .airfoil_mesh import AirfoilMesh
from .mesh_result import MeshResult
from .ply import Ply
from .skin import Skin
from .thickness import Thickness
from .web import Web

__all__ = [
    "Thickness",
    "Ply",
    "Web",
    "Skin",
    "AirfoilMesh",
    "MeshResult",
]
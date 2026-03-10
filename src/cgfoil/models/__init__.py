"""Data models for cgfoil inputs and outputs."""

import numpy as np

from .airfoil_mesh import AirfoilMesh
from .mesh_result import MeshResult
from .ply import Ply
from .skin import Skin
from .thickness import Thickness
from .web import Web

__all__ = [
    "AirfoilMesh",
    "MeshResult",
    "Ply",
    "Skin",
    "Thickness",
    "Web",
]

# Rebuild models to resolve forward references
Thickness.model_rebuild()
Ply.model_rebuild()
Web.model_rebuild()
Skin.model_rebuild()
AirfoilMesh.model_rebuild()
MeshResult.model_rebuild()

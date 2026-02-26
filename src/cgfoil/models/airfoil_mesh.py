"""Airfoil mesh configuration model."""

from __future__ import annotations

from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict

from .skin import Skin

from .web import Web


class AirfoilMesh(BaseModel):
    """Model for defining an airfoil mesh."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    skins: dict[str, Skin]
    webs: dict[str, Web]
    airfoil_input: str | list[tuple[float, float]] | np.ndarray = "naca0018.dat"
    n_elem: int | None = None
    plot: bool = False
    vtk: str | None = None
    split_view: bool = False
    plot_filename: str | None = None
    materials: list[dict[str, Any]] | None = None
    scale_factor: float = 1.0
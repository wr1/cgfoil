"""Web model for airfoil structures."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    import numpy as np

    from .ply import Ply


class Web(BaseModel):
    """Model for a web definition."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    points: list[tuple[float, float]] | None = None
    coord_input: str | list[tuple[float, float]] | np.ndarray | None = None
    plies: list[Ply]
    normal_ref: list[float] = [0, 0]
    orientation: list[float] = [0, 1, 0]
    n_elem: int | None = None

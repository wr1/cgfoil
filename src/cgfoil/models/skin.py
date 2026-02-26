"""Skin model for airfoil layers."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from .thickness import Thickness


class Skin(BaseModel):
    """Model for a skin layer."""

    thickness: Thickness
    material: int | str
    sort_index: int

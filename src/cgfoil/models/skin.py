"""Skin model for airfoil layers."""

from pydantic import BaseModel

from .thickness import Thickness


class Skin(BaseModel):
    """Model for a skin layer."""

    thickness: Thickness
    material: int | str
    sort_index: int
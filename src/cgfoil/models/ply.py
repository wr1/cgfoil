"""Ply model for webs."""

from pydantic import BaseModel

from .thickness import Thickness


class Ply(BaseModel):
    """Model for a ply in a web."""

    thickness: Thickness
    material: int | str
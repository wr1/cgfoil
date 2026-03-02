"""Ply model for webs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from .thickness import Thickness


class Ply(BaseModel):
    """Model for a ply in a web."""

    thickness: Thickness
    material: int | str

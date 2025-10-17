"""Pydantic data models for cgfoil inputs."""

from typing import Callable, Union, List, Tuple
from pydantic import BaseModel


class Ply(BaseModel):
    """Model for a ply in a web."""

    thickness: Union[float, Callable[[float], float]]
    material: int


class Web(BaseModel):
    """Model for a web definition."""

    points: Tuple[Tuple[float, float], Tuple[float, float]]
    plies: List[Ply]
    normal_ref: List[float] = [0, 0]
    n_cell: int


class Skin(BaseModel):
    """Model for a skin layer."""

    thickness: Union[float, Callable[[float], float]]
    material: int
    sort_index: int

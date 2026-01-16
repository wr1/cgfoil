"""Pydantic data models for cgfoil inputs."""

from __future__ import annotations

from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict


class Thickness(BaseModel):
    """Model for thickness definitions."""

    type: str
    coord: str = "x"
    value: float | None = None
    x: list[float] | None = None
    y: list[float] | None = None
    conditions: list[dict[str, Any]] | None = None
    else_value: float | None = 0.0
    array: list[float] | None = None

    def compute(self, coords: dict[str, list[float]]) -> list[float]:
        coord_vals = coords[self.coord]
        if self.type == "constant":
            return [self.value] * len(coord_vals)
        if self.type == "interp":
            return np.interp(coord_vals, self.x, self.y).tolist()
        if self.type == "condition":
            result = []
            for i in range(len(coord_vals)):
                satisfied = True
                if self.conditions:
                    for cond in self.conditions:
                        coord_list = coords.get(cond["coord"], [])
                        coord = coord_list[i] if i < len(coord_list) else 0.0
                        min_v, max_v = cond["range"]
                        if not (min_v <= coord <= max_v):
                            satisfied = False
                            break
                result.append(self.value if satisfied else self.else_value)
            return result
        if self.type == "conditions":
            result = []
            for i, ci in enumerate(coord_vals):
                val = self.else_value
                if self.conditions:
                    for cond in self.conditions:
                        if (
                            cond.get("min", -float("inf"))
                            <= ci
                            <= cond.get("max", float("inf"))
                        ):
                            val = cond["value"]
                            break
                result.append(val)
            return result
        if self.type == "array":
            if self.array is None:
                msg = "Array must be provided for thickness type 'array'"
                raise ValueError(msg)
            if len(self.array) != len(coord_vals):
                msg = (
                    f"Array length {len(self.array)} does not match "
                    f"number of points {len(coord_vals)}"
                )
                raise ValueError(
                    msg,
                )
            return self.array
        msg = f"Unknown thickness type: {self.type}"
        raise ValueError(msg)


class Ply(BaseModel):
    """Model for a ply in a web."""

    thickness: Thickness
    material: int | str


class Web(BaseModel):
    """Model for a web definition."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    points: list[tuple[float, float]] | None = None
    coord_input: str | list[tuple[float, float]] | np.ndarray | None = None
    plies: list[Ply]
    normal_ref: list[float] = [0, 0]
    n_elem: int | None = None


class Skin(BaseModel):
    """Model for a skin layer."""

    thickness: Thickness
    material: int | str
    sort_index: int


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


class MeshResult(BaseModel):
    """Model for mesh generation results."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    vertices: list[list[float]]
    faces: list[list[int]]
    outer_points: list[tuple[float, float]]
    inner_list: list[list[tuple[float, float]]]
    line_ply_list: list[list[tuple[float, float]]]
    untrimmed_lines: list[list[tuple[float, float]]]
    web_material_ids: list[int]
    skin_material_ids: list[int]
    web_names: list[str]
    face_normals: list[tuple[float, float]]
    face_material_ids: list[int]
    face_inplanes: list[tuple[float, float]]
    areas: dict[int, float]
    materials: list[dict[str, Any]] | None = None
    skin_ply_thicknesses: list[list[float]]
    web_ply_thicknesses: list[list[float]]

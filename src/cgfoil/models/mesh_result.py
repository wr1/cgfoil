"""Mesh result model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


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

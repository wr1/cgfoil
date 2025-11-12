"""Pydantic data models for cgfoil inputs."""

from typing import Callable, Union, List, Tuple, Dict, Optional, Any
from pydantic import BaseModel, ConfigDict
import numpy as np


class Thickness(BaseModel):
    """Model for thickness definitions."""

    type: str
    coord: str = "x"
    value: Optional[float] = None
    x: Optional[List[float]] = None
    y: Optional[List[float]] = None
    conditions: Optional[List[Dict[str, Any]]] = None
    else_value: Optional[float] = 0.0
    array: Optional[List[float]] = None

    def compute(
        self, x: List[float], ta: List[float], tr: List[float], xr: List[float]
    ) -> List[float]:
        if self.type == "constant":
            coord_vals = {"x": x, "ta": ta, "tr": tr, "xr": xr}[self.coord]
            return [self.value] * len(coord_vals)
        elif self.type == "interp":
            coord_vals = {"x": x, "ta": ta, "tr": tr, "xr": xr}[self.coord]
            return np.interp(coord_vals, self.x, self.y).tolist()
        elif self.type == "condition":
            result = []
            for i in range(len(x)):
                satisfied = True
                if self.conditions:
                    for cond in self.conditions:
                        coord = {"x": x, "ta": ta, "tr": tr, "xr": xr}[cond["coord"]][i]
                        min_v, max_v = cond["range"]
                        if not (min_v <= coord <= max_v):
                            satisfied = False
                            break
                result.append(self.value if satisfied else self.else_value)
            return result
        elif self.type == "conditions":
            coord_vals = {"x": x, "ta": ta, "tr": tr, "xr": xr}[self.coord]
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
        elif self.type == "array":
            if self.array is None:
                raise ValueError("Array must be provided for thickness type 'array'")
            if len(self.array) != len(x):
                raise ValueError(
                    f"Array length {len(self.array)} does not match number of points {len(x)}"
                )
            return self.array
        else:
            raise ValueError(f"Unknown thickness type: {self.type}")


class Ply(BaseModel):
    """Model for a ply in a web."""

    thickness: Union[float, Callable[[float], float]]
    material: Union[int, str]


class Web(BaseModel):
    """Model for a web definition."""

    points: Tuple[Tuple[float, float], Tuple[float, float]]
    plies: List[Ply]
    normal_ref: List[float] = [0, 0]
    n_cell: int


class Skin(BaseModel):
    """Model for a skin layer."""

    thickness: Thickness
    material: Union[int, str]
    sort_index: int


class AirfoilMesh(BaseModel):
    """Model for defining an airfoil mesh."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    skins: Dict[str, Skin]
    webs: Dict[str, Web]
    airfoil_input: Union[str, List[Tuple[float, float]], np.ndarray] = "naca0018.dat"
    n_elem: Optional[int] = 100
    plot: bool = False
    vtk: Optional[str] = None
    split_view: bool = False
    plot_filename: Optional[str] = None
    materials: Optional[List[Dict[str, Any]]] = None
    scale_factor: float = 1.0


class MeshResult(BaseModel):
    """Model for mesh generation results."""

    vertices: List[List[float]]
    faces: List[List[int]]
    outer_points: List[Tuple[float, float]]
    inner_list: List[List[Tuple[float, float]]]
    line_ply_list: List[List[Tuple[float, float]]]
    untrimmed_lines: List[List[Tuple[float, float]]]
    web_material_ids: List[int]
    skin_material_ids: List[int]
    web_names: List[str]
    face_normals: List[Tuple[float, float]]
    face_material_ids: List[int]
    face_inplanes: List[Tuple[float, float]]
    areas: Dict[int, float]
    materials: Optional[List[Dict[str, Any]]] = None

"""ANBA data building utilities."""

import math


def build_anba_data(mesh_result, matdb=None):
    """Build ANBA data dict from mesh_result."""
    points = [[p[0], p[1]] for p in mesh_result.vertices]  # Remove z
    cells = [face[1:] for face in mesh_result.faces]  # Remove the 3
    degree = 2
    if matdb:
        matlibrary = []
        max_id = max(mat["id"] for mat in matdb.values()) if matdb else 0
        for i in range(max_id + 1):
            mat = next((m for m in matdb.values() if m["id"] == i), None)
            if mat:
                if mat["type"] == "orthotropic":
                    matlibrary.append(
                        {
                            "type": "orthotropic",
                            "E1": mat["E1"],
                            "E2": mat["E2"],
                            "E3": mat["E3"],
                            "G12": mat["G12"],
                            "G13": mat["G13"],
                            "G23": mat["G23"],
                            "nu12": mat["nu12"],
                            "nu13": mat["nu13"],
                            "nu23": mat["nu23"],
                            "rho": mat["rho"],
                        }
                    )
                elif mat["type"] == "isotropic":
                    matlibrary.append(
                        {
                            "type": "isotropic",
                            "E": mat["E"],
                            "nu": mat["nu"],
                            "rho": mat["rho"],
                        }
                    )
            else:
                # Default isotropic if missing
                matlibrary.append(
                    {
                        "type": "isotropic",
                        "E": 98000000.0,
                        "nu": 0.3,
                        "rho": 7850.0,
                    }
                )
    else:
        unique_materials = sorted(set(mesh_result.face_material_ids))
        max_id = max(unique_materials) if unique_materials else 0
        matlibrary = [
            {
                "type": "isotropic",
                "E": 98000000.0,
                "nu": 0.3,
                "rho": 7850.0,
            }
            for _ in range(max_id + 1)
        ]
    material_ids = mesh_result.face_material_ids
    fiber_orientations = [0.0] * len(cells)
    plane_orientations = []
    for ix, iy in mesh_result.face_inplanes:
        angle = math.degrees(math.atan2(iy, ix))
        angle = (angle + 90) % 180 - 90
        plane_orientations.append(angle)
    scaling_constraint = 1.0
    singular = False
    data = {
        "points": points,
        "cells": cells,
        "degree": degree,
        "mat_library": matlibrary,
        "material_ids": material_ids,
        "fiber_orientations": fiber_orientations,
        "plane_orientations": plane_orientations,
        "scaling_constraint": scaling_constraint,
        "singular": singular,
    }
    return data

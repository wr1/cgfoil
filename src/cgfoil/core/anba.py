"""ANBA data building utilities."""

import math


def build_anba_data(mesh_result):
    """Build ANBA data dict from mesh_result."""
    points = [[p[0], p[1]] for p in mesh_result.vertices]  # Remove z
    cells = [face[1:] for face in mesh_result.faces]  # Remove the 3
    degree = 2
    if mesh_result.materials:
        matlibrary = []
        for mat in mesh_result.materials:
            if mat["type"] == "orthotropic":
                matlibrary.append(
                    {
                        "type": "orthotropic",
                        "e_xx": mat["e_xx"],
                        "e_yy": mat["e_yy"],
                        "e_zz": mat["e_zz"],
                        "g_xy": mat["g_xy"],
                        "g_xz": mat["g_xz"],
                        "g_yz": mat["g_yz"],
                        "nu_xy": mat["nu_xy"],
                        "nu_zx": mat["nu_zx"],
                        "nu_zy": mat["nu_zy"],
                        "rho": mat["rho"],
                    }
                )
            elif mat["type"] == "isotropic":
                matlibrary.append(
                    {
                        "type": "isotropic",
                        "e": mat["e"],
                        "nu": mat["nu"],
                        "rho": mat["rho"],
                    }
                )
    else:
        unique_materials = sorted(set(mesh_result.face_material_ids))
        max_id = max(unique_materials) if unique_materials else 0
        matlibrary = [
            {
                "type": "isotropic",
                "e": 98000000.0,
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
        "mesh": {
            "points": points,
            "cells": cells,
        },
        "degree": degree,
        "matlibrary": matlibrary,
        "materials": material_ids,
        "fiber_orientations": fiber_orientations,
        "plane_orientations": plane_orientations,
        "scaling_constraint": scaling_constraint,
        "singular": singular,
    }
    return data

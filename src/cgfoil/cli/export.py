"""Export command functionalities."""

import pickle
import json
import math
import os
from cgfoil.utils.logger import logger


def export_mesh_to_vtk(mesh_file: str, vtk_file: str):
    """Export mesh to VTK file."""
    with open(mesh_file, "rb") as f:
        mesh_result = pickle.load(f)
    try:
        import pyvista as pv
        import numpy as np
    except ImportError:
        print("pyvista not available")
        return
    mesh_obj = pv.UnstructuredGrid(
        mesh_result.faces,
        [pv.CellType.TRIANGLE] * len(mesh_result.faces),
        mesh_result.vertices,
    )
    mesh_obj.cell_data["material_id"] = mesh_result.face_material_ids
    mesh_obj.cell_data["normals"] = np.array(
        [[n[0], n[1], 0.0] for n in mesh_result.face_normals]
    )
    mesh_obj.cell_data["inplane"] = np.array(
        [[i[0], i[1], 0.0] for i in mesh_result.face_inplanes]
    )
    plane_orientations = []
    for ix, iy in mesh_result.face_inplanes:
        angle = math.degrees(math.atan2(iy, ix))
        angle = (angle + 90) % 180 - 90
        plane_orientations.append(angle)
    mesh_obj.cell_data["plane_orientations"] = plane_orientations
    # Add offset normals (inward for skins)
    mesh_obj.cell_data["offset_normals"] = np.array(
        [[-n[0], -n[1], 0.0] for n in mesh_result.face_normals]
    )
    mesh_obj.save(vtk_file)
    logger.info(f"Mesh exported to {vtk_file}")


def export_mesh_to_anba(mesh_file: str, anba_file: str):
    """Export mesh to ANBA format (JSON)."""
    with open(mesh_file, "rb") as f:
        mesh_result = pickle.load(f)
    # Create serializable data
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
    with open(anba_file, "w") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Mesh exported to {anba_file}")

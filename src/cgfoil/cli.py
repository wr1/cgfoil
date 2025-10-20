"""Command line interface for cgfoil."""

import pickle
import yaml
import json
import sys
import math
from pathlib import Path
import pandas as pd
from treeparse import cli, command, argument, option, group
from cgfoil.core.main import run_cgfoil, generate_mesh, plot_mesh
from cgfoil.models import AirfoilMesh
from cgfoil.utils.logger import logger


def mesh_from_yaml(yaml_file: str, output_mesh: str = None):
    """Generate mesh from YAML file."""
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)
    mesh = AirfoilMesh(**data)
    try:
        mesh_result = generate_mesh(mesh)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    if output_mesh:
        with open(output_mesh, "wb") as f:
            pickle.dump(mesh_result, f)
        logger.info(f"Mesh saved to {output_mesh}")
    return mesh_result


def plot_existing_mesh(mesh_file: str, plot_filename: str = None, split: bool = False):
    """Plot an existing mesh from file."""
    with open(mesh_file, "rb") as f:
        mesh_result = pickle.load(f)
    plot_mesh(mesh_result, plot_filename, split)


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
    plane_orientations = [math.atan2(iy, ix) for ix, iy in mesh_result.face_inplanes]
    mesh_obj.cell_data["plane_orientations"] = plane_orientations
    mesh_obj.save(vtk_file)
    logger.info(f"Mesh exported to {vtk_file}")


def export_mesh_to_anba(mesh_file: str, anba_file: str):
    """Export mesh to ANBA format (JSON)."""
    with open(mesh_file, "rb") as f:
        mesh_result = pickle.load(f)
    # Create serializable data
    points = mesh_result.vertices
    cells = [face[1:] for face in mesh_result.faces]  # Remove the 3
    degree = 2
    if mesh_result.materials:
        mat_library = mesh_result.materials
    else:
        unique_materials = sorted(set(mesh_result.face_material_ids))
        max_id = max(unique_materials) if unique_materials else 0
        mat_library = [
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
    plane_orientations = [math.atan2(iy, ix) for ix, iy in mesh_result.face_inplanes]
    scaling_constraint = 1.0
    singular = False
    data = {
        "points": points,
        "cells": cells,
        "degree": degree,
        "mat_library": mat_library,
        "material_ids": material_ids,
        "fiber_orientations": fiber_orientations,
        "plane_orientations": plane_orientations,
        "scaling_constraint": scaling_constraint,
        "singular": singular,
    }
    with open(anba_file, "w") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Mesh exported to {anba_file}")


def summarize_mesh(mesh_file: str, output: str = None):
    """Summarize areas and masses from mesh file."""
    with open(mesh_file, "rb") as f:
        mesh_result = pickle.load(f)
    rows = []
    total_mass = 0.0
    for mat_id, area in sorted(mesh_result.areas.items()):
        if mesh_result.materials and mat_id < len(mesh_result.materials):
            name = mesh_result.materials[mat_id].get("name", "N/A")
            rho = mesh_result.materials[mat_id]["rho"]
            mass = area * rho
            total_mass += mass
        else:
            name = "N/A"
            mass = float('nan')
        rows.append({
            "Material ID": mat_id,
            "Material Name": name,
            "Area": area,
            "Mass/m": mass,
        })
    if mesh_result.materials:
        rows.append({
            "Material ID": "Total",
            "Material Name": "",
            "Area": "",
            "Mass/m": total_mass,
        })
    df = pd.DataFrame(rows)
    if output:
        df.to_csv(output, index=False)
        logger.info(f"Summary saved to {output}")
    print(df.to_string())

app = cli(
    name="cgfoil",
    help="CGAL-based airfoil meshing tool for generating constrained Delaunay triangulations of airfoils with plies and webs.",
    max_width=120,
    show_types=True,
    show_defaults=True,
    line_connect=True,
    theme="monochrome",
)

mesh_cmd = command(
    name="mesh",
    help="Generate mesh from YAML file.",
    callback=mesh_from_yaml,
    arguments=[
        argument(
            name="yaml_file", arg_type=str, help="Path to YAML configuration file"
        ),
    ],
    options=[
        option(
            flags=["--output-mesh", "-o"],
            arg_type=str,
            help="Output mesh file (pickle)",
        ),
    ],
    sort_key=1,
)
app.commands.append(mesh_cmd)

plot_cmd = command(
    name="plot",
    help="Plot an existing mesh.",
    callback=plot_existing_mesh,
    arguments=[
        argument(name="mesh_file", arg_type=str, help="Path to mesh file (pickle)"),
    ],
    options=[
        option(
            flags=["--plot-file", "-f"],
            dest="plot_filename",
            arg_type=str,
            help="Save plot to file",
        ),
        option(
            flags=["--split", "-s"],
            arg_type=bool,
            default=False,
            help="Enable split view plotting",
        ),
    ],
    sort_key=2,
)
app.commands.append(plot_cmd)

export_group = group(name="export", help="Export mesh to various formats.", sort_key=3)
app.subgroups.append(export_group)

vtk_cmd = command(
    name="vtk",
    help="Export mesh to VTK file.",
    callback=export_mesh_to_vtk,
    arguments=[
        argument(name="mesh_file", arg_type=str, help="Path to mesh file (pickle)"),
        argument(name="vtk_file", arg_type=str, help="Output VTK file"),
    ],
)
export_group.commands.append(vtk_cmd)

anba_cmd = command(
    name="anba",
    help="Export mesh to ANBA format (JSON).",
    callback=export_mesh_to_anba,
    arguments=[
        argument(name="mesh_file", arg_type=str, help="Path to mesh file (pickle)"),
        argument(name="anba_file", arg_type=str, help="Output ANBA file"),
    ],
)
export_group.commands.append(anba_cmd)

summary_cmd = command(
    name="summary",
    help="Summarize areas and masses from mesh file.",
    callback=summarize_mesh,
    arguments=[
        argument(name="mesh_file", arg_type=str, help="Path to mesh file (pickle)"),
    ],
    options=[
        option(
            flags=["--output", "-o"],
            arg_type=str,
            help="Output CSV file",
        ),
    ],
)
export_group.commands.append(summary_cmd)


def main():
    app.run()
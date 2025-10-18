"""Command line interface for cgfoil."""

import pickle
import yaml
import json
from pathlib import Path
from treeparse import cli, command, argument, option, group
from cgfoil.core.main import run_cgfoil, generate_mesh, plot_mesh
from cgfoil.models import AirfoilMesh


def mesh_from_yaml(yaml_file: str, output_mesh: str = None):
    """Generate mesh from YAML file."""
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)
    mesh = AirfoilMesh(**data)
    mesh_result = generate_mesh(mesh)
    if output_mesh:
        with open(output_mesh, "wb") as f:
            pickle.dump(mesh_result, f)
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
    mesh_obj.save(vtk_file)
    print(f"Mesh exported to {vtk_file}")


def export_mesh_to_anba(mesh_file: str, anba_file: str):
    """Export mesh to ANBA format (JSON)."""
    with open(mesh_file, "rb") as f:
        mesh_result = pickle.load(f)
    # Create serializable data
    points = mesh_result.vertices
    cells = [face[1:] for face in mesh_result.faces]  # Remove the 3
    degree = 2
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
    plane_orientations = [0.0] * len(cells)
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
    print(f"Mesh exported to {anba_file}")


def run_mesh(
    plot: bool = False,
    vtk: str = None,
    file: str = "naca0018.dat",
    split: bool = False,
    plot_file: str = None,
):
    # Default skins
    skins = {
        "outer_skin": {
            "thickness": {"type": "constant", "value": 0.005},
            "material": 2,
            "sort_index": 1,
        },
        "inner_skin": {
            "thickness": {"type": "constant", "value": 0.005},
            "material": 2,
            "sort_index": 2,
        },
    }
    webs = {}
    mesh = AirfoilMesh(
        skins=skins,
        webs=webs,
        airfoil_filename=file,
        plot=plot,
        vtk=vtk,
        split_view=split,
        plot_filename=plot_file,
    )
    run_cgfoil(mesh)


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
            flags=["--plot-file"],
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
)
app.commands.append(plot_cmd)

export_group = group(name="export", help="Export mesh to various formats.")
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

run_cmd = command(
    name="run",
    help="Run meshing with defaults.",
    callback=run_mesh,
    options=[
        option(
            flags=["--plot", "-p"],
            arg_type=bool,
            default=False,
            help="Plot the triangulation",
        ),
        option(
            flags=["--vtk", "-v"],
            arg_type=str,
            help="Output VTK file",
        ),
        option(
            flags=["--file", "-f"],
            arg_type=str,
            default="naca0018.dat",
            help="Path to airfoil data file (.dat)",
        ),
        option(
            flags=["--split", "-s"],
            arg_type=bool,
            default=False,
            help="Enable split view plotting",
        ),
        option(
            flags=["--plot-file"],
            arg_type=str,
            help="Save plot to file",
        ),
    ],
)
app.commands.append(run_cmd)


def main():
    app.run()
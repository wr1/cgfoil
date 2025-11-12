"""Export tests for cgfoil."""

import os
import tempfile
from pathlib import Path
import yaml
import pytest
import json
from unittest.mock import patch
from CGAL.CGAL_Kernel import Point_2
from CGAL.CGAL_Mesh_2 import Mesh_2_Constrained_Delaunay_triangulation_2
from cgfoil.models import AirfoilMesh
from cgfoil.core.main import generate_mesh
from cgfoil.cli.cli import export_mesh_to_vtk, export_mesh_to_anba, summarize_mesh
from cgfoil.utils.plot import plot_triangulation

@pytest.fixture

def mesh_result_fixture():
    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_file = Path(__file__).parent / "airfoil_mesh.yaml"
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        mesh = AirfoilMesh(**data)
        mesh.airfoil_input = str(Path(__file__).parent / "naca0018.dat")
        mesh_result = generate_mesh(mesh)
        # Save to pickle
        import pickle
        mesh_file = os.path.join(tmpdir, "mesh.pck")
        with open(mesh_file, "wb") as f:
            pickle.dump(mesh_result, f)
        yield tmpdir, mesh_result


def test_export_vtk(mesh_result_fixture):
    tmpdir, mesh_result = mesh_result_fixture
    vtk_file = os.path.join(tmpdir, "test.vtk")
    export_mesh_to_vtk(os.path.join(tmpdir, "mesh.pck"), vtk_file)
    assert os.path.exists(vtk_file)


def test_export_vtk_loadable(mesh_result_fixture):
    tmpdir, mesh_result = mesh_result_fixture
    vtk_file = os.path.join(tmpdir, "test.vtk")
    export_mesh_to_vtk(os.path.join(tmpdir, "mesh.pck"), vtk_file)
    import pyvista as pv
    mesh = pv.read(vtk_file)
    assert "material_id" in mesh.cell_data
    assert "normals" in mesh.cell_data
    assert "inplane" in mesh.cell_data
    assert "plane_orientations" in mesh.cell_data
    assert len(mesh.cell_data["material_id"]) == len(mesh_result.face_material_ids)


def test_export_anba(mesh_result_fixture):
    tmpdir, mesh_result = mesh_result_fixture
    anba_file = os.path.join(tmpdir, "test.json")
    export_mesh_to_anba(os.path.join(tmpdir, "mesh.pck"), anba_file)
    assert os.path.exists(anba_file)


def test_export_anba_fields(mesh_result_fixture):
    tmpdir, mesh_result = mesh_result_fixture
    anba_file = os.path.join(tmpdir, "test.json")
    export_mesh_to_anba(os.path.join(tmpdir, "mesh.pck"), anba_file)
    with open(anba_file) as f:
        data = json.load(f)
    assert "mesh" in data
    assert "points" in data["mesh"]
    assert "cells" in data["mesh"]
    assert "degree" in data
    assert "matlibrary" in data
    assert "materials" in data
    assert "fiber_orientations" in data
    assert "plane_orientations" in data
    assert "scaling_constraint" in data
    assert "singular" in data
    n_cells = len(data["mesh"]["cells"])
    assert len(data["materials"]) == n_cells
    assert len(data["fiber_orientations"]) == n_cells
    assert len(data["plane_orientations"]) == n_cells
    assert len(data["mesh"]["points"]) == len(mesh_result.vertices)
    # Check that points are 2D
    for p in data["mesh"]["points"]:
        assert len(p) == 2
    # Check material library fields
    for mat in data["matlibrary"]:
        if mat["type"] == "orthotropic":
            required_keys = ["type", "e_xx", "e_yy", "e_zz", "g_xy", "g_xz", "g_yz", "nu_xy", "nu_zx", "nu_zy", "rho"]
            assert all(key in mat for key in required_keys)
        elif mat["type"] == "isotropic":
            required_keys = ["type", "e", "nu", "rho"]
            assert all(key in mat for key in required_keys)


def test_export_summary(mesh_result_fixture):
    tmpdir, mesh_result = mesh_result_fixture
    summary_file = os.path.join(tmpdir, "summary.csv")
    summarize_mesh(os.path.join(tmpdir, "mesh.pck"), output=summary_file)
    assert os.path.exists(summary_file)
    with open(summary_file) as f:
        content = f.read()
    assert "Total" in content


def test_plot_triangulation_to_file(tmp_path):
    cdt = Mesh_2_Constrained_Delaunay_triangulation_2()
    cdt.insert_constraint(Point_2(0, 0), Point_2(1, 0))
    cdt.insert_constraint(Point_2(1, 0), Point_2(0.5, 1))
    cdt.insert_constraint(Point_2(0.5, 1), Point_2(0, 0))
    outer_points = [Point_2(0, 0), Point_2(1, 0), Point_2(0.5, 1)]
    inner_list = []
    line_ply_list = []
    untrimmed_lines = []
    web_material_ids = []
    skin_material_ids = [0]
    web_names = []
    face_normals = [(0, 1)] * cdt.number_of_faces()
    face_material_ids = [0] * cdt.number_of_faces()
    face_inplanes = [(1, 0)] * cdt.number_of_faces()
    # Compute vertices and faces
    vertices = []
    vertex_map = {}
    idx = 0
    for v in cdt.finite_vertices():
        vertex_map[v] = idx
        vertices.append([v.point().x(), v.point().y(), 0.0])
        idx += 1
    faces = []
    for face in cdt.finite_faces():
        v0 = vertex_map[face.vertex(0)]
        v1 = vertex_map[face.vertex(1)]
        v2 = vertex_map[face.vertex(2)]
        faces.append([3, v0, v1, v2])
    plot_filename = tmp_path / "test.png"
    plot_triangulation(
        vertices,
        faces,
        outer_points,
        inner_list,
        line_ply_list,
        untrimmed_lines,
        web_material_ids,
        skin_material_ids,
        web_names,
        face_normals,
        face_material_ids,
        face_inplanes,
        split_view=False,
        plot_filename=str(plot_filename),
    )
    assert plot_filename.exists()
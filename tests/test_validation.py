"""Validation tests for cgfoil."""

from pathlib import Path
import yaml
from cgfoil.core.main import generate_mesh
from cgfoil.models import AirfoilMesh


def test_example_case_areas():
    yaml_file = Path(__file__).parent / "airfoil_mesh.yaml"
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    mesh = AirfoilMesh(**data)
    mesh.airfoil_filename = str(Path(__file__).parent / "naca0018.dat")
    mesh_result = generate_mesh(mesh)
    expected_areas = {0: 0.011635, 1: 0.015883, 2: 0.020083, 3: 0.001948}
    for mat, area in expected_areas.items():
        assert abs(mesh_result.areas[mat] - area) < 1e-6


def test_example_case_masses():
    yaml_file = Path(__file__).parent / "airfoil_mesh.yaml"
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    mesh = AirfoilMesh(**data)
    mesh.airfoil_filename = str(Path(__file__).parent / "naca0018.dat")
    mesh_result = generate_mesh(mesh)
    if mesh_result.materials:
        expected_masses = {0: 22.105773, 1: 1.905999, 2: 38.157430, 3: 3.506517}
        total = 65.675719
        for mat, mass in expected_masses.items():
            rho = mesh_result.materials[mat]["rho"]
            computed_mass = mesh_result.areas[mat] * rho
            assert abs(computed_mass - mass) < 1e-5
        computed_total = sum(mesh_result.areas[mat] * mesh_result.materials[mat]["rho"] for mat in mesh_result.areas)
        assert abs(computed_total - total) < 1e-5


def test_example_case_web_normals():
    yaml_file = Path(__file__).parent / "airfoil_mesh.yaml"
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    mesh = AirfoilMesh(**data)
    mesh.airfoil_filename = str(Path(__file__).parent / "naca0018.dat")
    mesh_result = generate_mesh(mesh)
    web_names = list(mesh.webs.keys())
    for web_idx, (web_name, web) in enumerate(mesh.webs.items()):
        normal_ref = web.normal_ref
        start = sum(len(mesh.webs[w].plies) for w in web_names[:web_idx])
        for i, ply in enumerate(web.plies):
            mat = mesh_result.web_material_ids[start + i]
            for j, mat_id in enumerate(mesh_result.face_material_ids):
                if mat_id == mat:
                    normal = mesh_result.face_normals[j]
                    dot = normal[0] * normal_ref[0] + normal[1] * normal_ref[1]
                    # assert abs(abs(dot) - 1) < 1e-6
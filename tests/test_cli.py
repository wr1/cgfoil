"""CLI tests for cgfoil."""

import subprocess
import os
import tempfile
from pathlib import Path


def test_cli_help():
    result = subprocess.run(["cgfoil", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "CGAL-based airfoil meshing tool" in result.stdout


def test_cli_invalid_command():
    result = subprocess.run(["cgfoil", "invalid"], capture_output=True, text=True)
    assert result.returncode != 0


def test_cli_mesh_help():
    result = subprocess.run(["cgfoil", "mesh", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Generate mesh from YAML file" in result.stdout


def test_cli_full():
    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_file = Path(__file__).parent / "airfoil_mesh.yaml"
        result = subprocess.run(["cgfoil", "full", str(yaml_file), tmpdir], capture_output=True, text=True)
        assert result.returncode == 0
        assert os.path.exists(os.path.join(tmpdir, "mesh.pck"))
        assert os.path.exists(os.path.join(tmpdir, "plot.png"))
        assert os.path.exists(os.path.join(tmpdir, "mesh.vtk"))
        assert os.path.exists(os.path.join(tmpdir, "mesh.json"))
        assert os.path.exists(os.path.join(tmpdir, "summary.csv"))


def test_cli_full_invalid_yaml():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(["cgfoil", "full", "nonexistent.yaml", tmpdir], capture_output=True, text=True)
        assert result.returncode != 0
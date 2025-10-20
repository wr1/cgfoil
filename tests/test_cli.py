"""CLI tests for cgfoil."""

import subprocess
import os
import tempfile
import shutil
from pathlib import Path
import yaml


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
        # Copy and modify yaml
        yaml_src = Path(__file__).parent / "airfoil_mesh.yaml"
        yaml_dst = Path(tmpdir) / "airfoil_mesh.yaml"
        shutil.copy(yaml_src, yaml_dst)
        with open(yaml_dst, 'r') as f:
            data = yaml.safe_load(f)
        data['airfoil_filename'] = str(Path(tmpdir) / "naca0018.dat")
        with open(yaml_dst, 'w') as f:
            yaml.dump(data, f)
        # Copy naca
        naca_src = Path(__file__).parent / "naca0018.dat"
        naca_dst = Path(tmpdir) / "naca0018.dat"
        shutil.copy(naca_src, naca_dst)
        result = subprocess.run(["cgfoil", "full", str(yaml_dst), tmpdir], capture_output=True, text=True)
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
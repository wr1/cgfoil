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


def test_cli_mesh():
    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_src = Path(__file__).parent / "airfoil_mesh.yaml"
        yaml_dst = Path(tmpdir) / "test.yaml"
        shutil.copy(yaml_src, yaml_dst)
        with open(yaml_dst, 'r') as f:
            data = yaml.safe_load(f)
        data['airfoil_filename'] = str(Path(tmpdir) / "naca0018.dat")
        with open(yaml_dst, 'w') as f:
            yaml.dump(data, f)
        naca_src = Path(__file__).parent / "naca0018.dat"
        naca_dst = Path(tmpdir) / "naca0018.dat"
        shutil.copy(naca_src, naca_dst)
        out_file = Path(tmpdir) / "mesh.pkl"
        result = subprocess.run(["cgfoil", "mesh", str(yaml_dst), "-o", str(out_file)], capture_output=True, text=True)
        assert result.returncode == 0
        assert out_file.exists()


def test_cli_plot():
    with tempfile.TemporaryDirectory() as tmpdir:
        # First create mesh
        yaml_src = Path(__file__).parent / "airfoil_mesh.yaml"
        yaml_dst = Path(tmpdir) / "test.yaml"
        shutil.copy(yaml_src, yaml_dst)
        with open(yaml_dst, 'r') as f:
            data = yaml.safe_load(f)
        data['airfoil_filename'] = str(Path(tmpdir) / "naca0018.dat")
        with open(yaml_dst, 'w') as f:
            yaml.dump(data, f)
        naca_src = Path(__file__).parent / "naca0018.dat"
        naca_dst = Path(tmpdir) / "naca0018.dat"
        shutil.copy(naca_src, naca_dst)
        mesh_file = Path(tmpdir) / "mesh.pkl"
        result_mesh = subprocess.run(["cgfoil", "mesh", str(yaml_dst), "-o", str(mesh_file)], capture_output=True, text=True)
        assert result_mesh.returncode == 0
        # Now plot
        plot_file = Path(tmpdir) / "plot.png"
        result_plot = subprocess.run(["cgfoil", "plot", str(mesh_file), "-f", str(plot_file)], capture_output=True, text=True)
        assert result_plot.returncode == 0
        assert plot_file.exists()


def test_cli_export_vtk():
    with tempfile.TemporaryDirectory() as tmpdir:
        # First create mesh
        yaml_src = Path(__file__).parent / "airfoil_mesh.yaml"
        yaml_dst = Path(tmpdir) / "test.yaml"
        shutil.copy(yaml_src, yaml_dst)
        with open(yaml_dst, 'r') as f:
            data = yaml.safe_load(f)
        data['airfoil_filename'] = str(Path(tmpdir) / "naca0018.dat")
        with open(yaml_dst, 'w') as f:
            yaml.dump(data, f)
        naca_src = Path(__file__).parent / "naca0018.dat"
        naca_dst = Path(tmpdir) / "naca0018.dat"
        shutil.copy(naca_src, naca_dst)
        mesh_file = Path(tmpdir) / "mesh.pkl"
        result_mesh = subprocess.run(["cgfoil", "mesh", str(yaml_dst), "-o", str(mesh_file)], capture_output=True, text=True)
        assert result_mesh.returncode == 0
        # Now export VTK
        vtk_file = Path(tmpdir) / "mesh.vtk"
        result_export = subprocess.run(["cgfoil", "export", "vtk", str(mesh_file), str(vtk_file)], capture_output=True, text=True)
        assert result_export.returncode == 0
        assert vtk_file.exists()


def test_cli_export_anba():
    with tempfile.TemporaryDirectory() as tmpdir:
        # First create mesh
        yaml_src = Path(__file__).parent / "airfoil_mesh.yaml"
        yaml_dst = Path(tmpdir) / "test.yaml"
        shutil.copy(yaml_src, yaml_dst)
        with open(yaml_dst, 'r') as f:
            data = yaml.safe_load(f)
        data['airfoil_filename'] = str(Path(tmpdir) / "naca0018.dat")
        with open(yaml_dst, 'w') as f:
            yaml.dump(data, f)
        naca_src = Path(__file__).parent / "naca0018.dat"
        naca_dst = Path(tmpdir) / "naca0018.dat"
        shutil.copy(naca_src, naca_dst)
        mesh_file = Path(tmpdir) / "mesh.pkl"
        result_mesh = subprocess.run(["cgfoil", "mesh", str(yaml_dst), "-o", str(mesh_file)], capture_output=True, text=True)
        assert result_mesh.returncode == 0
        # Now export ANBA
        anba_file = Path(tmpdir) / "mesh.json"
        result_export = subprocess.run(["cgfoil", "export", "anba", str(mesh_file), str(anba_file)], capture_output=True, text=True)
        assert result_export.returncode == 0
        assert anba_file.exists()


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
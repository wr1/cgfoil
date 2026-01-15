"""Tests for VTK export functionality."""

from unittest.mock import MagicMock, patch

import pytest

from cgfoil.core.vtk import build_vtk_mesh
from cgfoil.models import MeshResult


def test_build_vtk_mesh_without_mesh():
    """Test building VTK mesh without mesh object."""
    mesh_result = MeshResult(
        vertices=[[0, 0, 0], [1, 0, 0], [0, 1, 0]],
        faces=[[3, 0, 1, 2]],
        outer_points=[(0, 0), (1, 0), (0, 1)],
        inner_list=[],
        line_ply_list=[],
        untrimmed_lines=[],
        web_material_ids=[],
        skin_material_ids=[1],
        web_names=[],
        face_normals=[(0, 0)],
        face_material_ids=[1],
        face_inplanes=[(0, 0)],
        areas={1: 0.5},
        materials=None,
        skin_ply_thicknesses=[],
        web_ply_thicknesses=[],
    )
    vtk_mesh = build_vtk_mesh(mesh_result)
    assert vtk_mesh.n_cells == 1
    assert vtk_mesh.n_points == 3
    assert "material_id" in vtk_mesh.cell_data
    assert "normals" in vtk_mesh.cell_data
    assert "inplane" in vtk_mesh.cell_data
    assert "plane_orientations" in vtk_mesh.cell_data
    assert "offset_normals" in vtk_mesh.cell_data
    assert "Area" in vtk_mesh.cell_data


def test_build_vtk_mesh_with_mesh():
    """Test build_vtk_mesh with mesh (includes ply thicknesses)."""
    # Mock mesh_result
    mesh_result = MagicMock()
    mesh_result.faces = [[3, 0, 1, 2]]
    mesh_result.vertices = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
    mesh_result.face_material_ids = [0]
    mesh_result.face_normals = [(0, 1)]
    mesh_result.face_inplanes = [(1, 0)]
    mesh_result.skin_ply_thicknesses = [[0.1, 0.2, 0.3]]
    mesh_result.web_ply_thicknesses = [[0.4, 0.5]]
    mesh_result.skin_material_ids = [0]
    mesh_result.web_material_ids = [1]
    mesh_result.outer_points = [(0, 0), (1, 0), (0, 1)]
    mesh_result.untrimmed_lines = [[(0.5, 0), (0.5, 1)]]

    # Mock mesh
    mesh = MagicMock()
    mesh.webs = {"web1": MagicMock(plies=[MagicMock()])}

    mock_pv = MagicMock()
    mock_np = MagicMock()
    mock_np.array.return_value.flatten.return_value = [3, 0, 1, 2]
    mock_pv.CellType.TRIANGLE = "triangle"
    mock_mesh_obj = MagicMock()
    mock_pv.UnstructuredGrid.return_value = mock_mesh_obj
    mock_mesh_obj.cell_data = {}
    mock_mesh_obj.compute_cell_sizes.return_value = mock_mesh_obj

    with patch.dict("sys.modules", {"pyvista": mock_pv, "numpy": mock_np}):
        result = build_vtk_mesh(mesh_result, mesh)

        assert result is mock_mesh_obj
        assert "material_id" in mock_mesh_obj.cell_data
        assert "normals" in mock_mesh_obj.cell_data
        assert "inplane" in mock_mesh_obj.cell_data
        assert "plane_orientations" in mock_mesh_obj.cell_data
        assert "offset_normals" in mock_mesh_obj.cell_data


def test_build_vtk_mesh_pyvista_not_available():
    """Test that ImportError is raised when pyvista is not available."""

    def mock_import(name, *args, **kwargs):
        if name == "pyvista":
            msg = "No module named 'pyvista'"
            raise ImportError(msg)
        return __import__(name, *args, **kwargs)

    with patch("builtins.__import__", mock_import):
        with pytest.raises(ImportError, match="pyvista not available"):
            mesh_result = MeshResult(
                vertices=[[0, 0, 0], [1, 0, 0], [0, 1, 0]],
                faces=[[3, 0, 1, 2]],
                outer_points=[(0, 0), (1, 0), (0, 1)],
                inner_list=[],
                line_ply_list=[],
                untrimmed_lines=[],
                web_material_ids=[],
                skin_material_ids=[1],
                web_names=[],
                face_normals=[(0, 0)],
                face_material_ids=[1],
                face_inplanes=[(0, 0)],
                areas={1: 0.5},
                materials=None,
                skin_ply_thicknesses=[],
                web_ply_thicknesses=[],
            )
            build_vtk_mesh(mesh_result)

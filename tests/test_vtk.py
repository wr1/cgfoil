"""Tests for vtk.py."""

import pytest
from unittest.mock import MagicMock, patch
from cgfoil.core.vtk import build_vtk_mesh


def test_build_vtk_mesh_without_mesh():
    """Test build_vtk_mesh without mesh (no ply thicknesses)."""
    # Mock mesh_result
    mesh_result = MagicMock()
    mesh_result.faces = [[3, 0, 1, 2], [3, 1, 2, 3]]
    mesh_result.vertices = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]]
    mesh_result.face_material_ids = [0, 1]
    mesh_result.face_normals = [(0, 1), (1, 0)]
    mesh_result.face_inplanes = [(1, 0), (0, 1)]

    mock_pv = MagicMock()
    mock_np = MagicMock()
    mock_np.array.return_value.flatten.return_value = [3, 0, 1, 2, 3, 1, 2, 3]
    mock_pv.CellType.TRIANGLE = "triangle"
    mock_mesh_obj = MagicMock()
    mock_pv.UnstructuredGrid.return_value = mock_mesh_obj
    mock_mesh_obj.cell_data = {}

    with patch.dict("sys.modules", {"pyvista": mock_pv, "numpy": mock_np}):
        result = build_vtk_mesh(mesh_result)

        mock_pv.UnstructuredGrid.assert_called_once_with(
            [3, 0, 1, 2, 3, 1, 2, 3],
            ["triangle", "triangle"],
            [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]],
        )
        assert mock_mesh_obj.cell_data["material_id"] == [0, 1]
        assert "ply_0_thickness" not in mock_mesh_obj.cell_data
        assert result == mock_mesh_obj


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

    with patch.dict("sys.modules", {"pyvista": mock_pv, "numpy": mock_np}):
        result = build_vtk_mesh(mesh_result, mesh)

        assert "ply_0_thickness" in mock_mesh_obj.cell_data
        assert result == mock_mesh_obj


def test_build_vtk_mesh_pyvista_not_available():
    """Test build_vtk_mesh raises ImportError if pyvista not available."""
    mesh_result = MagicMock()

    def mock_import(name, *args, **kwargs):
        if name == "pyvista":
            raise ImportError("pyvista not available")
        return __import__(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mock_import):
        with pytest.raises(ImportError, match="pyvista not available"):
            build_vtk_mesh(mesh_result)

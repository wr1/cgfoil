"""Tests for VTK utilities."""

import builtins
from unittest.mock import patch

import pytest

from cgfoil.core.vtk import build_vtk_mesh
from cgfoil.models import MeshResult


def test_build_vtk_mesh_without_mesh():
    """Test building VTK mesh without optional mesh argument."""
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
    assert vtk_mesh.n_points == 3
    assert vtk_mesh.n_cells == 1


def test_build_vtk_mesh_with_mesh():
    """Test building VTK mesh with optional mesh argument."""
    from cgfoil.models import AirfoilMesh, Skin, Thickness

    mesh = AirfoilMesh(
        skins={
            "skin": Skin(
                thickness=Thickness(type="constant", value=0.005),
                material=1,
                sort_index=1,
            )
        },
        webs={},
        airfoil_input=[(0, 0), (1, 0), (0, 1)],
    )
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
    vtk_mesh = build_vtk_mesh(mesh_result, mesh)
    assert vtk_mesh.n_points == 3
    assert vtk_mesh.n_cells == 1


def test_build_vtk_mesh_pyvista_not_available():
    """Test that ImportError is raised when pyvista is not available."""
    original_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "pyvista":
            msg = "No module named 'pyvista'"
            raise ImportError(msg)
        return original_import(name, *args, **kwargs)

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

"""Basic tests for cgfoil."""

import pytest
import tempfile
from unittest.mock import patch
from pathlib import Path
import yaml
from CGAL.CGAL_Kernel import Point_2
from CGAL.CGAL_Mesh_2 import Mesh_2_Constrained_Delaunay_triangulation_2
from cgfoil.core.main import run_cgfoil
from cgfoil.core.mesh import create_line_mesh
from cgfoil.core.normals import compute_face_normals
from cgfoil.core.offset import offset_airfoil
from cgfoil.core.trim import adjust_endpoints, trim_self_intersecting_curve
from cgfoil.models import Ply, Skin, Web, AirfoilMesh, Thickness
from cgfoil.utils.geometry import point_in_polygon
from cgfoil.utils.io import load_airfoil
from cgfoil.utils.plot import plot_triangulation
from cgfoil.utils.summary import compute_cross_sectional_areas


def test_import():
    import cgfoil

    assert cgfoil


def test_models():
    thickness = Thickness(type='constant', value=0.1)
    assert thickness.compute([0.5], [0.5], [0.5]) == [0.1]

    ply = Ply(thickness=0.1, material=1)
    assert ply.thickness == 0.1
    assert ply.material == 1

    skin = Skin(thickness=thickness, material=2, sort_index=1)
    assert skin.thickness.type == 'constant'
    assert skin.material == 2
    assert skin.sort_index == 1

    web = Web(points=((0, 0), (1, 1)), plies=[ply], normal_ref=[0, 1], n_cell=10)
    assert web.points == ((0, 0), (1, 1))
    assert len(web.plies) == 1
    assert web.normal_ref == [0, 1]
    assert web.n_cell == 10

    mesh = AirfoilMesh(skins={"skin": skin}, webs={"web": web})
    assert "skin" in mesh.skins
    assert "web" in mesh.webs


def test_point_in_polygon():
    polygon = [Point_2(0, 0), Point_2(1, 0), Point_2(1, 1), Point_2(0, 1)]
    point_inside = Point_2(0.5, 0.5)
    point_outside = Point_2(2, 2)
    assert point_in_polygon(point_inside, polygon)
    assert not point_in_polygon(point_outside, polygon)


def test_create_line_mesh():
    p1 = Point_2(0, 0)
    p2 = Point_2(1, 0)
    points = create_line_mesh(p1, p2, 3)
    assert len(points) == 4  # p1, two intermediates, p2
    assert points[0].x() == 0
    assert points[0].y() == 0
    assert points[-1].x() == 1
    assert points[-1].y() == 0


def test_offset_airfoil():
    points = [Point_2(0, 0), Point_2(1, 0), Point_2(1, 1), Point_2(0, 1)]
    offset = offset_airfoil(points, 0.1)
    assert len(offset) == 4
    # Check that points are offset outward
    # For simplicity, just check length


def test_load_airfoil(tmp_path):
    dat_content = """1

0.0 0.0
1.0 0.1
"""
    file = tmp_path / "test.dat"
    file.write_text(dat_content)
    points = load_airfoil(str(file))
    assert len(points) == 2
    assert points[0].x() == 0.0
    assert points[0].y() == 0.0
    assert points[1].x() == 1.0
    assert points[1].y() == 0.1


def test_adjust_endpoints():
    points = [Point_2(0, 0), Point_2(1, 0), Point_2(2, 0)]
    adjusted = adjust_endpoints(points, 0.1)
    assert len(adjusted) == 3
    # Check that endpoints are adjusted
    assert adjusted[0].x() < 0  # moved backward
    assert adjusted[-1].x() > 2  # moved forward


def test_trim_self_intersecting_curve():
    # Create points that form a self-intersecting curve
    points = [Point_2(0, 0), Point_2(1, 1), Point_2(1, 0), Point_2(0, 1)]
    trimmed = trim_self_intersecting_curve(points)
    assert isinstance(trimmed, list)
    # Depending on intersection, it may trim


def test_compute_face_normals():
    cdt = Mesh_2_Constrained_Delaunay_triangulation_2()
    cdt.insert_constraint(Point_2(0, 0), Point_2(1, 0))
    cdt.insert_constraint(Point_2(1, 0), Point_2(0.5, 1))
    cdt.insert_constraint(Point_2(0.5, 1), Point_2(0, 0))
    outer_points = [Point_2(0, 0), Point_2(1, 0), Point_2(0.5, 1)]
    inner_list = []
    line_ply_list = []
    web_material_ids = []
    skin_material_ids = [0]
    outer_normals = [(0, 1), (0, 1), (0, 1)]
    ply_normals = []
    outer_tangents = [(1, 0), (-0.5, 0.5), (-0.5, -0.5)]
    face_normals, face_material_ids, face_inplanes = compute_face_normals(
        cdt,
        outer_points,
        inner_list,
        line_ply_list,
        web_material_ids,
        skin_material_ids,
        outer_normals,
        ply_normals,
        outer_tangents,
    )
    assert len(face_normals) == cdt.number_of_faces()
    assert len(face_material_ids) == cdt.number_of_faces()
    assert len(face_inplanes) == cdt.number_of_faces()


def test_compute_cross_sectional_areas():
    cdt = Mesh_2_Constrained_Delaunay_triangulation_2()
    cdt.insert_constraint(Point_2(0, 0), Point_2(1, 0))
    cdt.insert_constraint(Point_2(1, 0), Point_2(0.5, 1))
    cdt.insert_constraint(Point_2(0.5, 1), Point_2(0, 0))
    face_material_ids = [0] * cdt.number_of_faces()  # Assume all 0
    areas = compute_cross_sectional_areas(cdt, face_material_ids)
    assert isinstance(areas, dict)
    assert 0 in areas
    assert areas[0] > 0

@patch('matplotlib.pyplot.show')
def test_plot_triangulation(mock_show):
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
        plot_filename=None,
    )
    mock_show.assert_called_once()

@patch('matplotlib.pyplot.savefig')
def test_run_cgfoil(mock_savefig):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
        f.write("1\n\n0.0 0.0\n1.0 0.1\n")
        fname = f.name
    thickness = Thickness(type='constant', value=0.01)
    skins = {
        "skin": Skin(thickness=thickness, material=1, sort_index=1)
    }
    web_definition = {}
    mesh = AirfoilMesh(
        skins=skins,
        webs=web_definition,
        airfoil_filename=fname,
        plot=True,
        plot_filename='test.png'
    )
    run_cgfoil(mesh)
    mock_savefig.assert_called_once_with('test.png')
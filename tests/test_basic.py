"""Basic tests for cgfoil."""

import pytest
import tempfile
from unittest.mock import patch
from CGAL.CGAL_Kernel import Point_2
from CGAL.CGAL_Mesh_2 import Mesh_2_Constrained_Delaunay_triangulation_2
from cgfoil.core.main import run_cgfoil
from cgfoil.core.mesh import create_line_mesh
from cgfoil.core.normals import compute_face_normals
from cgfoil.core.offset import offset_airfoil
from cgfoil.core.trim import adjust_endpoints, trim_self_intersecting_curve
from cgfoil.models import Ply, Skin, Web
from cgfoil.utils.geometry import point_in_polygon
from cgfoil.utils.io import load_airfoil
from cgfoil.utils.plot import plot_triangulation
from cgfoil.utils.summary import compute_cross_sectional_areas


def test_import():
    import cgfoil

    assert cgfoil


def test_models():
    ply = Ply(thickness=0.1, material=1)
    assert ply.thickness == 0.1
    assert ply.material == 1

    skin = Skin(thickness=0.2, material=2, sort_index=1)
    assert skin.thickness == 0.2
    assert skin.material == 2
    assert skin.sort_index == 1

    web = Web(points=((0, 0), (1, 1)), plies=[ply], normal_ref=[0, 1], n_cell=10)
    assert web.points == ((0, 0), (1, 1))
    assert len(web.plies) == 1
    assert web.normal_ref == [0, 1]
    assert web.n_cell == 10


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
    ply_ids = []
    airfoil_ids = [0]
    outer_normals = [(0, 1), (0, 1), (0, 1)]
    ply_normals = []
    outer_tangents = [(1, 0), (-0.5, 0.5), (-0.5, -0.5)]
    face_normals, face_material_ids, face_inplanes = compute_face_normals(
        cdt,
        outer_points,
        inner_list,
        line_ply_list,
        ply_ids,
        airfoil_ids,
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
    ply_ids = []
    airfoil_ids = [0]
    web_names = []
    face_normals = [(0, 1)] * cdt.number_of_faces()
    face_material_ids = [0] * cdt.number_of_faces()
    face_inplanes = [(1, 0)] * cdt.number_of_faces()
    plot_triangulation(
        cdt,
        outer_points,
        inner_list,
        line_ply_list,
        untrimmed_lines,
        ply_ids,
        airfoil_ids,
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
    skins = {
        "skin": Skin(thickness=lambda x: 0.01, material=1, sort_index=1)
    }
    web_definition = {}
    run_cgfoil(skins, web_definition, airfoil_filename=fname, plot=True, vtk=None, split_view=False, plot_filename='test.png')
    mock_savefig.assert_called_once_with('test.png')

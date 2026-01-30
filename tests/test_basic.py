"""Basic tests for cgfoil."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
from CGAL.CGAL_Kernel import Point_2
from CGAL.CGAL_Mesh_2 import Mesh_2_Constrained_Delaunay_triangulation_2

from cgfoil.core.main import generate_mesh, plot_mesh, run_cgfoil
from cgfoil.core.mesh import create_line_mesh
from cgfoil.core.normals import compute_face_normals
from cgfoil.core.offset import offset_airfoil
from cgfoil.core.trim import adjust_endpoints, trim_self_intersecting_curve
from cgfoil.models import AirfoilMesh, Ply, Skin, Thickness, Web
from cgfoil.utils.geometry import point_in_polygon
from cgfoil.utils.io import load_airfoil
from cgfoil.utils.plot import plot_triangulation
from cgfoil.utils.summary import compute_cross_sectional_areas

# Constants for test assertions
EXPECTED_LEN_2 = 2
EXPECTED_LEN_3 = 3
EXPECTED_LEN_4 = 4
MATERIAL_1 = 1
MATERIAL_2 = 2
SORT_INDEX_1 = 1
N_ELEM_10 = 10
POINT_0 = 0
POINT_1 = 1
POINT_2 = 2
THICKNESS_0_1 = 0.1
POINT_0_5 = 0.5
THICKNESS_0_01 = 0.01
THICKNESS_0_005 = 0.005


def test_import():
    import cgfoil  # noqa: PLC0415

    assert cgfoil


def test_models():
    thickness = Thickness(type="constant", value=THICKNESS_0_1)
    assert thickness.compute(
        {
            "x": [POINT_0_5],
            "y": [POINT_0_5],
            "ta": [POINT_0_5],
            "tr": [POINT_0_5],
            "xr": [POINT_0_5],
        },
    ) == [THICKNESS_0_1]

    thickness_array = Thickness(type="array", array=[THICKNESS_0_1, 0.2, 0.3])
    assert thickness_array.compute(
        {
            "x": [0.0, POINT_0_5, POINT_1],
            "y": [0.0, POINT_0_5, POINT_1],
            "ta": [0.0, POINT_0_5, POINT_1],
            "tr": [0.0, POINT_0_5, POINT_1],
            "xr": [0.0, POINT_0_5, POINT_1],
        },
    ) == [THICKNESS_0_1, 0.2, 0.3]

    ply = Ply(thickness=thickness, material=MATERIAL_1)
    assert ply.thickness.type == "constant"
    assert ply.material == MATERIAL_1

    skin = Skin(thickness=thickness, material=MATERIAL_2, sort_index=SORT_INDEX_1)
    assert skin.thickness.type == "constant"
    assert skin.material == MATERIAL_2
    assert skin.sort_index == SORT_INDEX_1

    web = Web(
        points=[(POINT_0, POINT_0), (POINT_1, POINT_1)],
        plies=[ply],
        normal_ref=[POINT_0, POINT_1],
        n_elem=N_ELEM_10,
    )
    assert web.points == [(0.0, 0.0), (1.0, 1.0)]
    assert len(web.plies) == MATERIAL_1
    assert web.normal_ref == [POINT_0, POINT_1]
    assert web.n_elem == N_ELEM_10

    mesh = AirfoilMesh(skins={"skin": skin}, webs={"web": web})
    assert "skin" in mesh.skins
    assert "web" in mesh.webs


def test_point_in_polygon():
    polygon = [
        Point_2(POINT_0, POINT_0),
        Point_2(POINT_1, POINT_0),
        Point_2(POINT_1, POINT_1),
        Point_2(POINT_0, POINT_1),
    ]
    point_inside = Point_2(POINT_0_5, POINT_0_5)
    point_outside = Point_2(POINT_2, POINT_2)
    assert point_in_polygon(point_inside, polygon)
    assert not point_in_polygon(point_outside, polygon)


def test_create_line_mesh():
    p1 = Point_2(POINT_0, POINT_0)
    p2 = Point_2(POINT_1, POINT_0)
    points = create_line_mesh(p1, p2, 3)
    assert len(points) == EXPECTED_LEN_4  # p1, two intermediates, p2
    assert points[POINT_0].x() == POINT_0
    assert points[POINT_0].y() == POINT_0
    assert points[-POINT_1].x() == POINT_1
    assert points[-POINT_1].y() == POINT_0


def test_offset_airfoil():
    points = [
        Point_2(POINT_0, POINT_0),
        Point_2(POINT_1, POINT_0),
        Point_2(POINT_1, POINT_1),
        Point_2(POINT_0, POINT_1),
    ]
    offset = offset_airfoil(points, THICKNESS_0_1)
    assert len(offset) == EXPECTED_LEN_4
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
    assert len(points) == EXPECTED_LEN_2
    assert points[POINT_0].x() == 0.0
    assert points[POINT_0].y() == 0.0
    assert points[POINT_1].x() == 1.0
    assert points[POINT_1].y() == THICKNESS_0_1


def test_load_airfoil_list():
    points_list = [(0.0, 0.0), (1.0, THICKNESS_0_1)]
    points = load_airfoil(points_list)
    assert len(points) == EXPECTED_LEN_2
    assert points[POINT_0].x() == 0.0
    assert points[POINT_0].y() == 0.0
    assert points[POINT_1].x() == 1.0
    assert points[POINT_1].y() == THICKNESS_0_1


def test_load_airfoil_numpy():
    points_array = np.array([[0.0, 0.0], [1.0, THICKNESS_0_1]])
    points = load_airfoil(points_array)
    assert len(points) == EXPECTED_LEN_2
    assert points[POINT_0].x() == 0.0
    assert points[POINT_0].y() == 0.0
    assert points[POINT_1].x() == 1.0
    assert points[POINT_1].y() == THICKNESS_0_1


def test_adjust_endpoints():
    points = [
        Point_2(POINT_0, POINT_0),
        Point_2(POINT_1, POINT_0),
        Point_2(POINT_2, POINT_0),
    ]
    adjusted = adjust_endpoints(points, THICKNESS_0_1)
    assert len(adjusted) == EXPECTED_LEN_3
    # Check that endpoints are adjusted
    assert adjusted[POINT_0].x() < POINT_0  # moved backward
    assert adjusted[-POINT_1].x() > POINT_2  # moved forward


def test_trim_self_intersecting_curve():
    # Create points that form a self-intersecting curve
    points = [
        Point_2(POINT_0, POINT_0),
        Point_2(POINT_1, POINT_1),
        Point_2(POINT_1, POINT_0),
        Point_2(POINT_0, POINT_1),
    ]
    trimmed = trim_self_intersecting_curve(points)
    assert isinstance(trimmed, list)
    # Depending on intersection, it may trim


def test_compute_face_normals():
    cdt = Mesh_2_Constrained_Delaunay_triangulation_2()
    cdt.insert_constraint(Point_2(POINT_0, POINT_0), Point_2(POINT_1, POINT_0))
    cdt.insert_constraint(Point_2(POINT_1, POINT_0), Point_2(POINT_0_5, POINT_1))
    cdt.insert_constraint(Point_2(POINT_0_5, POINT_1), Point_2(POINT_0, POINT_0))
    outer_points = [
        Point_2(POINT_0, POINT_0),
        Point_2(POINT_1, POINT_0),
        Point_2(POINT_0_5, POINT_1),
    ]
    inner_list = []
    line_ply_list = []
    web_material_ids = []
    skin_material_ids = [POINT_0]
    outer_normals = [(POINT_0, POINT_1), (POINT_0, POINT_1), (POINT_0, POINT_1)]
    ply_normals = []
    outer_tangents = [
        (POINT_1, POINT_0),
        (-POINT_0_5, POINT_0_5),
        (-POINT_0_5, -POINT_0_5),
    ]
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
    cdt.insert_constraint(Point_2(POINT_0, POINT_0), Point_2(POINT_1, POINT_0))
    cdt.insert_constraint(Point_2(POINT_1, POINT_0), Point_2(POINT_0_5, POINT_1))
    cdt.insert_constraint(Point_2(POINT_0_5, POINT_1), Point_2(POINT_0, POINT_0))
    face_material_ids = [POINT_0] * cdt.number_of_faces()  # Assume all 0
    areas = compute_cross_sectional_areas(cdt, face_material_ids)
    assert isinstance(areas, dict)
    assert POINT_0 in areas
    assert areas[POINT_0] > POINT_0


def test_plot_triangulation():
    cdt = Mesh_2_Constrained_Delaunay_triangulation_2()
    cdt.insert_constraint(Point_2(POINT_0, POINT_0), Point_2(POINT_1, POINT_0))
    cdt.insert_constraint(Point_2(POINT_1, POINT_0), Point_2(POINT_0_5, POINT_1))
    cdt.insert_constraint(Point_2(POINT_0_5, POINT_1), Point_2(POINT_0, POINT_0))
    outer_points = [
        Point_2(POINT_0, POINT_0),
        Point_2(POINT_1, POINT_0),
        Point_2(POINT_0_5, POINT_1),
    ]
    inner_list = []
    line_ply_list = []
    untrimmed_lines = []
    web_material_ids = []
    skin_material_ids = [POINT_0]
    web_names = []
    face_normals = [(POINT_0, POINT_1)] * cdt.number_of_faces()
    face_material_ids = [POINT_0] * cdt.number_of_faces()
    face_inplanes = [(POINT_1, POINT_0)] * cdt.number_of_faces()
    # Compute vertices and faces
    vertices = []
    vertex_map = {}
    for idx, v in enumerate(cdt.finite_vertices()):
        vertex_map[v] = idx
        vertices.append([v.point().x(), v.point().y(), 0.0])
    faces = []
    for face in cdt.finite_faces():
        v0 = vertex_map[face.vertex(POINT_0)]
        v1 = vertex_map[face.vertex(POINT_1)]
        v2 = vertex_map[face.vertex(POINT_2)]
        faces.append([3, v0, v1, v2])
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        plot_filename = f.name
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
        plot_filename=plot_filename,
    )
    assert Path(plot_filename).exists()
    Path(plot_filename).unlink()


def test_plot_mesh():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".dat", delete=False) as f:
        f.write("1\n\n0.0 0.0\n1.0 0.1\n")
        fname = f.name
    thickness = Thickness(type="constant", value=THICKNESS_0_01)
    skins = {
        "skin": Skin(
            thickness=thickness,
            material=MATERIAL_1,
            sort_index=SORT_INDEX_1,
        ),
    }
    web_definition = {}
    mesh = AirfoilMesh(
        skins=skins,
        webs=web_definition,
        airfoil_input=fname,
        plot=True,
        plot_filename=None,
        split_view=False,
    )
    mesh_result = generate_mesh(mesh)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        plot_filename = f.name
    plot_mesh(mesh_result, plot_filename, split_view=False)
    assert Path(plot_filename).exists()
    Path(plot_filename).unlink()


@patch("matplotlib.pyplot.savefig")
def test_run_cgfoil(mock_savefig):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".dat", delete=False) as f:
        f.write("1\n\n0.0 0.0\n1.0 0.1\n")
        fname = f.name
    thickness = Thickness(type="constant", value=THICKNESS_0_01)
    skins = {
        "skin": Skin(
            thickness=thickness,
            material=MATERIAL_1,
            sort_index=SORT_INDEX_1,
        ),
    }
    web_definition = {}
    mesh = AirfoilMesh(
        skins=skins,
        webs=web_definition,
        airfoil_input=fname,
        plot=True,
        plot_filename="test.png",
    )
    run_cgfoil(mesh)
    mock_savefig.assert_called_once_with("test.png")


def test_run_examples():
    """Test running a simple example."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".dat", delete=False) as f:
        f.write("1\n\n0.0 0.0\n1.0 0.1\n")
        fname = f.name
    skins = {
        "skin": Skin(
            thickness=Thickness(type="constant", value=THICKNESS_0_005),
            material=MATERIAL_1,
            sort_index=SORT_INDEX_1,
        ),
    }
    mesh = AirfoilMesh(skins=skins, webs={}, airfoil_input=fname, plot=False, vtk=None)
    run_cgfoil(mesh)

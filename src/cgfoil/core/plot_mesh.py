"""Mesh plotting logic."""

from cgfoil.models import MeshResult
from cgfoil.utils.plot import plot_triangulation


def plot_mesh(
    mesh_result: MeshResult,
    plot_filename: str | None = None,
    split_view: bool = False,
):
    # Convert back to Point_2 for plotting
    from CGAL.CGAL_Kernel import Point_2

    outer_points = [Point_2(*p) for p in mesh_result.outer_points]
    inner_list = [[Point_2(*p) for p in inner] for inner in mesh_result.inner_list]
    line_ply_list = [[Point_2(*p) for p in ply] for ply in mesh_result.line_ply_list]
    untrimmed_lines = [
        [Point_2(*p) for p in line] for line in mesh_result.untrimmed_lines
    ]
    plot_triangulation(
        mesh_result.vertices,
        mesh_result.faces,
        outer_points,
        inner_list,
        line_ply_list,
        untrimmed_lines,
        mesh_result.web_material_ids,
        mesh_result.skin_material_ids,
        mesh_result.web_names,
        mesh_result.face_normals,
        mesh_result.face_material_ids,
        mesh_result.face_inplanes,
        split_view,
        plot_filename,
    )
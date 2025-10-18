"""Main execution logic for cgfoil."""

import math
import numpy as np
from typing import Dict, Optional
from CGAL.CGAL_Kernel import Point_2
from CGAL.CGAL_Mesh_2 import Mesh_2_Constrained_Delaunay_triangulation_2
from cgfoil.core.mesh import create_line_mesh
from cgfoil.core.normals import compute_face_normals
from cgfoil.core.offset import offset_airfoil
from cgfoil.core.trim import (
    adjust_endpoints,
    trim_line,
    trim_self_intersecting_curve,
)
from cgfoil.models import Skin, Web, AirfoilMesh, MeshResult
from cgfoil.utils.geometry import point_in_polygon
from cgfoil.utils.io import load_airfoil
from cgfoil.utils.logger import logger
from cgfoil.utils.plot import plot_triangulation
from cgfoil.utils.summary import compute_cross_sectional_areas


def generate_mesh(mesh: AirfoilMesh) -> MeshResult:
    skins = mesh.skins
    web_definition = mesh.webs
    airfoil_filename = mesh.airfoil_filename
    n_elem = mesh.n_elem

    # Load airfoil points (outer)
    outer_points = load_airfoil(airfoil_filename, n_elem)

    # Compute coordinates: x, ta (absolute arc length), tr (relative arc length)
    x = [p.x() for p in outer_points]
    ta = [0.0]
    for i in range(1, len(outer_points)):
        dx = outer_points[i].x() - outer_points[i-1].x()
        dy = outer_points[i].y() - outer_points[i-1].y()
        dist = math.sqrt(dx**2 + dy**2)
        ta.append(ta[-1] + dist)
    total_length = ta[-1]
    tr = [t / total_length for t in ta]

    # Compute normals for outer points (outward)
    n = len(outer_points)
    outer_normals = []
    outer_tangents = []
    for i in range(n):
        prev = outer_points[(i - 1) % n]
        curr = outer_points[i]
        next_p = outer_points[(i + 1) % n]
        tx = (next_p.x() - prev.x()) / 2
        ty = (next_p.y() - prev.y()) / 2
        t_len = math.sqrt(tx**2 + ty**2)
        if t_len > 0:
            tx /= t_len
            ty /= t_len
        nx = -ty
        ny = tx
        outer_normals.append((nx, ny))
        outer_tangents.append((tx, ty))

    # Ply thicknesses for airfoil
    sorted_skins = sorted(skins.values(), key=lambda s: s.sort_index)
    ply_thicknesses = []
    for s in sorted_skins:
        thickness_result = s.thickness.compute(x, ta, tr)
        ply_thicknesses.append(thickness_result)
    inner_list = []
    current = outer_points
    for thickness in ply_thicknesses:
        current = offset_airfoil(current, thickness)
        inner_points = trim_self_intersecting_curve(current)
        inner_list.append(inner_points)

    # Calculate protrusion distance from last ply thickness
    last_ply = ply_thicknesses[-1]
    if isinstance(last_ply, (list, np.ndarray)):
        protrusion_distance = 0.5 * max(last_ply)
    else:
        protrusion_distance = 0.5 * last_ply
    if protrusion_distance == 0:
        protrusion_distance = 1e-3

    # Create line plies for each web
    line_ply_list = []
    ply_ids = []
    ply_normals = []
    untrimmed_lines = []
    web_names = list(web_definition.keys())
    for web_name, web in web_definition.items():
        p1_coords, p2_coords = web.points
        p1 = Point_2(*p1_coords)
        p2 = Point_2(*p2_coords)
        untrimmed_base_line = create_line_mesh(p1, p2, web.n_cell)
        untrimmed_lines.append(untrimmed_base_line)
        base_line = trim_line(untrimmed_base_line, inner_list[-1])
        base_line = adjust_endpoints(base_line, protrusion_distance)
        current_line = base_line
        current_untrimmed = untrimmed_base_line
        normal_ref = web.normal_ref
        for ply in web.plies:
            if callable(ply.thickness):
                thickness_list = [ply.thickness(p.y()) for p in untrimmed_base_line]
            else:
                thickness_list = [ply.thickness] * len(untrimmed_base_line)
            untrimmed_offset_line = offset_airfoil(
                current_untrimmed, thickness_list, normal_ref
            )
            offset_line = trim_line(untrimmed_offset_line, inner_list[-1])
            offset_line = adjust_endpoints(offset_line, protrusion_distance)
            ply_points = current_line + offset_line[::-1]
            line_ply_list.append(ply_points)
            ply_ids.append(ply.material)
            ply_normals.append(normal_ref if normal_ref else [0, 0])
            current_line = offset_line
            current_untrimmed = untrimmed_offset_line

    # Airfoil material ids
    airfoil_ids = [0] + [s.material for s in sorted_skins]

    # Create constrained Delaunay triangulation
    cdt = Mesh_2_Constrained_Delaunay_triangulation_2()

    # Insert outer boundary as constraints
    for i in range(len(outer_points)):
        cdt.insert_constraint(
            outer_points[i], outer_points[(i + 1) % len(outer_points)]
        )

    # Insert inner boundaries as constraints
    for inner_points in inner_list:
        for i in range(len(inner_points)):
            cdt.insert_constraint(
                inner_points[i], inner_points[(i + 1) % len(inner_points)]
            )

    # Insert line plies as constraints
    for ply_points in line_ply_list:
        for i in range(len(ply_points)):
            cdt.insert_constraint(ply_points[i], ply_points[(i + 1) % len(ply_points)])

    # Collect vertices and faces
    vertices = []
    vertex_map = {}
    idx = 0
    for v in cdt.finite_vertices():
        vertex_map[v] = idx
        vertices.append([v.point().x(), v.point().y(), 0.0])
        idx += 1
    faces = []
    for face in cdt.finite_faces():
        material_id = -1  # Will compute below
        if material_id != -1:
            v0 = vertex_map[face.vertex(0)]
            v1 = vertex_map[face.vertex(1)]
            v2 = vertex_map[face.vertex(2)]
            faces.append([3, v0, v1, v2])

    # Compute face normals and material IDs
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

    # Collect faces with material_id != -1 and filter the lists
    faces = []
    filtered_face_normals = []
    filtered_face_material_ids = []
    filtered_face_inplanes = []
    idx = 0
    for face in cdt.finite_faces():
        material_id = face_material_ids[idx]
        if material_id != -1:
            v0 = vertex_map[face.vertex(0)]
            v1 = vertex_map[face.vertex(1)]
            v2 = vertex_map[face.vertex(2)]
            faces.append([3, v0, v1, v2])
            filtered_face_normals.append(face_normals[idx])
            filtered_face_material_ids.append(material_id)
            filtered_face_inplanes.append(face_inplanes[idx])
        idx += 1

    # Compute cross-sectional areas
    areas = compute_cross_sectional_areas(cdt, face_material_ids)

    # Convert to serializable lists
    outer_points_list = [[p.x(), p.y()] for p in outer_points]
    inner_list_list = [[[p.x(), p.y()] for p in inner] for inner in inner_list]
    line_ply_list_list = [[[p.x(), p.y()] for p in ply] for ply in line_ply_list]
    untrimmed_lines_list = [[[p.x(), p.y()] for p in line] for line in untrimmed_lines]

    return MeshResult(
        vertices=vertices,
        faces=faces,
        outer_points=outer_points_list,
        inner_list=inner_list_list,
        line_ply_list=line_ply_list_list,
        untrimmed_lines=untrimmed_lines_list,
        ply_ids=ply_ids,
        airfoil_ids=airfoil_ids,
        web_names=web_names,
        face_normals=filtered_face_normals,
        face_material_ids=filtered_face_material_ids,
        face_inplanes=filtered_face_inplanes,
        areas=areas,
    )


def plot_mesh(mesh_result: MeshResult, plot_filename: Optional[str] = None, split_view: bool = False):
    # Convert back to Point_2 for plotting
    from CGAL.CGAL_Kernel import Point_2
    outer_points = [Point_2(*p) for p in mesh_result.outer_points]
    inner_list = [[Point_2(*p) for p in inner] for inner in mesh_result.inner_list]
    line_ply_list = [[Point_2(*p) for p in ply] for ply in mesh_result.line_ply_list]
    untrimmed_lines = [[Point_2(*p) for p in line] for line in mesh_result.untrimmed_lines]
    plot_triangulation(
        mesh_result.vertices,
        mesh_result.faces,
        outer_points,
        inner_list,
        line_ply_list,
        untrimmed_lines,
        mesh_result.ply_ids,
        mesh_result.airfoil_ids,
        mesh_result.web_names,
        mesh_result.face_normals,
        mesh_result.face_material_ids,
        mesh_result.face_inplanes,
        split_view,
        plot_filename,
    )


def run_cgfoil(mesh: AirfoilMesh):
    mesh_result = generate_mesh(mesh)
    logger.info(f"Cross-sectional areas: {mesh_result.areas}")

    if mesh.vtk:
        try:
            import pyvista as pv
        except ImportError:
            logger.warning("pyvista not available, cannot save VTK")
        else:
            mesh_obj = pv.UnstructuredGrid(
                mesh_result.faces, [pv.CellType.TRIANGLE] * len(mesh_result.faces), mesh_result.vertices
            )
            mesh_obj.cell_data["material_id"] = mesh_result.face_material_ids
            mesh_obj.cell_data["normals"] = np.array([[n[0], n[1], 0.0] for n in mesh_result.face_normals])
            mesh_obj.cell_data["inplane"] = np.array([[i[0], i[1], 0.0] for i in mesh_result.face_inplanes])
            mesh_obj.save(mesh.vtk)
            logger.info(f"Mesh saved to {mesh.vtk}")

    if mesh.plot:
        plot_mesh(mesh_result, mesh.plot_filename, mesh.split_view)

    logger.info(f"Number of vertices: {len(mesh_result.vertices)}")
    logger.info(f"Number of faces: {len(mesh_result.faces)}")
    logger.info(f"Web Material ids: {mesh_result.ply_ids}")
    logger.info(f"Airfoil Material ids: {mesh_result.airfoil_ids}")
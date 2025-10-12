"""Main execution logic for cgfoil."""

from CGAL.CGAL_Kernel import Point_2
from CGAL.CGAL_Mesh_2 import Mesh_2_Constrained_Delaunay_triangulation_2

from cgfoil.core.mesh import create_line_mesh
from cgfoil.core.offset import offset_airfoil
from cgfoil.core.trim import (
    adjust_endpoints,
    trim_line,
    trim_self_intersecting_curve,
)
from cgfoil.utils.geometry import point_in_polygon
from cgfoil.utils.io import load_airfoil
from cgfoil.utils.plot import plot_triangulation


def run_cgfoil(
    skins, web_definition, airfoil_filename="naca0018.dat", plot=False, vtk=None
):
    # Load airfoil points (outer)
    outer_points = load_airfoil(airfoil_filename)

    # Ply thicknesses for airfoil
    x = [p.x() for p in outer_points]
    sorted_skins = sorted(skins.values(), key=lambda d: d["sort_index"])
    ply_thicknesses = [s["thickness"] for s in sorted_skins]
    inner_list = []
    current = outer_points
    for thickness in ply_thicknesses:
        current = offset_airfoil(current, thickness)
        inner_points = trim_self_intersecting_curve(current)
        inner_list.append(inner_points)

    # Calculate protrusion distance from last ply thickness
    last_ply = ply_thicknesses[-1]
    if isinstance(last_ply, list):
        protrusion_distance = 0.5 * max(last_ply)
    else:
        protrusion_distance = 0.5 * max(last_ply)
    if protrusion_distance == 0:
        protrusion_distance = 1e-3

    # Create line plies for each web
    line_ply_list = []
    ply_ids = []
    untrimmed_lines = []
    web_names = list(web_definition.keys())
    for web_name, web in web_definition.items():
        p1_coords, p2_coords = web["points"]
        p1 = Point_2(*p1_coords)
        p2 = Point_2(*p2_coords)
        untrimmed_base_line = create_line_mesh(p1, p2, web["n_cell"])
        untrimmed_lines.append(untrimmed_base_line)
        base_line = trim_line(untrimmed_base_line, inner_list[-1])
        base_line = adjust_endpoints(base_line, protrusion_distance)
        current_line = base_line
        current_untrimmed = untrimmed_base_line
        normal_ref = web.get("normal_ref")
        for ply in web["plies"]:
            if callable(ply["thickness"]):
                thickness_list = [ply["thickness"](p.y()) for p in untrimmed_base_line]
            else:
                thickness_list = [ply["thickness"]] * len(untrimmed_base_line)
            untrimmed_offset_line = offset_airfoil(
                current_untrimmed, thickness_list, normal_ref
            )
            offset_line = trim_line(untrimmed_offset_line, inner_list[-1])
            offset_line = adjust_endpoints(offset_line, protrusion_distance)
            ply_points = current_line + offset_line[::-1]
            line_ply_list.append(ply_points)
            ply_ids.append(ply["material"])
            current_line = offset_line
            current_untrimmed = untrimmed_offset_line

    # Airfoil material ids
    airfoil_ids = []
    material_id = max(ply_ids) + 1 if ply_ids else 0
    for i in range(len(inner_list) + 1):
        airfoil_ids.append(material_id)
        material_id += 1

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

    if vtk:
        try:
            import pyvista as pv
        except ImportError:
            print("pyvista not available, cannot save VTK")
        else:
            # Collect vertices
            vertices = []
            vertex_map = {}
            idx = 0
            for v in cdt.finite_vertices():
                vertex_map[v] = idx
                vertices.append([v.point().x(), v.point().y(), 0.0])
                idx += 1
            # Collect faces and materials
            faces = []
            cell_materials = []
            for face in cdt.finite_faces():
                p0 = face.vertex(0).point()
                p1 = face.vertex(1).point()
                p2 = face.vertex(2).point()
                cx = (p0.x() + p1.x() + p2.x()) / 3.0
                cy = (p0.y() + p1.y() + p2.y()) / 3.0
                centroid = Point_2(cx, cy)
                in_hole = point_in_polygon(centroid, inner_list[-1])
                material_id = -1
                if not in_hole:
                    for i in range(len(inner_list) + 1):
                        if i == 0:
                            if not point_in_polygon(centroid, inner_list[0]):
                                material_id = airfoil_ids[i]
                                break
                        elif i < len(inner_list):
                            if point_in_polygon(
                                centroid, inner_list[i - 1]
                            ) and not point_in_polygon(centroid, inner_list[i]):
                                material_id = airfoil_ids[i]
                                break
                        else:
                            if point_in_polygon(centroid, inner_list[-1]):
                                material_id = airfoil_ids[i]
                                break
                if material_id == -1:
                    for idx_ply, ply in enumerate(line_ply_list):
                        if point_in_polygon(centroid, ply):
                            material_id = ply_ids[idx_ply]
                            break
                if material_id != -1:
                    v0 = vertex_map[face.vertex(0)]
                    v1 = vertex_map[face.vertex(1)]
                    v2 = vertex_map[face.vertex(2)]
                    faces.append([3, v0, v1, v2])
                    cell_materials.append(material_id)
            mesh = pv.UnstructuredGrid(
                faces, [pv.CellType.TRIANGLE] * len(faces), vertices
            )
            mesh.cell_data["material_id"] = cell_materials
            mesh.save(vtk)
            print(f"Mesh saved to {vtk}")

    if plot:
        plot_triangulation(
            cdt,
            outer_points,
            inner_list,
            line_ply_list,
            untrimmed_lines,
            ply_ids,
            airfoil_ids,
            web_names,
        )

    print(f"Number of vertices: {cdt.number_of_vertices()}")
    print(f"Number of faces: {cdt.number_of_faces()}")
    print(f"Web Material ids: {ply_ids}")
    print(f"Airfoil Material ids: {airfoil_ids}")

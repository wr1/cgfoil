"""Normal computation utilities."""

from cgfoil.utils.geometry import point_in_polygon


def compute_face_normals(
    cdt,
    outer_points,
    inner_list,
    line_ply_list,
    ply_ids,
    airfoil_ids,
    outer_normals,
    ply_normals,
    outer_tangents,
):
    """Compute normals, inplane vectors, and material IDs for each finite face in the triangulation."""
    face_normals = []
    face_inplanes = []
    face_material_ids = []
    n = len(outer_points)
    for face in cdt.finite_faces():
        p0 = face.vertex(0).point()
        p1 = face.vertex(1).point()
        p2 = face.vertex(2).point()
        cx = (p0.x() + p1.x() + p2.x()) / 3.0
        cy = (p0.y() + p1.y() + p2.y()) / 3.0
        centroid = type(outer_points[0])(cx, cy)  # Assuming Point_2
        in_hole = len(inner_list) > 0 and point_in_polygon(centroid, inner_list[-1])
        material_id = -1
        normal_x, normal_y = 0, 0
        inplane_x, inplane_y = 0, 0
        if not in_hole:
            for i in range(len(inner_list) + 1):
                if i == 0:
                    if len(inner_list) == 0 or not point_in_polygon(centroid, inner_list[0]):
                        material_id = airfoil_ids[i]
                        # Find closest outer point by 2D distance
                        closest_i = min(
                            range(n),
                            key=lambda j: (outer_points[j].x() - cx) ** 2 + (outer_points[j].y() - cy) ** 2,
                        )
                        normal_x, normal_y = outer_normals[closest_i]
                        inplane_x, inplane_y = outer_tangents[closest_i]
                        break
                elif i < len(inner_list):
                    if (
                        point_in_polygon(centroid, inner_list[i - 1])
                        and not point_in_polygon(centroid, inner_list[i])
                    ):
                        material_id = airfoil_ids[i]
                        # Find closest outer point by 2D distance
                        closest_i = min(
                            range(n),
                            key=lambda j: (outer_points[j].x() - cx) ** 2 + (outer_points[j].y() - cy) ** 2,
                        )
                        normal_x, normal_y = outer_normals[closest_i]
                        inplane_x, inplane_y = outer_tangents[closest_i]
                        break
                else:
                    if point_in_polygon(centroid, inner_list[-1]):
                        material_id = airfoil_ids[i]
                        # Find closest outer point by 2D distance
                        closest_i = min(
                            range(n),
                            key=lambda j: (outer_points[j].x() - cx) ** 2 + (outer_points[j].y() - cy) ** 2,
                        )
                        normal_x, normal_y = outer_normals[closest_i]
                        inplane_x, inplane_y = outer_tangents[closest_i]
                        break
        if material_id == -1:
            for idx_ply, ply in enumerate(line_ply_list):
                if point_in_polygon(centroid, ply):
                    material_id = ply_ids[idx_ply]
                    normal_x, normal_y = ply_normals[idx_ply]
                    inplane_x, inplane_y = ply_normals[idx_ply][1], -ply_normals[idx_ply][0]
                    break
        face_normals.append((normal_x, normal_y))
        face_inplanes.append((inplane_x, inplane_y))
        face_material_ids.append(material_id)
    return face_normals, face_material_ids, face_inplanes

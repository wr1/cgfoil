"""Summarizing utilities."""

from __future__ import annotations


def compute_cross_sectional_areas(cdt, face_material_ids) -> dict[int, float]:
    """Compute total cross-sectional area for each material ID."""
    areas = {}
    idx = 0
    for face in cdt.finite_faces():
        material_id = face_material_ids[idx]
        if material_id != -1:
            p0 = face.vertex(0).point()
            p1 = face.vertex(1).point()
            p2 = face.vertex(2).point()
            x1, y1 = p0.x(), p0.y()
            x2, y2 = p1.x(), p1.y()
            x3, y3 = p2.x(), p2.y()
            area = 0.5 * abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
            areas[material_id] = areas.get(material_id, 0) + area
        idx += 1
    return areas

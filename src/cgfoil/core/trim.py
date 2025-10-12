"""Trimming utilities."""

import math
from CGAL.CGAL_Kernel import Point_2, Segment_2, do_intersect, intersection


def trim_self_intersecting_curve(points):
    """Trim the curve to remove loose ends by keeping the closed loop between self-intersection points."""
    n = len(points)
    intersecting_indices = set()
    for i in range(n - 1):
        seg1 = Segment_2(points[i], points[(i + 1) % n])
        for j in range(i + 2, n - 1):
            seg2 = Segment_2(points[j], points[(j + 1) % n])
            if do_intersect(seg1, seg2):
                intersecting_indices.add(i)
                intersecting_indices.add(j)
    print(
        f"Self intersecting indices: {intersecting_indices}, count: {len(intersecting_indices)}"
    )
    if intersecting_indices:
        min_idx = min(intersecting_indices)
        max_idx = max(intersecting_indices)
        return points[min_idx + 1 : max_idx + 1]
    return points


def trim_line(points, inner_points):
    """Trim the line to keep only the piece between intersections with inner."""
    inter_points = []
    for i in range(len(points) - 1):
        seg = Segment_2(points[i], points[i + 1])
        for j in range(len(inner_points)):
            inner_seg = Segment_2(
                inner_points[j], inner_points[(j + 1) % len(inner_points)]
            )
            if do_intersect(seg, inner_seg):
                inter = intersection(seg, inner_seg)
                if inter.is_Point_2():
                    inter_points.append(inter.get_Point_2())
    if len(inter_points) >= 2:
        all_points = points + inter_points
        # Sort by distance from start
        start = points[0]
        all_points.sort(
            key=lambda p: math.sqrt((p.x() - start.x()) ** 2 + (p.y() - start.y()) ** 2)
        )
        # Find indices of inter_points in sorted list
        inter_set = set((p.x(), p.y()) for p in inter_points)
        indices = [i for i, p in enumerate(all_points) if (p.x(), p.y()) in inter_set]
        if indices:
            min_idx = min(indices)
            max_idx = max(indices)
            return all_points[min_idx : max_idx + 1]
    return points


def adjust_endpoints(points, distance):
    """Adjust endpoints to project out in line direction by distance."""
    if len(points) < 2:
        return points
    # For start point, move backward along tangent
    p0 = points[0]
    p1 = points[1]
    dx = p1.x() - p0.x()
    dy = p1.y() - p0.y()
    len_t = math.sqrt(dx**2 + dy**2)
    if len_t > 0:
        dx /= len_t
        dy /= len_t
        points[0] = Point_2(p0.x() - distance * dx, p0.y() - distance * dy)
    # For end point, move forward along tangent
    pn = points[-1]
    pm = points[-2]
    dx = pn.x() - pm.x()
    dy = pn.y() - pm.y()
    len_t = math.sqrt(dx**2 + dy**2)
    if len_t > 0:
        dx /= len_t
        dy /= len_t
        points[-1] = Point_2(pn.x() + distance * dx, pn.y() + distance * dy)
    return points

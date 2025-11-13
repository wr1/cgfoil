"""Trimming utilities."""

import math
from CGAL.CGAL_Kernel import Point_2, Segment_2, do_intersect, intersection
from cgfoil.utils.logger import logger


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
    logger.info(
        f"Self intersecting indices: {intersecting_indices}, count: {len(intersecting_indices)}"
    )
    if intersecting_indices:
        min_idx = min(intersecting_indices)
        max_idx = max(intersecting_indices)
        trimmed = points[min_idx + 1 : max_idx + 1]
        logger.info(f"Trimmed curve from {len(points)} to {len(trimmed)} points")
        return trimmed
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
    logger.info(f"Found {len(inter_points)} intersection points with inner boundary")
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
            trimmed = all_points[min_idx : max_idx + 1]
            logger.info(f"Trimmed line to {len(trimmed)} points between indices {min_idx} to {max_idx}")
            return trimmed
    logger.info("No trimming applied, returning original points")
    return points


def adjust_endpoints(points, distance):
    """Adjust endpoints to project out in line direction by distance."""
    if len(points) < 2:
        return points
    # Compute overall direction from start to end
    p_start = points[0]
    p_end = points[-1]
    overall_dx = p_end.x() - p_start.x()
    overall_dy = p_end.y() - p_start.y()
    len_overall = math.sqrt(overall_dx**2 + overall_dy**2)
    if len_overall > 0:
        overall_dx /= len_overall
        overall_dy /= len_overall
        # For start point, move backward along overall direction
        new_p0 = Point_2(p_start.x() - distance * overall_dx, p_start.y() - distance * overall_dy)
        logger.info(f"Adjusted start point from ({p_start.x():.4f}, {p_start.y():.4f}) to ({new_p0.x():.4f}, {new_p0.y():.4f}) along overall direction")
        points[0] = new_p0
        # For end point, move forward along overall direction
        new_pn = Point_2(p_end.x() + distance * overall_dx, p_end.y() + distance * overall_dy)
        logger.info(f"Adjusted end point from ({p_end.x():.4f}, {p_end.y():.4f}) to ({new_pn.x():.4f}, {new_pn.y():.4f}) along overall direction")
        points[-1] = new_pn
    else:
        logger.warning("Overall direction length is zero, no adjustment made")
    return points

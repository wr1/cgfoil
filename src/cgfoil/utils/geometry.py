"""Geometric utilities."""


def point_in_polygon(point, polygon):
    """Check if point is inside polygon using ray casting."""
    x, y = point.x(), point.y()
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0].x(), polygon[0].y()
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n].x(), polygon[i % n].y()
        if y > min(p1y, p2y) and y <= max(p1y, p2y) and x <= max(p1x, p2x):
            if p1y != p2y:
                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            if p1x == p2x or x <= xinters:
                inside = not inside
        p1x, p1y = p2x, p2y
    return inside

"""Meshing utilities."""

from CGAL.CGAL_Kernel import Point_2


def create_line_mesh(p1, p2, n_elements):
    """Create points for a line mesh with n_elements between p1 and p2."""
    points = [p1]
    for i in range(1, n_elements):
        t = i / n_elements
        x = p1.x() + t * (p2.x() - p1.x())
        y = p1.y() + t * (p2.y() - p1.y())
        points.append(Point_2(x, y))
    points.append(p2)
    return points

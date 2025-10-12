"""Input/Output utilities."""

from CGAL.CGAL_Kernel import Point_2


def load_airfoil(filename):
    """Load airfoil points from file."""
    points = []
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines[1:]:  # Skip header
            parts = line.strip().split()
            if len(parts) == 2:
                x = float(parts[0])
                y = float(parts[1])
                points.append(Point_2(x, y))
    return points

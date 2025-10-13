"""Plotting utilities."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from CGAL.CGAL_Kernel import Point_2
from cgfoil.utils.geometry import point_in_polygon


def plot_triangulation(
    cdt,
    outer_points,
    inner_list,
    line_ply_list,
    untrimmed_lines,
    ply_ids,
    airfoil_ids,
    web_names,
    face_normals,
    face_material_ids,
    face_inplanes,
    split_view=False,
):
    """Plot the triangulation with filled triangles colored by material id and colorbar."""

    def rescale_plot(ax, scale=1.1):
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        xmid = (xmin + xmax) / 2.0
        ymid = (ymin + ymax) / 2.0
        xran = xmax - xmid
        yran = ymax - ymid
        ax.set_xlim(xmid - xran * scale, xmid + xran * scale)
        ax.set_ylim(ymid - yran * scale, ymid + yran * scale)

    cmap = plt.cm.viridis
    all_ids = ply_ids + airfoil_ids
    max_id = max(all_ids) if all_ids else 0

    if split_view:
        # Compute max_y for offset
        all_points = outer_points[:]
        for inner in inner_list:
            all_points.extend(inner)
        for ply in line_ply_list:
            all_points.extend(ply)
        max_y = max(p.y() for p in all_points) if all_points else 0
        offset_y = 3 * max_y

        # Plot boundaries at +offset_y
        xs = [p.x() for p in outer_points] + [outer_points[0].x()]
        ys = [p.y() + offset_y for p in outer_points] + [outer_points[0].y() + offset_y]
        plt.plot(xs, ys, "r-", linewidth=2)

        colors = ["g-", "c-", "m-", "y-"]
        for idx, inner_points in enumerate(inner_list):
            xs = [p.x() for p in inner_points] + [inner_points[0].x()]
            ys = [p.y() + offset_y for p in inner_points] + [inner_points[0].y() + offset_y]
            plt.plot(xs, ys, colors[idx % len(colors)], linewidth=2)

        for idx, ply_points in enumerate(line_ply_list):
            xs = [p.x() for p in ply_points] + [ply_points[0].x()]
            ys = [p.y() + offset_y for p in ply_points] + [ply_points[0].y() + offset_y]
            color = cmap(ply_ids[idx] / max_id)
            plt.plot(xs, ys, color=color, linewidth=2)

        # Plot untrimmed lines at +offset_y
        for untrimmed in untrimmed_lines:
            xs = [p.x() for p in untrimmed]
            ys = [p.y() + offset_y for p in untrimmed]
            plt.plot(xs, ys, "k-", alpha=0.1)

        # Annotate web names at +offset_y
        for idx, line in enumerate(untrimmed_lines):
            max_y_point = max(line, key=lambda p: p.y())
            plt.text(
                max_y_point.x(),
                max_y_point.y() + offset_y,
                web_names[idx],
                fontsize=12,
                ha="center",
                va="bottom",
            )

    centroids = []
    normals = []
    inplanes = []
    idx = 0
    for face in cdt.finite_faces():
        material_id = face_material_ids[idx]
        if material_id != -1:
            p0 = face.vertex(0).point()
            p1 = face.vertex(1).point()
            p2 = face.vertex(2).point()
            cx = (p0.x() + p1.x() + p2.x()) / 3.0
            cy = (p0.y() + p1.y() + p2.y()) / 3.0
            xs = [p0.x(), p1.x(), p2.x()]
            ys = [p0.y(), p1.y(), p2.y()]
            color = cmap(material_id / max_id)
            plt.fill(xs, ys, color=color, alpha=0.5)
            centroids.append((cx, cy))
            normals.append(face_normals[idx])
            inplanes.append(face_inplanes[idx])
        idx += 1

    if not split_view:
        # Plot the input lines without trim using alpha=0.1
        for untrimmed in untrimmed_lines:
            xs = [p.x() for p in untrimmed]
            ys = [p.y() for p in untrimmed]
            plt.plot(xs, ys, "k-", alpha=0.1)

        # Annotate web names at the upper end
        for idx, line in enumerate(untrimmed_lines):
            max_y_point = max(line, key=lambda p: p.y())
            plt.text(
                max_y_point.x(),
                max_y_point.y(),
                web_names[idx],
                fontsize=12,
                ha="center",
                va="bottom",
            )

        # Plot the boundaries
        xs = [p.x() for p in outer_points] + [outer_points[0].x()]
        ys = [p.y() for p in outer_points] + [outer_points[0].y()]
        plt.plot(xs, ys, "r-", linewidth=2)

        colors = ["g-", "c-", "m-", "y-"]
        for idx, inner_points in enumerate(inner_list):
            xs = [p.x() for p in inner_points] + [inner_points[0].x()]
            ys = [p.y() for p in inner_points] + [inner_points[0].y()]
            plt.plot(xs, ys, colors[idx % len(colors)], linewidth=2)

        for idx, ply_points in enumerate(line_ply_list):
            xs = [p.x() for p in ply_points] + [ply_points[0].x()]
            ys = [p.y() for p in ply_points] + [ply_points[0].y()]
            color = cmap(ply_ids[idx] / max_id)
            plt.plot(xs, ys, color=color, linewidth=2)

    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=max_id))
    sm.set_array([])
    plt.colorbar(sm, ax=plt.gca(), label="Material ID")

    # Add quiver plot for normals and inplanes
    if centroids and normals:
        cx_list, cy_list = zip(*centroids)
        if split_view:
            cy_list = [cy - offset_y for cy in cy_list]
        nx_list, ny_list = zip(*normals)
        plt.quiver(cx_list, cy_list, nx_list, ny_list, scale=30, color='blue', alpha=0.4, width=0.0025)

    if centroids and inplanes:
        ix_list, iy_list = zip(*inplanes)
        if split_view:
            cy_list = [cy - offset_y for cy in cy_list]  # reuse
        plt.quiver(cx_list, cy_list, ix_list, iy_list, scale=30, color='red', alpha=0.4, width=0.0025)

    rescale_plot(plt.gca())
    plt.axis("equal")
    # Set to fullscreen
    fig = plt.gcf()
    if hasattr(fig.canvas.manager, 'full_screen_toggle'):
        fig.canvas.manager.full_screen_toggle()
    plt.show()

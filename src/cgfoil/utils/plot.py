"""Plotting utilities."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import math
from collections import defaultdict
from CGAL.CGAL_Kernel import Point_2
from cgfoil.utils.geometry import point_in_polygon


def plot_triangulation(
    vertices,
    faces,
    outer_points,
    inner_list,
    line_ply_list,
    untrimmed_lines,
    web_material_ids,
    skin_material_ids,
    web_names,
    face_normals,
    face_material_ids,
    face_inplanes,
    split_view=False,
    plot_filename=None,
):
    """Plot the triangulation with filled triangles colored by material id and colorbar."""

    # Increase figure size by 2 in both dimensions
    default_width, default_height = plt.rcParams['figure.figsize']
    plt.figure(figsize=(default_width + 2, default_height + 2))

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
    all_ids = web_material_ids + skin_material_ids
    max_id = max(all_ids) if all_ids else 0

    # Compute ta and tr
    x_list = [p.x() for p in outer_points]
    ta_list = [0.0]
    for i in range(1, len(outer_points)):
        dx = outer_points[i].x() - outer_points[i-1].x()
        dy = outer_points[i].y() - outer_points[i-1].y()
        dist = math.sqrt(dx**2 + dy**2)
        ta_list.append(ta_list[-1] + dist)
    total_length = ta_list[-1]
    tr_list = [t / total_length for t in ta_list]

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
            ys = [p.y() + offset_y for p in inner_points] + [
                inner_points[0].y() + offset_y
            ]
            plt.plot(xs, ys, colors[idx % len(colors)], linewidth=2)

        for idx, ply_points in enumerate(line_ply_list):
            xs = [p.x() for p in ply_points] + [ply_points[0].x()]
            ys = [p.y() + offset_y for p in ply_points] + [ply_points[0].y() + offset_y]
            if max_id == 0:
                color = cmap(0)
            else:
                color = cmap(web_material_ids[idx] / max_id)
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
    for face in faces:
        material_id = face_material_ids[idx]
        if material_id != -1:
            _, v0, v1, v2 = face
            p0 = vertices[v0][:2]
            p1 = vertices[v1][:2]
            p2 = vertices[v2][:2]
            cx = (p0[0] + p1[0] + p2[0]) / 3.0
            cy = (p0[1] + p1[1] + p2[1]) / 3.0
            xs = [p0[0], p1[0], p2[0]]
            ys = [p0[1], p1[1], p2[1]]
            if max_id == 0:
                color = cmap(0)
            else:
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
            ys = [p.y() + offset_y for p in ply_points] + [ply_points[0].y() + offset_y]
            if max_id == 0:
                color = cmap(0)
            else:
                color = cmap(web_material_ids[idx] / max_id)
            plt.plot(xs, ys, color=color, linewidth=2)

    # Add dashed axvline at position of maximum thickness
    all_points = outer_points[:]
    for inner in inner_list:
        all_points.extend(inner)
    x_to_ys = defaultdict(list)
    for p in all_points:
        x_rounded = round(p.x(), 4)
        x_to_ys[x_rounded].append(p.y())
    max_thickness = 0
    max_thickness_x = 0
    for x, ys in x_to_ys.items():
        thickness = max(ys) - min(ys)
        if thickness > max_thickness:
            max_thickness = thickness
            max_thickness_x = x
    plt.axvline(max_thickness_x, linestyle='--', color='black', linewidth=1)
    # Find indices for ta and tr at this x
    idxs = [i for i in range(len(x_list)) if abs(x_list[i] - max_thickness_x) < 1e-3]
    ta_vals = [ta_list[i] for i in idxs]
    tr_vals = [tr_list[i] for i in idxs]
    # Add text label
    rescale_plot(plt.gca())
    _, ymax = plt.ylim()
    if len(ta_vals) == 2:
        ta_str = f'{ta_vals[0]:.3f}, {ta_vals[1]:.3f}'
        tr_str = f'{tr_vals[0]:.3f}, {tr_vals[1]:.3f}'
    else:
        ta_str = f'{ta_vals[0]:.3f}' if ta_vals else 'N/A'
        tr_str = f'{tr_vals[0]:.3f}' if tr_vals else 'N/A'
    plt.text(max_thickness_x, ymax + 0.01, f'x={max_thickness_x:.3f}\nta={ta_str}\ntr={tr_str}\nthickness={max_thickness:.4f}', ha='center', va='bottom', fontsize=10, bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=max_id))
    sm.set_array([])
    plt.colorbar(sm, ax=plt.gca(), label="Material ID")

    # Add quiver plot for normals and inplanes
    if centroids and normals and inplanes:
        cx_list, cy_list = zip(*centroids)
        if split_view:
            cy_list = [cy - offset_y for cy in cy_list]
        # print(cy_list)
        nx_list, ny_list = zip(*normals)
        plt.quiver(
            cx_list,
            cy_list,
            nx_list,
            ny_list,
            scale=30,
            color="blue",
            alpha=0.5,
            width=0.0008,
        )

        ix_list, iy_list = zip(*inplanes)
        plt.quiver(
            cx_list,
            cy_list,
            ix_list,
            iy_list,
            scale=30,
            color="red",
            alpha=0.5,
            width=0.0008,
        )

    plt.axis("equal")
    plt.grid(True)
    plt.tight_layout()
    # Set to fullscreen
    fig = plt.gcf()
    if hasattr(fig.canvas.manager, "full_screen_toggle"):
        fig.canvas.manager.full_screen_toggle()
    if plot_filename:
        plt.savefig(plot_filename)
    else:
        plt.show()
"""Command line interface for cgfoil."""

from treeparse import cli, command, argument, option, group
from cgfoil.cli.mesh import mesh_from_yaml
from cgfoil.cli.plot import plot_existing_mesh
from cgfoil.cli.export import export_mesh_to_vtk, export_mesh_to_anba
from cgfoil.cli.summary import summarize_mesh
from cgfoil.cli.full import full_mesh
from cgfoil.cli.run import run_defaults

app = cli(
    name="cgfoil",
    help="CGAL-based airfoil meshing tool for generating constrained "
    "Delaunay triangulations of airfoils with plies and webs.",
    max_width=120,
    show_types=True,
    show_defaults=True,
    line_connect=True,
    theme="monochrome",
)

mesh_cmd = command(
    name="mesh",
    help="Generate mesh from YAML file.",
    callback=mesh_from_yaml,
    arguments=[
        argument(
            name="yaml_file", arg_type=str, help="Path to YAML configuration file"
        ),
    ],
    options=[
        option(
            flags=["--output-mesh", "-o"],
            arg_type=str,
            help="Output mesh file (pickle)",
        ),
        option(
            flags=["--vtk"],
            arg_type=str,
            help="Output VTK file",
        ),
    ],
    sort_key=1,
)
app.commands.append(mesh_cmd)

plot_cmd = command(
    name="plot",
    help="Plot an existing mesh.",
    callback=plot_existing_mesh,
    arguments=[
        argument(name="mesh_file", arg_type=str, help="Path to mesh file (pickle)"),
    ],
    options=[
        option(
            flags=["--plot-file", "-f"],
            dest="plot_filename",
            arg_type=str,
            help="Save plot to file",
        ),
        option(
            flags=["--split", "-s"],
            arg_type=bool,
            default=False,
            help="Enable split view plotting",
        ),
    ],
    sort_key=2,
)
app.commands.append(plot_cmd)

export_group = group(name="export", help="Export mesh to various formats.", sort_key=3)
app.subgroups.append(export_group)

vtk_cmd = command(
    name="vtk",
    help="Export mesh to VTK file.",
    callback=export_mesh_to_vtk,
    arguments=[
        argument(
            name="mesh_file",
            arg_type=str,
            help="Path to mesh file (pickle)",
            sort_key=-1,
        ),
        argument(name="vtk_file", arg_type=str, help="Output VTK file"),
    ],
    options=[
        option(
            flags=["--output", "-o"],
            dest="vtk_file",
            arg_type=str,
            help="Output VTK file",
        ),
    ],
)
export_group.commands.append(vtk_cmd)

anba_cmd = command(
    name="anba",
    help="Export mesh to ANBA format (JSON).",
    callback=export_mesh_to_anba,
    arguments=[
        argument(
            name="mesh_file",
            arg_type=str,
            help="Path to mesh file (pickle)",
            sort_key=-1,
        ),
        argument(name="anba_file", arg_type=str, help="Output ANBA file"),
    ],
    options=[
        option(
            flags=["--output", "-o"],
            dest="anba_file",
            arg_type=str,
            help="Output ANBA file",
        ),
        option(
            flags=["--matdb"],
            arg_type=str,
            help="Path to material database JSON",
            default=None,
        ),
    ],
)
export_group.commands.append(anba_cmd)

summary_cmd = command(
    name="summary",
    help="Summarize areas and masses from mesh file.",
    callback=summarize_mesh,
    arguments=[
        argument(name="mesh_file", arg_type=str, help="Path to mesh file (pickle)"),
    ],
    options=[
        option(
            flags=["--output", "-o"],
            arg_type=str,
            help="Output CSV file",
        ),
    ],
)
export_group.commands.append(summary_cmd)

full_cmd = command(
    name="full",
    help="Run full meshing pipeline.",
    callback=full_mesh,
    arguments=[
        argument(
            name="yaml_file",
            arg_type=str,
            help="Path to YAML configuration file",
            sort_key=-1,
        ),
        argument(name="output_dir", arg_type=str, help="Output directory"),
    ],
    options=[
        option(
            flags=["--output-dir", "-o"],
            dest="output_dir",
            arg_type=str,
            help="Output directory",
        ),
    ],
    sort_key=4,
)
app.commands.append(full_cmd)

run_cmd = command(
    name="run",
    help="Run meshing with defaults.",
    callback=run_defaults,
    options=[
        option(
            flags=["--plot", "-p"],
            arg_type=bool,
            default=False,
            help="Plot the triangulation",
        ),
        option(
            flags=["--vtk", "-v"],
            arg_type=str,
            help="Output VTK file",
        ),
        option(
            flags=["--file", "-f"],
            arg_type=str,
            default="naca0018.dat",
            help="Path to airfoil data file (.dat)",
        ),
        option(
            flags=["--split", "-s"],
            arg_type=bool,
            default=False,
            help="Enable split view plotting",
        ),
    ],
    sort_key=5,
)
app.commands.append(run_cmd)


def main():
    app.run()

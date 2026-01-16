"""Summary command functionality."""

import pickle
from pathlib import Path

import pandas as pd

from cgfoil.utils.logger import logger


def summarize_mesh(mesh_file: str, output=None):
    """Summarize areas and masses from mesh file."""
    with Path(mesh_file).open("rb") as f:
        mesh_result = pickle.load(f)  # noqa: S301
    rows = []
    total_mass = 0.0
    for mat_id, area in sorted(mesh_result.areas.items()):
        if mesh_result.materials and mat_id < len(mesh_result.materials):
            name = mesh_result.materials[mat_id].get("name", "N/A")
            rho = mesh_result.materials[mat_id]["rho"]
            mass = area * rho
            total_mass += mass
        else:
            name = "N/A"
            mass = float("nan")
        rows.append(
            {
                "Material ID": mat_id,
                "Material Name": name,
                "Area": area,
                "Mass/m": mass,
            },
        )
    if mesh_result.materials:
        rows.append(
            {
                "Material ID": "Total",
                "Material Name": "",
                "Area": "",
                "Mass/m": total_mass,
            },
        )
    df = pd.DataFrame(rows)
    if output:
        with Path(output).open("w") as f:
            df.to_csv(f, index=False)
        logger.info(f"Summary saved to {output}")
    logger.info(df.to_string())

"""Summary command functionality."""

from __future__ import annotations

import pickle

import pandas as pd

from cgfoil.utils.logger import logger


def summarize_mesh(mesh_file: str, output: str | None = None):
    """Summarize areas and masses from mesh file."""
    with open(mesh_file, "rb") as f:
        mesh_result = pickle.load(f)
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
        df.to_csv(output, index=False)
        logger.info(f"Summary saved to {output}")
    logger.info(df.to_string())

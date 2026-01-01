"""Export utilities for cgfoil."""

import json
import pickle
from ..core.anba import build_anba_data


def export_mesh_to_anba(mesh_file: str, anba_file: str, matdb: dict = None) -> None:
    """Export mesh result to ANBA JSON format."""
    with open(mesh_file, "rb") as f:
        mesh_result = pickle.load(f)
    data = build_anba_data(mesh_result, matdb)
    with open(anba_file, "w") as f:
        json.dump(data, f, indent=2)

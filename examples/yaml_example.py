"""Example demonstrating loading an airfoil mesh from YAML and validating with Pydantic.

The YAML demonstrates tapers (interp), conditions with multiple coordinates,
remeshing with n_elem.
"""

from pathlib import Path

import yaml

from cgfoil.core.main import run_cgfoil
from cgfoil.models import AirfoilMesh

# Load YAML configuration
yaml_file = Path(__file__).parent / "airfoil_mesh.yaml"
with yaml_file.open() as f:
    data = yaml.safe_load(f)

# Validate and create AirfoilMesh model
data["plot"] = True
data["plot_filename"] = "yaml_example.png"
data["split_view"] = True
mesh = AirfoilMesh(**data)

# Run the meshing
run_cgfoil(mesh)

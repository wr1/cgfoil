"""Example demonstrating loading an airfoil mesh from YAML and validating with Pydantic.

The YAML demonstrates tapers (interp), conditions with multiple coordinates,
remeshing with n_elem.
"""

import yaml
from pathlib import Path
from cgfoil.core.main import run_cgfoil
from cgfoil.models import AirfoilMesh

# Load YAML configuration
yaml_file = Path(__file__).parent / "airfoil_mesh.yaml"
with open(yaml_file, "r") as f:
    data = yaml.safe_load(f)

# Validate and create AirfoilMesh model
data["plot"] = False  # Disable plotting for headless CI
mesh = AirfoilMesh(**data)

# Run the meshing
run_cgfoil(mesh)

# Alternatively, generate mesh separately
# mesh_result = generate_mesh(mesh)
# plot_mesh(mesh_result)

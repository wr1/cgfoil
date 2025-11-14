"""Tests for running programmatic examples."""

import subprocess
import os
import pytest
from pathlib import Path


def test_example():
    """Test running example.py."""
    result = subprocess.run(
        ["python", "examples/example.py"], capture_output=True, text=True
    )
    assert result.returncode == 0


def test_example_list():
    """Test running example_list.py."""
    result = subprocess.run(
        ["python", "examples/example_list.py"], capture_output=True, text=True
    )
    assert result.returncode == 0


def test_yaml_example():
    """Test running yaml_example.py."""
    result = subprocess.run(
        ["python", "examples/yaml_example.py"], capture_output=True, text=True
    )
    assert result.returncode == 0


def test_example_list_web():
    """Test running example_list_web.py."""
    result = subprocess.run(
        ["python", "examples/example_list_web.py"], capture_output=True, text=True
    )
    assert result.returncode == 0


def test_example_list_web2():
    """Test running example_list_web2.py."""
    result = subprocess.run(
        ["python", "examples/example_list_web2.py"], capture_output=True, text=True
    )
    assert result.returncode == 0


def test_example_vtp_section():
    """Test running example_vtp_section.py if VTP file exists."""
    vtp_file = "airfoil_sections.vtp"
    if os.path.exists(vtp_file):
        result = subprocess.run(
            ["python", "examples/example_vtp_section.py"], capture_output=True, text=True
        )
        assert result.returncode == 0
    else:
        pytest.skip("VTP file not found")

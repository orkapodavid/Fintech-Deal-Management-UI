"""Application configuration loaded from pyproject.toml."""

import tomllib
from pathlib import Path

# Find the project root (where pyproject.toml is located)
_PROJECT_ROOT = Path(__file__).parent.parent

# Load version from pyproject.toml
def _load_version() -> str:
    """Load the project version from pyproject.toml."""
    pyproject_path = _PROJECT_ROOT / "pyproject.toml"
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "0.0.0")
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        return "0.0.0"


VERSION = _load_version()

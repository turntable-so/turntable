import importlib
import itertools
import os
import sys
from pathlib import Path
from types import ModuleType

import toml
from vinyl.lib.utils.pkg import _find_nearest_pyproject_toml_directory


def _get_root() -> Path | None:
    # Create a Path object for the start directory
    path = Path().resolve()

    # Traverse up through the parent directories
    for parent in itertools.chain([path], path.parents):
        pyproject_toml = parent / "pyproject.toml"
        if pyproject_toml.exists():
            return pyproject_toml.parent.absolute()

    return None


class PyProjectSettings:
    _toml: dict

    def __init__(self, path: Path | None = None):
        if path is None:
            path = _get_root()
            if path is None:
                raise FileNotFoundError("pyproject.toml not found")
        with open(path / "pyproject.toml") as f:
            self._toml = toml.load(f)

    def _get_setting(self, key: str) -> str | None:
        return self._toml["tool"]["vinyl"].get(key, None)


def _get_project_module_name() -> str:
    root_path = _find_nearest_pyproject_toml_directory()

    with open(root_path, "r") as file:
        data = toml.load(file)

    return data["tool"]["vinyl"]["module_name"]


def _load_project_module() -> ModuleType:
    # Backup the original sys.modules
    try:
        module_name = _get_project_module_name()
    except KeyError:
        raise ValueError("Can't find a project pyproject.toml file.")

    sys.path.append(os.getcwd())
    imported_module = importlib.import_module(module_name)
    return imported_module

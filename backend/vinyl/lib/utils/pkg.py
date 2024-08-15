import os
import pkgutil
import sys
from contextlib import contextmanager
from types import ModuleType
from typing import Any, Generator

import toml


@contextmanager
def _extend_sys_path(path: str) -> Generator[Any, Any, Any]:
    original_sys_path = list(sys.path)  # Make a copy of the original sys.path
    sys.path.append(path)
    try:
        yield
    finally:
        sys.path = original_sys_path  # Restore the original sys.path


# separating recursion out allows us to only extend sys path temporarily for top-level package
def _find_submodule_names_recursion_helper(package: str | ModuleType) -> list[str]:
    """Recursively find all submodules in a nested set of folders for the given package."""
    if isinstance(package, str):
        package = __import__(package, fromlist=[""])

    submodules = []
    for loader, name, is_pkg in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):
        submodules.append(name)
        # If the current module is a package, recurse into it
        if is_pkg:
            submodules.extend(_find_submodule_names_recursion_helper(name))
    return submodules


def _find_submodules_names(package: str | ModuleType) -> list[str]:
    if isinstance(package, str):
        package = __import__(package, fromlist=[""])
    if hasattr(package, "__path__"):
        with _extend_sys_path(package.__path__[0]):
            return list(set(_find_submodule_names_recursion_helper(package)))
    else:
        return [package.__name__]


def _find_nearest_pyproject_toml_directory(start_path: str = ".") -> str:
    """
    Search for the nearest 'pyproject.toml' starting from 'start_path' and moving up the directory tree.
    Returns the path to 'pyproject.toml' if found, otherwise None.
    """
    current_dir = os.path.abspath(start_path)
    while True:
        file_list = os.listdir(current_dir)
        parent_dir = os.path.dirname(current_dir)
        if "pyproject.toml" in file_list:
            return os.path.join(current_dir, "pyproject.toml")
        elif current_dir == parent_dir:  # If we've reached the root directory
            raise FileNotFoundError("No 'pyproject.toml' found in the directory tree.")
        else:
            current_dir = parent_dir


def _get_project_directory(start_path: str = ".") -> str:
    toml_path = _find_nearest_pyproject_toml_directory(start_path)
    with open(toml_path, "r") as file:
        data = toml.load(file)
    return os.path.join(
        os.path.dirname(toml_path), data["tool"]["vinyl"]["module_name"]
    )

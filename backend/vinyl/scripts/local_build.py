import platform
import subprocess
import sys

from vinyl.lib.utils.files import _preserve_file_state


@_preserve_file_state("pyproject.toml")
def run_build():
    try:
        # Get the current platform
        current_platform = platform.system()

        if current_platform == "Windows":
            plat = "windows"

        elif current_platform == "Linux":
            plat = "linux"

        else:
            plat = "macos"

        current_version = sys.version_info
        version = f"cp{current_version.major}{current_version.minor}-*"

        subprocess.run(
            "poetry run python scripts/cache_project_scaffolding.py", shell=True
        )

        subprocess.run(
            "poetry run python scripts/generate_autocomplete_hints.py -p vinyl",
            shell=True,
        )
        subprocess.run(
            "poetry run python scripts/set_pyproject.py --engine nuitka", shell=True
        )
        subprocess.run(
            f"CIBW_BUILD={version} poetry run cibuildwheel --platform {plat} --output-dir dist/wheelhouse",
            shell=True,
        )
    finally:
        # make sure type stubs are removed no matter what
        subprocess.run(
            "poetry run python scripts/cleanup_autocomplete_hints.py", shell=True
        )


if __name__ == "__main__":
    run_build()

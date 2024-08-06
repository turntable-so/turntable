import argparse
import subprocess
import sys

import toml


def install_dependencies(use_uv=True):
    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)

    dependencies = pyproject["project"]["dependencies"]
    dev_dependencies = pyproject["tool"]["rye"]["dev-dependencies"]

    if use_uv:
        subprocess.call(
            [
                "uv",
                "pip",
                "install",
                "--python",
                sys.executable,
                *dependencies,
                *dev_dependencies,
            ]
        )
    else:
        subprocess.call(["pip", "install", *dependencies, *dev_dependencies])


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--use-pip", action="store_true")
    args = argparser.parse_args()
    install_dependencies(not args.use_pip)

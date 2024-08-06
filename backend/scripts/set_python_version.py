import toml


def set_version(version: str):
    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)
    pyproject["tool"]["cibuildwheel"]["build"] = f"cp{version.replace('.', '')}-*"
    with open("pyproject.toml", "w") as f:
        toml.dump(pyproject, f)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--version")
    args = parser.parse_args()
    set_version(args.version)

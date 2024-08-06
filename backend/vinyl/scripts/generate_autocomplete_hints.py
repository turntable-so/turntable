import toml
import subprocess


def generate_autocomplete_hints(project_names: list = []):
    subprocess.run(
        f"poetry run stubgen --include-docstrings -p {' '.join(project_names)} -o .",
        shell=True,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project-names", nargs="+")
    args = parser.parse_args()
    generate_autocomplete_hints(args.project_names)

import glob
import os

import toml


def delete_pyi_files(directory):
    # Check if the given directory exists
    if not os.path.exists(directory):
        print(f"The directory '{directory}' does not exist.")
        return

    # Use glob.glob with recursive=True to find all .pyi files in the directory and its subdirectories
    pyi_files = glob.glob(os.path.join(directory, "**/*.pyi"), recursive=True)

    # Loop through the list of .pyi files and remove each one
    for file in pyi_files:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except OSError as e:
            print(f"Error deleting {file}: {e.strerror}")


# Replace 'your_directory_path_here' with the actual directory path

if __name__ == "__main__":
    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)
        project_name = pyproject["tool"]["poetry"]["name"]
    delete_pyi_files(project_name)

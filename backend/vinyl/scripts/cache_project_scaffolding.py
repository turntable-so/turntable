## Needs to happen because nuitka removes all .py files, and in this case, we need to keep them. We zip the folder before the build with this script.
if __name__ == "__main__":
    import shutil

    shutil.make_archive(
        "vinyl/cli/_project_scaffolding", "zip", "vinyl/cli/_project_scaffolding"
    )

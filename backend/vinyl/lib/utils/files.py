import functools
import glob
import hashlib
import os
import subprocess
import tempfile
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable

import orjson


def _create_dirs_with_init_py(end_path: str, start_dir: str = ".") -> None:
    # Ensure the start_dir is an absolute path
    start_dir = os.path.abspath(start_dir)

    # Construct the full path to the target directory
    # Split the relative path into its components
    relative_path = os.path.relpath(end_path, start_dir)
    dirs = relative_path.split(os.sep)

    # Create __init__.py along the relative path
    for i in range(1, len(dirs) + 1):
        # Construct the path up to the current depth within the relative path
        current_dir = os.path.join(start_dir, os.sep.join(dirs[:i]))
        if not os.path.exists(current_dir):
            # Create the directory if it doesn't exist
            os.makedirs(current_dir, exist_ok=True)
        init_file = os.path.join(current_dir, "__init__.py")
        if not os.path.isfile(init_file):
            # Create __init__.py if it doesn't exist
            open(init_file, "a").close()

    return None


def _file_hash(file_path: str, hash_func: Callable[..., Any] = hashlib.md5) -> str:
    hash_obj = hash_func()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def _get_directory_hashes(
    directory: str, hash_func: Callable[..., Any] = hashlib.md5
) -> dict[str, str]:
    hashes = {}
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            if os.path.isfile(file_path):
                relative_path = os.path.relpath(file_path, directory)
                hashes[relative_path] = _file_hash(file_path, hash_func)
    return hashes


def _get_changed_files(directory: str, hash_func: Callable[..., Any] = hashlib.md5):
    def decorator_check_files(func):
        @functools.wraps(func)
        def wrapper_check_files(*args, **kwargs):
            # Check file hashes before function execution
            before_hashes = _get_directory_hashes(directory, hash_func)
            func(*args, **kwargs)  # Execute the function
            # Check file hashes after function execution
            after_hashes = _get_directory_hashes(directory, hash_func)

            if before_hashes != after_hashes:
                out = {}
                for file_path in before_hashes:
                    if before_hashes[file_path] != after_hashes.get(file_path):
                        out[file_path] = (
                            before_hashes[file_path],
                            after_hashes.get(file_path),
                        )
                return out

            return {}

        return wrapper_check_files

    return decorator_check_files


def _preserve_file_state(file_path: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Read the original content of the file
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    original_content = file.read()
            else:
                original_content = None

            # Execute the function
            result = func(*args, **kwargs)

            # Check if the file content has changed
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    new_content = file.read()
                if new_content != original_content:
                    # If changed, revert to original content
                    with open(file_path, "w") as file:
                        file.write(original_content)

            return result

        return wrapper

    return decorator


def preserve_file_state_on_failure(file_path: str, overwrite=True, bytes=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Read the original content of the file
            if os.path.exists(file_path):
                with open(file_path, "r" if not bytes else "rb") as file:
                    original_content = file.read()
                if overwrite:
                    os.remove(file_path)
            else:
                original_content = None

            try:
                # Execute the function
                result = func(*args, **kwargs)

            except Exception as e:
                # Check if the file content has changed
                if os.path.exists(file_path):
                    with open(file_path, "r" if not bytes else "rb") as file:
                        new_content = file.read()
                    if original_content is None:
                        os.remove(file_path)
                    elif new_content != original_content:
                        # If changed, revert to original content
                        with open(file_path, "w" if not bytes else "wb") as file:
                            file.write(original_content)

                raise e

            return result

        return wrapper

    return decorator


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(prevdir)


def load_orjson(path):
    with open(path, "r") as f:
        contents = f.read()
    out = orjson.loads(contents)
    return out


def save_orjson(path, contents):
    to_save = orjson.dumps(contents).decode("utf-8")
    with open(path, "w") as f:
        f.write(to_save)


def ruff_format_text(content: str) -> str:
    with tempfile.NamedTemporaryFile(mode="r+", delete=True, suffix=".py") as tf:
        tf.write(content)
        tf.flush()
        subprocess.run(
            ["ruff", "format", tf.name], check=True, stdout=subprocess.DEVNULL
        )  # suppress ruff output
        with open(tf.name, "r") as f:
            formatted_content = f.read()
    return formatted_content


def adjust_path(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))


def file_exists_in_directory(file_name, directory_path):
    file_path = os.path.join(directory_path, "**", file_name)
    files = glob.glob(file_path, recursive=True)
    if len(files) > 0:
        return files[0]
    else:
        return None

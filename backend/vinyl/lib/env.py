import os
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values


@lru_cache()
def load_dotenv(dotenv_path: str | Path | None = None):
    if dotenv_path is None:
        dotenv_path = ".env"
    env_values = dotenv_values(dotenv_path)

    # Check if any op env variables are loaded
    op_variables = [k for k, v in env_values.items() if v.startswith("op://")]
    if op_variables:
        # Fetch the values, will log you in if you need
        command = f"op run --env-file={dotenv_path} --no-masking -- printenv"
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        # get the values into python
        with tempfile.NamedTemporaryFile("w+", delete=True) as f:
            f.write(result.stdout)
            f.flush()
            env_values_new = dotenv_values(f.name)
        for k, v in env_values_new.items():
            if k in op_variables:
                env_values[k] = v

    # Set the environment variables
    for k, v in env_values.items():
        os.environ[k] = v

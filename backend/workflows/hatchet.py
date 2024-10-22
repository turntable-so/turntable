import os

from dotenv import load_dotenv
from hatchet_sdk import ClientConfig, Hatchet

load_dotenv()  # we'll use dotenv to load the required Hatchet and OpenAI api keys

# load the Hatchet client token if using local docker
if hatchet_env_path := os.getenv("HATCHET_ENV_PATH"):
    load_dotenv(hatchet_env_path)

is_dev = os.getenv("DEV", "false").lower() in ("true", "t", "1")

hatchet = Hatchet(debug=is_dev)

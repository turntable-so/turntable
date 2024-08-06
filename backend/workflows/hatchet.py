import os

from dotenv import load_dotenv
from hatchet_sdk import Hatchet

load_dotenv()  # we'll use dotenv to load the required Hatchet and OpenAI api keys

# load the Hatchet client token if using local docker
if hatchet_env_path := os.getenv("HATCHET_ENV_PATH"):
    load_dotenv(hatchet_env_path)

hatchet = Hatchet(debug=True)

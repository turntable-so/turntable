import asyncio
import json
import os
import shutil
import tempfile
import uuid
import webbrowser
import zipfile
from importlib.metadata import version as get_version
from typing import Any
from urllib.parse import urlencode

import toml
import typer
import websockets
from vinyl.cli.events import Event, EventLogger
from vinyl.cli.user import DEFAULT_CREDS_PATH

from .dbt import dbt_cli
from .preview import preview_cli
from .project import project_cli
from .sources import sources_cli

CLERK_CLIENT_ID = "Vq0JUkek1jaqmY1t"


app: typer.Typer = typer.Typer(pretty_exceptions_show_locals=False)
app.add_typer(preview_cli, name="preview")
app.add_typer(sources_cli, name="sources")
app.add_typer(project_cli, name="project")
app.add_typer(dbt_cli, name="dbt")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
    ),
):
    if version:
        typer.echo(f"Vinyl version: {get_version('vinyl')}")
        return 0

    if ctx.invoked_subcommand is not None:
        return 0

    typer.echo(ctx.get_help())
    return 0


async def listen_for_event(state, stop_event):
    uri = f"wss://vinyl-cloud.onrender.com/ws/{state}"
    async with websockets.connect(uri) as websocket:
        try:
            while not stop_event.is_set():
                message = await websocket.recv()
                data = json.loads(message)
                auth = data["auth"]
                email = data["user_info"]["email"]
                user_id = data["user_info"]["user_id"]
                credentials_path = DEFAULT_CREDS_PATH
                if not credentials_path.exists():
                    credentials_path.touch()

                with open(credentials_path, "w") as f:
                    f.write(
                        json.dumps(
                            {
                                "email": email,
                                "user_id": user_id,
                                "access_token": auth["access_token"],
                                "refresh_token": auth["refresh_token"],
                            }
                        )
                    )

                print(f"Logged in as user: {email}")
                print(
                    f"Credentials saved to: {credentials_path}",
                )
                print("Successfully logged in 🎉")
                stop_event.set()
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed with error: {e}")
            stop_event.set()


@app.command("login")
def login():
    """Log into Turntable"""
    url = "https://turntable.so/sign-in"
    state_id = str(uuid.uuid4())
    params = {
        "oauth": "true",
        "client_id": CLERK_CLIENT_ID,
        "prompt": "login",
        "redirect_uri": "https://turntable.so/vinyl_redirect",
        "response_type": "code",
        "scope": "profile email",
        "state": state_id,
    }
    sign_in_url = f"{url}?{urlencode(params)}"
    typer.echo("Logging you into Turntable")
    typer.echo(
        "If your browser doesnt open automatically, please visit the following URL:"
    )
    typer.echo(sign_in_url)
    webbrowser.open(sign_in_url)
    stop_event = asyncio.Event()
    asyncio.get_event_loop().run_until_complete(listen_for_event(state_id, stop_event))
    track = EventLogger()
    track.log_event(Event.LOGIN)


@app.command("init")
def init_project(project_name: str):
    """Initialize a new Vinyl project and it's file strucutre"""
    track = EventLogger()
    track.log_event(Event.PROJECT_INIT)

    normalized_project_name = project_name.lower().replace(" ", "_")
    scaffolding_path = os.path.join(os.path.dirname(__file__), "_project_scaffolding")
    project_path = os.path.join(os.getcwd())

    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)

        tool_vinyl: Any
        tool_vinyl = pyproject["tool"]["vinyl"] = {}
        tool_vinyl["module_name"] = normalized_project_name
        tool_vinyl["tz"] = "America/Los_Angeles"
        tool_vinyl["dark-mode"] = True

        tool_ruff: Any
        tool_ruff = pyproject["tool"]["ruff"] = {}
        tool_ruff["lint"] = {}
        tool_ruff["lint"]["ignore"] = ["E711"]

    with open("pyproject.toml", "w") as f:
        toml.dump(pyproject, f)

    # create zip if it doesn't exist, will already exist in build contexts
    zip_path = os.path.join(os.path.dirname(__file__), "_project_scaffolding.zip")
    if not os.path.exists(zip_path):
        shutil.make_archive(scaffolding_path, "zip", scaffolding_path)

    # Use a temporary directory to extract the ZIP contents
    with tempfile.TemporaryDirectory() as extract_path:
        # Extract the ZIP file
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

            # copy the scaffolding to the new project path
            shutil.copytree(extract_path, project_path, dirs_exist_ok=True)

    # rename the project folder
    os.rename(
        os.path.join(project_path, "__project_name__"),
        os.path.join(project_path, normalized_project_name),
    )

    # templatize project assets
    project_assets = [
        "README.md",
        "pyproject.toml",
    ]
    asset_paths = [os.path.join(project_path, asset) for asset in project_assets]
    for path in asset_paths:
        with open(path, "r") as f:
            content = f.read()
        content = content.replace("{{PROJECT_NAME}}", normalized_project_name)
        with open(path, "w") as f:
            f.write(content)
    # change imports in the models.py file
    models_path = os.path.join(
        project_path, normalized_project_name, "models", "models.py"
    )
    with open(models_path, "r") as f:
        content = f.read()
        content_to_write = content.replace("__project_name__", normalized_project_name)
    with open(models_path, "w") as f:
        f.write(content_to_write)

    typer.echo(f"Created project at {project_path}")


if __name__ == "__main__":
    app()

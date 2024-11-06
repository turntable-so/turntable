import argparse
import subprocess

modes = ["prod", "demo", "dev", "dev-internal", "staging"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, required=False, default="prod")
    parser.add_argument(
        "--frontend",
        action="store_true",
        default=False,
        help="Enable frontend build",
    )
    parser.add_argument(
        "--backend",
        action="store_true",
        default=False,
        help="Enable backend build",
    )
    args = parser.parse_args()

    if args.mode not in modes:
        raise ValueError(f"Invalid mode: {args.mode}. Must be one of {modes}")

    env_file = ".env.local" if args.mode in ["prod", "demo"] else ".env.staging"
    docker_compose_file = (
        "docker-compose.yml"
        if args.mode == "prod"
        else f"docker-compose.{args.mode}.yml"
    )
    to_build = []
    if args.frontend:
        to_build.append("web")
    if args.backend:
        to_build.extend(["api", "worker", "scheduler"])

    if not to_build:
        command = f"docker compose -f {docker_compose_file} --env-file {env_file} up"
    else:
        command = f"docker compose -f {docker_compose_file} --env-file {env_file} build {' '.join(to_build)} && docker compose -f {docker_compose_file} --env-file {env_file} up"

    subprocess.run(command, shell=True)


if __name__ == "__main__":
    main()

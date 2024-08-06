import argparse
import os
import subprocess
from urllib.parse import urlparse

from dotenv import load_dotenv

from supabase import create_client

load_dotenv()


def get_current_git_branch():
    try:
        # Run the git command to get the current branch name
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        # The branch name is in the stdout
        branch_name = result.stdout.strip()
        return branch_name
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.strip()}")
        return None


def create_dev_db():
    current_branch = get_current_git_branch()
    if current_branch is None:
        raise ValueError("Failed to get the current branch name")
    subprocess.run(["supabase", "branches", "create", current_branch, "--experimental"])


def populate_dev_db():
    # Get prod resources
    url = os.environ.get("SUPABASE_PROD_URL")
    key = os.environ.get("SUPABASE_PROD_KEY")
    supabase = create_client(url, key)
    current_profiles = supabase.table("profiles").select("*").execute().data
    current_resources = supabase.table("resources").select("*").execute().data
    current_github_installations = (
        supabase.table("github_installations").select("*").execute().data
    )

    # Upload resources to dev
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url, key)
    supabase.table("profiles").upsert(current_profiles).execute()
    supabase.table("resources").upsert(current_resources).execute()
    supabase.table("github_installations").upsert(
        current_github_installations
    ).execute()

    # Create buckets in dev to match prod
    buckets = [b.name for b in supabase.storage.list_buckets()]
    if "artifacts" not in buckets:
        supabase.storage.create_bucket("artifacts")


def get_supbase_db_url(prod: bool = False):
    if prod:
        supabase_url = os.environ.get("SUPABASE_PROD_URL")
        supabase_password = os.environ.get("SUPABASE_PROD_PASSWORD")
        supabase_host = os.environ.get("SUPABASE_PROD_HOST")
    else:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_password = os.environ.get("SUPABASE_PASSWORD")
        supabase_host = os.environ.get("SUPABASE_HOST")

    db_name = urlparse(supabase_url).hostname.split(".")[0]
    db_url = f"postgres://postgres.{db_name}:{supabase_password}@{supabase_host}:5432/postgres"
    return db_url


def pull_db():
    db_url = get_supbase_db_url()
    subprocess.run(f"supabase db pull --db-url {db_url}", shell=True, check=True)


def dump_db():
    db_url = get_supbase_db_url(prod=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True)
    args = parser.parse_args()
    subprocess.run(
        f"supabase db dump --db-url {db_url} -f '{args.file}'", shell=True, check=True
    )


def repair_db():
    parser = argparse.ArgumentParser()
    parser.add_argument("--migration", type=str, required=True)
    parser.add_argument("--status", type=str, required=True)
    # Parse the command-line arguments
    args = parser.parse_args()
    migration = args.migration
    status = args.status
    db_url = get_supbase_db_url()
    subprocess.run(
        f"supabase migration repair --db-url {db_url} --status {status} {migration}",
        shell=True,
        check=True,
    )

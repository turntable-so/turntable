import argparse
import os
import subprocess

from dotenv import load_dotenv

from supabase import Client, ClientOptions, create_client

load_dotenv()

MIN_PASSWORD_LENGTH = 30
MAX_PASSWORD_LENGTH = 50


def run_command(command: str):
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, check=True
    )
    return result.stdout


def create_user():
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(
        url,
        key,
        options=ClientOptions(
            auto_refresh_token=False
        ),  # needed because otherwise command hangs because of thread that handles token refresh
    )
    parser = argparse.ArgumentParser(description="My script description")
    parser.add_argument("--email", type=str, help="email")
    parser.add_argument("--tenant", type=str, help="tenant id")
    args = parser.parse_args()
    metadata_attributes = {
        "app_metadata": {
            "tenant_id": args.tenant,
        }
    }

    if args.email:
        user = supabase.auth.admin.invite_user_by_email(email=args.email)

    else:
        # create 1 password item
        email = f"tenants+{args.tenant}@turntable.so"
        vault_name = "Tenants"
        op_create_command = f"op item create --vault={vault_name} --category=login --title={args.tenant} --url=https://www.supabase.co --generate-password username={email}"
        run_command(op_create_command)

        # retrieve the password
        op_get_command = f"op read op://{vault_name}/{args.tenant}/password"
        credentials = {
            "email": email,
            "password": run_command(op_get_command).strip(),
        }

        # create the supabase user
        user = supabase.auth.sign_up(
            credentials
        )  # automatically signs in the user. use this vs. admin create user to ensure email is pre-verified
        supabase.auth.sign_out()  # sign out the user to we can set their app data using admin credentials

    # set tenant id in app metadata (more secure than user metadata)
    supabase.auth.admin.update_user_by_id(user.user.id, attributes=metadata_attributes)


if __name__ == "__main__":
    create_user()

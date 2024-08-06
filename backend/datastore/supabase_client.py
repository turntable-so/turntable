import os

from dotenv import load_dotenv

from supabase import Client, ClientOptions, create_client

load_dotenv()


url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase_user_email: str = os.environ.get("SUPABASE_USER_EMAIL")
supabase_user_password: str = os.environ.get("SUPABASE_USER_PASSWORD")

supabase: Client = create_client(
    url,
    key,
    options=ClientOptions(
        auto_refresh_token=os.getenv("DAEMON") == "true"
    ),  # needed because otherwise command hangs because of thread that handles token refresh if user is signed in
)

if supabase_user_email is not None and supabase_user_password is not None:
    # sign in with the user
    supabase.auth.sign_in_with_password(
        {"email": supabase_user_email, "password": supabase_user_password}
    )

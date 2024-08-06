## Setting up supabase

1. Install the supabase CLI by running `brew install supabase/tap/supabase`.
2. Run supabase login and login in the GUI.
3. Run `supabase link --project-ref uknnswxmayalzancjxhg` to link the project to the CLI.
4. Make sure you have the prod url and key in your `.env` file as `SUPABASE_PROD_URL` and `SUPABASE_PROD_KEY` so you don't accidentally run commands on prod.

## Setting up One Password

1. Make sure you have 1Password desktop installed. Visit [here](https://1password.com/downloads/mac/) if you don't.
2. Install the 1Password CLI by running `brew install 1password-cli`.
3. Follow [these instructions](https://developer.1password.com/docs/cli/get-started/#step-2-turn-on-the-1password-desktop-app-integration) to enable the 1Password CLI integration with the desktop app. This will allow you to automatically get pinged with a touch ID request when you need to sign in.
4. Run `op signin` to sign in to your 1Password account.
5. To access secrets in your environment, add them to your .env file as op://{vault}/{item}/{field}. For example, `SUPABASE_PROD_KEY=op://supabase/prod/key`.

## Creating a new branch in Supabase

If you need to work with a dev database in supabase, perform the following steps:

1. [IMPORTANT] Publish your branch.
2. Run `rye run create_dev_db` to create a new branch in supabase.
3. Update the `.env` file in `backend` with the new `SUPABASE_URL` and `SUPABASE_KEY` values which can be found by visiting the project page[here](https://supabase.com/dashboard/project/uknnswxmayalzancjxhg/settings/api) and switching to the new branch.
4. Wait until the branch is fully spun up (likely ~1 minute).
5. Populate the new branch with minimal resource data by running `rye run populate_dev_db`.

## Merging schema changes

If you need to merge schema changes from the main branch to your branch, perform the following steps:

1. Make the necessary changes in the Supabase UI
2. Once ready, run `rye run pull_db` to pull the changes into your local branch
3. Once you submit the PR on main, the changes will be merged into the main branch

## Create a new user

1. Make sure you are using the intended Supabase URL and associated key. Note that this may be a dev branch.
2. Run either `rye run create_user --tenant_id {tenant_id}` or `rye run create_user --tenant_id {tenant_id} --email {email}` to create a new user. The tenant_id is the id for the organization in clerk. If an email is provided, the user will be sent an account sign up link directly. Otherwise, the user will be created and then the credentials uploaded to 1Password in the `Tenants` vault, where you can create a link to share with the user.

## Other notes

- If you are running the server or the worker, you will need to turn on token auto-refresh when accessing the DB. To do this, set `DAEMON` to `true` in your `.env` file.
- If you are running the tests locally, you may need to run them on main to ensure that the tests work properly. Some require real data. We will change this eventually.
- If you ever need to recreate the policies or indexes, you can run `rye run python scripts/create_policies_sql.py` and copy the outputed sql into the Supabase SQL editor. This is much faster than updating the policies/indexes one by one in the UI.
- If you encounter any issues with migrations that need repair, use `rye run repair_db` with the appropriate arguments.

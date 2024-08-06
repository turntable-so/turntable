import argparse


def main():
    # Creating argument parser
    parser = argparse.ArgumentParser(
        description="Script to process tenant and repo IDs"
    )

    # Adding arguments
    parser.add_argument("--tenant_id", type=str, help="Tenant ID")
    parser.add_argument("--repo_id", type=str, help="Repo ID")

    # Parsing arguments
    args = parser.parse_args()

    # Checking if both arguments are provided
    if not args.tenant_id or not args.repo_id:
        parser.error("Both --tenant_id and --repo_id are required.")
    else:
        print("Success! Tenant ID:", args.tenant_id, "Repo ID:", args.repo_id)


if __name__ == "__main__":
    main()

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import IntegrityError, DataError


class Command(BaseCommand):
    help = "Sets workspace_id for AssetError objects, handling null values and non-existent workspaces"

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            try:
                # Check if workspace with id 3 exists
                cursor.execute("SELECT COUNT(*) FROM app_workspace WHERE id = 3")
                workspace_exists = cursor.fetchone()[0] > 0

                if not workspace_exists:
                    self.stdout.write(
                        self.style.WARNING(
                            "Workspace with id 3 does not exist. Creating it..."
                        )
                    )
                    cursor.execute(
                        "INSERT INTO app_workspace (id, name) VALUES (3, 'Default Workspace')"
                    )

                # Update AssetError records, excluding those with null workspace_id
                cursor.execute(
                    """
                    UPDATE app_asseterror 
                    SET workspace_id = 3 
                    WHERE workspace_id IS NOT NULL
                """
                )

                # Get the number of updated rows
                cursor.execute(
                    "SELECT COUNT(*) FROM app_asseterror WHERE workspace_id = 3"
                )
                updated_count = cursor.fetchone()[0]

                # Get the number of rows with null workspace_id
                cursor.execute(
                    "SELECT COUNT(*) FROM app_asseterror WHERE workspace_id IS NULL"
                )
                null_count = cursor.fetchone()[0]

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully updated {updated_count} AssetError records"
                    )
                )
                if null_count > 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f"{null_count} AssetError records still have null workspace_id"
                        )
                    )

            except (IntegrityError, DataError) as e:
                self.stdout.write(self.style.ERROR(f"Error occurred: {str(e)}"))

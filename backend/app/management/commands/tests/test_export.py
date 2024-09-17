import os
import time

import pytest
from django.core.management import call_command


@pytest.mark.django_db
def test_data_export():
    call_command("export")

    ## check if a file exists
    dir = "exports/"
    relevant_file_times = [
        os.path.getctime(f"{dir}{f}") for f in os.listdir(dir) if f.endswith(".zip")
    ]
    assert any(
        [time.time() - t < 5 for t in relevant_file_times]
    ), "Exported file not found in exports folder"

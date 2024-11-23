import pytest

from app.workflows.utils import task


def test_bad_task():
    with pytest.raises(ValueError, match="must have 'self' as first parameter"):

        @task
        def bad_task():
            pass


def test_good_task():
    @task
    def good_task(self):
        pass

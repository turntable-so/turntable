import json
import sys
import time
import uuid

import pytest
from django_celery_results.models import TaskResult

from api.serializers import TaskSerializer
from app.workflows.utils import task
from vinyl.lib.utils.sequence import _get_list_depth, _get_list_key_depth


def test_bad_task():
    with pytest.raises(ValueError, match="must have 'self' as first parameter"):

        @task
        def bad_task():
            pass


def test_good_task():
    @task
    def good_task(self):
        pass


if "pytest" in sys.modules:
    # only initialize these tasks if we're running the tests. Otherwise, will pollute our actual worker.

    def _check_children_before_completion(task_id: str):
        """
        Show that the task has children initialized in the TaskResult even though it hasn't finished yet. This is an important customization we've made, and our subtask functionality will fail if this is not the case.
        """
        time.sleep(0.5)
        meta = json.loads(TaskResult.objects.get(task_id=task_id).meta)
        children = meta["children"]
        assert children

    @task
    def leaf(self, workspace_id: str, parent_id: str):
        _check_children_before_completion(parent_id)
        return 3

    @task
    def middle(self, workspace_id: str, parent_id: str):
        _check_children_before_completion(parent_id)

        # run subtasks
        t = leaf.si(workspace_id=workspace_id, parent_id=self.request.id)
        return self.run_subtasks(t, t)

    @task
    def root(self, workspace_id: str, parent_id: str):
        t = middle.si(workspace_id=workspace_id, parent_id=self.request.id)
        return self.run_subtasks(t)


@pytest.mark.django_db(transaction=True)
def test_nested_task(custom_celery):
    task_id = str(uuid.uuid4())
    result = root.si(workspace_id="1", parent_id=task_id).apply_async(task_id=task_id)
    assert result.get() == [[3, 3]]

    # Test serializer
    trs = TaskResult.objects.all()
    serializer = TaskSerializer(trs, many=True)
    for tr in serializer.data:
        # confirm the structure of the result and subtasks are the same
        result_depth = _get_list_depth(tr["result"])
        subtask_depth = _get_list_key_depth(tr["subtasks"], "subtasks")
        assert result_depth == subtask_depth

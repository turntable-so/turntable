if __name__ == "__main__":
    import django

    django.setup()


from app.core.e2e import DataHubDBParser
from app.models import Resource
from workflows.utils.debug import ContextDebugger

if __name__ == "__main__":
    context = ContextDebugger(
        {"input": {"resource_id": "caef609b-c268-4726-b644-3fbcc9b60714"}}
    )
    resource = Resource.objects.get(id=context.workflow_input()["resource_id"])
    parser = DataHubDBParser(resource, "looker.duckdb")
    parser.parse()
    DataHubDBParser.combine_and_upload([parser], resource)

# from vinyl.lib.project import Project
import json
import pickle

from vinyl.lib.errors import VinylError

# print("bootstrapping")
# project = Project.bootstrap()
# print("get sql project")
# sqlproject = project.get_sql_project(
#     None,
#     None,
#     None,
#     False,
# )
# print("optimizing")
# sqlproject.optimize()
# print("getting lineage")
# sqlproject.get_lineage([])
# print("stitch lineage together")
# result = sqlproject.stitch_lineage(None, None, None)


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, VinylError):
            return obj.to_json()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


lineage = pickle.load(open("lineage.pkl", "rb"))
# Serializing VinylError
dbt_lineage_nodes = [
    node
    for node in lineage.get("column_lineage").get("nodes")
    if node["id"].startswith("internal_project")
]

dbt_lineage_links = [
    node
    for node in lineage.get("column_lineage").get("links")
    if node["source"].startswith("internal_project")
    or node["target"].startswith("internal_project")
]
ntypes = []
for link in dbt_lineage_links:
    ntypes.extend(list(link["ntype"]))

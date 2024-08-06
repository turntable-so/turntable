from vinyl.lib.asset import resource
from vinyl.lib.connect import FileConnector


@resource
def local_filesystem():
    return FileConnector(path="data")

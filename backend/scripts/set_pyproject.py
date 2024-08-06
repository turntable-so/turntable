import copy
import email.utils

import toml


def set_pyproject():
    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)

    poetry = copy.deepcopy(pyproject["tool"]["poetry"])
    build_system = pyproject["build-system"]
    build_system["requires"] = ["setuptools>=42", "wheel", "nuitka", "toml"]
    build_system["build-backend"] = "nuitka.distutils.Build"

    if "project" not in pyproject:
        pyproject["project"] = {}
    proj = pyproject["project"]

    proj["name"] = poetry["name"]
    proj["version"] = poetry["version"]
    proj["description"] = poetry["description"]
    adj_authors = [email.utils.parseaddr(auth) for auth in poetry["authors"]]
    proj["authors"] = [{"name": auth[0], "email": auth[1]} for auth in adj_authors]
    proj["scripts"] = poetry["scripts"]
    proj["license"] = {"file": poetry["license"]}
    proj["requires-python"] = poetry["dependencies"]["python"]
    proj["readme"] = poetry["readme"]
    proj["classifiers"] = poetry["classifiers"]

    proj["dynamic"] = ["dependencies"]

    with open("pyproject.toml", "w") as f:
        toml.dump(pyproject, f)


if __name__ == "__main__":
    set_pyproject()

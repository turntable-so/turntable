import ast
import os
import re
from typing import Any


class ClassInfo:
    _name: str
    _excluded_attrs: list[str]
    _attributes_dict: dict[str, str]

    def __init__(self, name: str, excluded_attributes: list[str] = []):
        self._name = name
        self._excluded_attrs = excluded_attributes
        self._attributes_dict = {}

    def _add_attribute(self, key, value):
        if key not in self._excluded_attrs:
            self._attributes_dict[key] = value


class ClassFinder(ast.NodeVisitor):
    _classes: list[ClassInfo]
    _excluded_attrs: list[str]

    def __init__(self, excluded_attributes: list[str] = []):
        self._classes = []
        self._excluded_attrs = excluded_attributes

    def visit_ClassDef(self, node):
        class_info = ClassInfo(node.name, self._excluded_attrs)

        # Look for assignments that occur directly in the class body
        for body_item in node.body:
            # Only handle type-annotated assignments with a value
            if isinstance(body_item, ast.AnnAssign) and body_item.value is not None:
                if isinstance(body_item.target, ast.Name):
                    # Add the attribute along with its value's AST
                    class_info._add_attribute(
                        body_item.target.id, ast.unparse(body_item.value)
                    )

        self._classes.append(class_info)
        self.generic_visit(node)  # Continue visiting child nodes


def _find_classes_and_attributes(file_path: str) -> dict[str, Any]:
    if not os.path.exists(file_path):
        return {}

    with open(file_path, "r") as file:
        source = file.read()

    tree = ast.parse(source)
    finder = ClassFinder(
        [
            "_table",
            "_unique_name",
            "_path",
            "_twin_path",
            "_row_count",
            "_schema",
            "_database",
        ]
    )
    finder.visit(tree)

    return finder._classes[0]._attributes_dict


# more accurate
def _get_imports_from_file_ast(file_path: str) -> str:
    with open(file_path, "r") as file:
        source = file.read()

    imports = ""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports += ast.unparse(node)
        elif isinstance(node, ast.ImportFrom):
            imports += ast.unparse(node)
        elif isinstance(node, ast.ClassDef):
            break
        imports += "\n"

    return imports


# more literal
def _get_imports_from_file_regex(file_path: str, regex: str = "@source") -> str:
    with open(file_path, "r") as file:
        source = file.read()

    parts = re.split(regex, source, re.MULTILINE)

    if len(parts) == 1:
        return ""

    return parts[0]

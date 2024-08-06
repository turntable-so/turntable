import inspect
import os
import shutil
from vinyl.lib.table import VinylTable
from vinyl.lib.column import VinylColumn


nested_functions = {
    "ArrayFunctions": "array",
    "MathFunctions": "math",
    "URLFunctions": "url",
    "RegexFunctions": "re",
    "StringFunctions": "str",
    "MapFunctions": "dict",
    "StructFunctions": "obj",
    "TemporalFunctions": "dt",
}


# Function to extract docstrings from all methods in a class
def extract_method_details(cls):
    methods_details = {}
    for name, member in inspect.getmembers(
        cls, predicate=lambda x: inspect.isfunction(x) or inspect.ismethod(x)
    ):
        if name in nested_functions:
            nested_class_methods = extract_method_details(member)
            prefix = nested_functions[name]
            nested_class_methods = {
                prefix + "." + k: v for k, v in nested_class_methods.items()
            }
            methods_details.update(nested_class_methods)
        if not name.startswith("_"):
            # Extracting the signature
            sig = inspect.signature(member)
            method_info = {
                "docstring": inspect.getdoc(member),
                "arguments": {},
                "return_type": (
                    sig.return_annotation
                    if sig.return_annotation is not inspect.Signature.empty
                    else None
                ),
            }
            # Extracting argument details
            for param_name, param in sig.parameters.items():
                if param_name == "self" or param_name == "cls":
                    continue  # Skip 'self' and 'cls' parameters
                arg_info = {
                    "type": (
                        param.annotation
                        if param.annotation is not inspect.Parameter.empty
                        else None
                    ),
                    "default": (
                        param.default
                        if param.default is not inspect.Parameter.empty
                        else None
                    ),
                    "required": param.default is inspect.Parameter.empty,
                }
                method_info["arguments"][param_name] = arg_info
            methods_details[name] = method_info
    return methods_details


def create_paramfield_text(details):
    param_fields = []
    for param, info in details["arguments"].items():
        # Assuming the parameters are part of the body payload
        param_type = (
            info["type"] if info["type"] else "string"
        )  # Defaulting to string if type is not specified
        required = "true" if info["required"] else "false"
        default_value = info["default"]
        # Constructing the ParamField text
        required = "{" + required + "}"
        param_field_core = (
            f"""ParamField body="{param}" type="{param_type}" required={required}"""
        )
        if default_value:
            param_field_core += f"""default="{default_value}" """
        param_field = f"""<{param_field_core}>
</ParamField>"""
        # Adding the constructed ParamField to the list
        param_fields.append(param_field)
    return "\n\n".join(param_fields)


# Example usage with the 'method1' from 'MyClass'
if os.path.exists("/Users/ian/code/docs/reference/table"):
    shutil.rmtree("/Users/ian/code/docs/reference/table")

os.mkdir("/Users/ian/code/docs/reference/table")
methods = extract_method_details(VinylTable)
table_method_entries = []


def create_param_accordion(details):
    if not details["arguments"]:
        return ""
    return f"""<Accordion title="Parameters">
  {create_paramfield_text(details)}
</Accordion>
"""


for name, details in methods.items():
    table_method_entries.append(
        f"""
## {name}
{details['docstring']}

{create_param_accordion(details)}
---
"""
    )

path = "/Users/ian/code/docs/reference/table.mdx"
with open(path, "w") as f:
    body = "\n".join(table_method_entries)
    f.write(
        f"""---
title: "Table Operations"
---
{body}
"""
    )


# Example usage with the 'method1' from 'MyClass'
if os.path.exists("/Users/ian/code/docs/reference/column"):
    shutil.rmtree("/Users/ian/code/docs/reference/column")

os.mkdir("/Users/ian/code/docs/reference/column")
methods = extract_method_details(VinylColumn)
other_functions = {}
standard_functions = []
for name, details in methods.items():
    if "." in name:
        group_name = name.split(".")[0]
        if group_name not in other_functions:
            other_functions[group_name] = []
        other_functions[group_name].append((name, details))
    else:
        standard_functions.append((name, details))


def group_name_title(group_name):
    if group_name == "math":
        return "Math Operations"
    elif group_name == "re":
        return "Regex Operations"
    elif group_name == "str":
        return "String Operations"
    elif group_name == "obj":
        return "Struct Operations"
    elif group_name == "dt":
        return "Datetime Operations"
    elif group_name == "dict":
        return "Map Operations"
    elif group_name == "url":
        return "URL Operations"
    elif group_name == "array":
        return "Array Operations"

    raise ValueError(f"cannot find a pairing for {group_name}")


method_entries = []

for function in standard_functions:
    name, details = function
    if name in nested_functions.keys():
        continue
    parameters = create_param_accordion(details)
    method_entries.append(
        f"""## {name}
{details['docstring']}
{parameters}
"""
    )

path = "/Users/ian/code/docs/reference/column/standard.mdx"
with open(path, "w") as f:
    body = "\n".join(method_entries)
    f.write(
        f"""---
title: Standard Operations
---
{body}
"""
    )

for group_name, functions in other_functions.items():
    path = f"/Users/ian/code/docs/reference/column/{group_name}.mdx"
    method_entries = []
    for name, details in functions:
        parameters = create_param_accordion(details)
        method_entries.append(
            f"""## {name}
{details['docstring']}
{parameters}
    """
        )
    with open(path, "w") as f:
        body = "\n".join(method_entries)
        f.write(
            f"""---
title: "{group_name_title(group_name)}"
---
{body}
    """
        )

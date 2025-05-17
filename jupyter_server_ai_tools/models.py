import inspect
from typing import Any, Callable, Dict, Optional, get_type_hints

from pydantic import BaseModel, model_validator


def python_type_to_json_type(py_type: Any) -> str:
    mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }
    return mapping.get(py_type, "string")


class ToolDefinition(BaseModel):
    """
    A structured representation of a tool with an associated callable and metadata.

    This model is used to register functions as tools in Jupyter server extensions.
    Users can provide a function and optionally supply structured metadata describing
    the tool's interface. If metadata is not provided, it is automatically inferred
    from the callable's name, docstring, and type annotations.

    Attributes:
        callable (Callable): The Python function to be registered as a tool.
        metadata (Optional[Dict[str, Any]]): A dictionary representing the tool's
            metadata. This should follow a JSON Schema–like format. If not provided,
            metadata will be inferred from the callable using `inspect` and `get_type_hints`.
    """

    callable: Callable
    metadata: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    @classmethod
    def fill_metadata(cls, values):
        fn = values.get("callable")
        metadata = values.get("metadata")

        if not metadata and fn:  # allows users to simply pass the callable
            sig = inspect.signature(fn)
            type_hints = get_type_hints(fn)

            properties = {}
            for name, param in sig.parameters.items():
                py_type = type_hints.get(name, str)
                json_type = python_type_to_json_type(py_type)
                properties[name] = {"type": json_type}

            values["metadata"] = {
                "name": fn.__name__,
                "description": fn.__doc__ or "",
                "inputSchema": {  # MCP uses inputSchema for paramter definitions
                    "type": "object",
                    "properties": properties,
                    "required": list(sig.parameters),
                },
            }

        return values

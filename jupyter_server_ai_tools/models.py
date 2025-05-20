import inspect
from typing import Any, Callable, Dict, Optional, get_type_hints

import jsonschema
from jsonschema import ValidationError as SchemaValidationError
from pydantic import BaseModel, model_validator

from jupyter_server_ai_tools.schema import MCP_TOOL_SCHEMA


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
    callable: Callable
    metadata: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    @classmethod
    def fill_metadata(cls, values):
        fn = values.get("callable")
        metadata = values.get("metadata")

        if not metadata and fn:
            sig = inspect.signature(fn)
            type_hints = get_type_hints(fn)

            properties = {}
            for name, param in sig.parameters.items():
                py_type = type_hints.get(name, str)
                json_type = python_type_to_json_type(py_type)
                properties[name] = {"type": json_type}

            metadata = {
                "name": fn.__name__,
                "description": fn.__doc__ or "",
                "inputSchema": {
                    "type": "object",
                    "properties": properties,
                    "required": list(sig.parameters),
                },
            }

        if metadata:
            try:
                jsonschema.validate(instance=metadata, schema=MCP_TOOL_SCHEMA)
            except SchemaValidationError as e:
                raise ValueError(
                    f"Invalid tool metadata for '{metadata.get('name', 'unknown')}': {e.message}"
                ) from e

        values["metadata"] = metadata
        return values

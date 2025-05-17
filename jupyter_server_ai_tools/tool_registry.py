import importlib
from typing import Any, Dict, List, Optional

import jsonschema

from jupyter_server_ai_tools.models import ToolDefinition


def find_tools(
    extension_manager, schema: Optional[dict] = None, return_metadata_only: bool = False
) -> List[Dict[str, Any]]:
    """
    Discover and return tools from installed Jupyter server extensions.

    Each extension must expose a `jupyter_server_extension_tools()` function
    that returns a list of `ToolDefinition` instances.

    Parameters:
        extension_manager: The Jupyter Server extension manager instance.
        schema (Optional[dict]): An optional JSON Schema to validate each tool's
            metadata against. Validation is only applied if the user has provided a
            schema to validate against.
        return_metadata_only (bool): If True, return only the `metadata` for each tool.
            If False (default), return the full dictionary representation of the tool,
            including both `metadata` and `callable`.

    Returns:
        A list of dictionaries, each representing a tool. The contents depend on
        `return_metadata_only`. Tools without required fields or invalid structure
        will raise errors or be skipped.
    """
    discovered = []

    for ext_name in extension_manager.extensions:
        try:
            module = importlib.import_module(ext_name)

            if hasattr(module, "jupyter_server_extension_tools"):
                tool_provider = getattr(module, "jupyter_server_extension_tools")
                if callable(tool_provider):
                    tools = tool_provider()
                    if not isinstance(tools, list):
                        raise TypeError(
                            f"`jupyter_server_extension_tools()` in '{ext_name}' must return a list"
                        )

                    for tool in tools:
                        if not isinstance(tool, ToolDefinition):
                            raise TypeError(f"Tool from '{ext_name}' must be a ToolDefinition")

                        if schema:
                            jsonschema.validate(instance=tool.metadata, schema=schema)

                        if return_metadata_only:
                            if not isinstance(tool.metadata, dict):
                                raise ValueError("Tool metadata must be a dict")
                            discovered.append(tool.metadata)
                        else:
                            discovered.append(tool.dict())
        except jsonschema.ValidationError as ve:
            print(f"[find_tools] Schema validation error in '{ext_name}': {ve.message}")
        except Exception as e:
            print(f"[find_tools] Failed to load tools from '{ext_name}': {e}")

    return discovered

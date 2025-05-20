import importlib
import logging
from typing import Any, Dict, List, cast

from jupyter_server_ai_tools.models import ToolDefinition

logger = logging.getLogger(__name__)


def find_tools(extension_manager, return_metadata_only: bool = False) -> List[Dict[str, Any]]:
    """
    Discover and return tools from installed Jupyter server extensions.

    Each extension must expose a `jupyter_server_extension_tools()` function
    that returns a list of `ToolDefinition` instances.

    Parameters:
        extension_manager: The Jupyter Server extension manager instance.
        return_metadata_only (bool): If True, return only the `metadata` for each tool.
            If False (default), return the full dictionary representation of the tool,
            including both `metadata` and `callable`.

    Returns:
        A list of dictionaries, each representing a tool. Invalid tools are skipped with warnings.
    """
    discovered = []

    for ext_name in extension_manager.extensions:
        try:
            module = importlib.import_module(ext_name)

            tool_provider = getattr(module, "jupyter_server_extension_tools", None)
            if not callable(tool_provider):
                continue

            tools = tool_provider()

            if not isinstance(tools, list):
                raise TypeError(
                    f"`jupyter_server_extension_tools()` in '{ext_name}' must return a list"
                )

            for tool in tools:
                if not isinstance(tool, ToolDefinition):
                    raise TypeError(f"Tool from '{ext_name}' is not a ToolDefinition instance")

                if return_metadata_only:
                    discovered.append(cast(Dict[str, Any], tool.metadata))
                else:
                    discovered.append(tool.model_dump(mode="python"))

        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to import tools from '{ext_name}': {e}")
        except (TypeError, ValueError) as e:
            logger.warning(f"Tool definition error in '{ext_name}': {e}")
        except Exception as e:
            logger.exception(f"Unexpected error while loading tools from '{ext_name}': {e}")

    return discovered

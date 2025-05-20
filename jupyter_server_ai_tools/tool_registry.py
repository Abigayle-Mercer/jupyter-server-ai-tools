import asyncio
import importlib
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

from jupyter_server_ai_tools.models import ToolDefinition

logger = logging.getLogger(__name__)


# -----------------------
# Tool Finder
# -----------------------


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


# -----------------------
# Tool call parsers
# -----------------------


def parse_openai_tool_call(call: Dict) -> Tuple[str, Dict]:
    fn = call.get("function", {})
    name = fn.get("name")
    arguments = json.loads(fn.get("arguments", "{}"))
    return name, arguments


def parse_anthropic_tool_call(call: Dict) -> Tuple[str, Dict]:
    return cast(str, call.get("name")), cast(Dict, call.get("input", {}))


def parse_mcp_tool_call(call: Dict) -> Tuple[str, Dict]:
    return cast(str, call.get("name")), cast(Dict, call.get("input", {}))


def parse_vercel_tool_call(call: Dict) -> Tuple[str, Dict]:
    return cast(str, call.get("name")), cast(Dict, call.get("arguments", {}))


PARSER_MAP: Dict[str, Callable[[Dict[str, Any]], Tuple[str, Dict[str, Any]]]] = {
    "openai": parse_openai_tool_call,
    "anthropic": parse_anthropic_tool_call,
    "mcp": parse_mcp_tool_call,
    "vercel": parse_vercel_tool_call,
}

# -----------------------
# Tool runner
# -----------------------


async def run_tool(
    extension_manager: Any,
    tool_calls: List[Dict[str, Any]],
    parse_fn: Optional[Union[str, Callable[[Dict[str, Any]], Tuple[str, Dict[str, Any]]]]] = None,
) -> List[Any]:
    """
    Execute a sequence of tools from structured tool call objects.

    Parameters:
        extension_manager: The Jupyter Server extension manager
        tool_calls: List of tool call objects in varied formats
        parse_fn: Either a string (e.g. "openai", "mcp") or a function to extract (name, arguments)

    Returns:
        A list of results or error dictionaries
    """
    # Resolve parser
    if isinstance(parse_fn, str):
        if parse_fn not in PARSER_MAP:
            return [
                {"error": f"Unknown parser '{parse_fn}'. Valid parsers: {list(PARSER_MAP.keys())}"}
            ]
        parse_fn = PARSER_MAP[parse_fn]
    elif parse_fn is None:
        parse_fn = PARSER_MAP["mcp"]  # default parser

    # Discover and build tool registry
    callable_registry: Dict[str, Callable] = {}
    try:
        tool_defs = find_tools(extension_manager, return_metadata_only=False)
        for tool in tool_defs:
            name = tool["metadata"]["name"]
            callable_registry[name] = tool["callable"]
    except Exception as e:
        logger.exception("Failed to build callable registry")
        return [{"error": f"Failed to load tools: {str(e)}"}]

    results = []

    # go through tool calls and build results list
    for i, call in enumerate(tool_calls):
        try:
            name, args = parse_fn(call)
            if not isinstance(name, str) or not isinstance(args, dict):
                raise ValueError("Parser must return (str, dict)")
        except Exception as e:
            results.append({"error": f"Tool call #{i + 1} failed to parse: {str(e)}", "call": call})
            continue

        try:
            fn = callable_registry[name]
            logger.info(f"Running tool #{i + 1}: {name} with args: {args}")
            if asyncio.iscoroutinefunction(fn):  # this is so I can run async notebook tools
                result = await fn(**args)
            else:
                result = fn(**args)
            results.append(result)
        except Exception as e:
            results.append(
                {"error": f"Tool call #{i + 1} execution failed: {str(e)}", "call": call}
            )

    return results

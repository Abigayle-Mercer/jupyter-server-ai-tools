from .extension import Extension
from .tool_registry import (
    find_tools,
    parse_anthropic_tool_call,
    parse_mcp_tool_call,
    parse_openai_tool_call,
    parse_vercel_tool_call,
    run_tools,
)

__all__ = [
    "find_tools",
    "run_tools",
    "parse_openai_tool_call",
    "parse_anthropic_tool_call",
    "parse_mcp_tool_call",
    "parse_vercel_tool_call",
]

__version__ = "0.1.2"


def _jupyter_server_extension_points():
    return [{"module": "jupyter_server_ai_tools", "app": Extension}]

from .extension import Extension
from .tool_registry import find_tools

__all__ = ["find_tools"]

__version__ = "0.1.0"


def _jupyter_server_extension_points():
    return [{"module": "jupyter_server_ai_tools", "app": Extension}]

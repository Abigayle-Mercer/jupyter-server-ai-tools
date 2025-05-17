from types import ModuleType
from typing import Any, cast
from unittest.mock import Mock, patch

from jupyter_server_ai_tools.models import ToolDefinition
from jupyter_server_ai_tools.tool_registry import find_tools


def test_tool_definition_metadata_inference():
    def greet(name: str, age: int):
        """Say hello"""
        return f"Hello {name}, age {age}"

    tool = ToolDefinition(callable=greet)
    assert tool.metadata is not None

    assert tool.metadata["name"] == "greet"
    assert tool.metadata["description"] == "Say hello"
    assert tool.metadata["inputSchema"]["required"] == ["name", "age"]
    assert tool.metadata["inputSchema"]["properties"]["name"]["type"] == "string"
    assert tool.metadata["inputSchema"]["properties"]["age"]["type"] == "integer"


def test_find_tools_returns_metadata_only():
    def say_hi(user: str):
        """Simple tool"""
        return f"Hi {user}"

    tool = ToolDefinition(callable=say_hi)

    fake_module = cast(Any, ModuleType("fake_ext"))
    fake_module.jupyter_server_extension_tools = lambda: [tool]

    extension_manager = Mock()
    extension_manager.extensions = ["fake_ext"]

    with patch("importlib.import_module", return_value=fake_module):
        result = find_tools(extension_manager, return_metadata_only=True)

    assert isinstance(result, list)
    assert result[0]["name"] == "say_hi"
    assert "callable" not in result[0]


def test_find_tools_returns_full_tool_definition():
    def echo(msg: str):
        """Repeat message"""
        return msg

    tool = ToolDefinition(callable=echo)

    fake_module = cast(Any, ModuleType("fake_ext"))
    fake_module.jupyter_server_extension_tools = lambda: [tool]

    extension_manager = Mock()
    extension_manager.extensions = ["another_ext"]

    with patch("importlib.import_module", return_value=fake_module):
        result = find_tools(extension_manager, return_metadata_only=False)

    assert isinstance(result, list)
    assert result[0]["metadata"]["name"] == "echo"
    assert callable(result[0]["callable"])

import logging
from types import ModuleType
from typing import Any, cast
from unittest.mock import Mock, patch

import pytest

from jupyter_server_ai_tools.models import ToolDefinition
from jupyter_server_ai_tools.tool_registry import find_tools

# ---------------------------------------------------------------------
# ToolDefinition Tests
# ---------------------------------------------------------------------


def test_tool_definition_metadata_inference():
    """
    Test that ToolDefinition correctly infers metadata from a function's
    name, docstring, parameter names, and type annotations.
    """

    def greet(name: str, age: int):
        """Say hello"""
        return f"Hello {name}, age {age}"

    tool = ToolDefinition(callable=greet)
    metadata = tool.metadata

    assert metadata is not None
    assert metadata["name"] == "greet"
    assert metadata["description"] == "Say hello"
    assert metadata["inputSchema"]["required"] == ["name", "age"]
    assert metadata["inputSchema"]["properties"]["name"]["type"] == "string"
    assert metadata["inputSchema"]["properties"]["age"]["type"] == "integer"


def test_metadata_infers_all_supported_types():
    """
    Test that ToolDefinition infers all supported JSON types correctly from Python types.
    """

    def func(a: str, b: int, c: float, d: bool, e: list, f: dict):
        """Covers all mapped Python types"""
        return None

    tool = ToolDefinition(callable=func)
    metadata = tool.metadata

    assert metadata is not None
    props = metadata["inputSchema"]["properties"]
    required = metadata["inputSchema"]["required"]

    assert set(required) == {"a", "b", "c", "d", "e", "f"}
    assert props["a"]["type"] == "string"
    assert props["b"]["type"] == "integer"
    assert props["c"]["type"] == "number"
    assert props["d"]["type"] == "boolean"
    assert props["e"]["type"] == "array"
    assert props["f"]["type"] == "object"


def test_tooldefinition_raises_on_invalid_metadata():
    """
    Test that invalid MCP metadata (missing inputSchema) raises a ValueError.
    """

    def greet(name: str):
        return f"Hi {name}"

    invalid_metadata = {
        "name": "greet",
        "description": "Greet someone",
        # Missing "inputSchema"
    }

    with pytest.raises(ValueError) as exc_info:
        ToolDefinition(callable=greet, metadata=invalid_metadata)

    assert "inputSchema" in str(exc_info.value)
    assert "greet" in str(exc_info.value)


# ---------------------------------------------------------------------
# find_tools() Tests
# ---------------------------------------------------------------------


def test_find_tools_returns_metadata_only():
    """
    Test that find_tools() returns only metadata when return_metadata_only=True.
    """

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
    """
    Test that find_tools() returns full ToolDefinition dicts with callable when
    return_metadata_only=False.
    """

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


def test_find_tools_skips_non_tooldefinition(caplog):
    """
    Test that find_tools() skips invalid tool entries that are not ToolDefinition instances.
    """
    bad_tool = {"name": "not_a_real_tool", "description": "I am not a ToolDefinition instance"}

    fake_module = cast(Any, ModuleType("bad_ext"))
    fake_module.jupyter_server_extension_tools = lambda: [bad_tool]

    extension_manager = Mock()
    extension_manager.extensions = ["bad_ext"]

    with patch("importlib.import_module", return_value=fake_module), caplog.at_level(
        logging.WARNING
    ):
        tools = find_tools(extension_manager)

    assert tools == []
    assert any("Tool from 'bad_ext' is not a ToolDefinition" in m for m in caplog.messages)


def test_find_tools_skips_extensions_without_hook():
    """
    Test that find_tools() skips extensions that do not define jupyter_server_extension_tools().
    """
    fake_module = cast(Any, ModuleType("no_hook_ext"))  # No tool function

    extension_manager = Mock()
    extension_manager.extensions = ["no_hook_ext"]

    with patch("importlib.import_module", return_value=fake_module):
        result = find_tools(extension_manager)

    assert result == []

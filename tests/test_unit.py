import logging
import warnings
from types import ModuleType
from typing import Any, cast
from unittest.mock import Mock, patch

import pytest

from jupyter_server_ai_tools.models import ToolDefinition
from jupyter_server_ai_tools.tool_registry import find_tools, run_tools


def safe_tool(callable_fn, metadata=None):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=ResourceWarning)
        return ToolDefinition(callable=callable_fn, metadata=metadata)


# ---------------------------------------------------------------------
# ToolDefinition Tests
# ---------------------------------------------------------------------


def test_tool_definition_metadata_inference():
    def greet(name: str, age: int):
        """Say hello"""
        return f"Hello {name}, age {age}"

    tool = safe_tool(greet)
    metadata = tool.metadata

    assert metadata is not None
    assert metadata["name"] == "greet"
    assert metadata["description"] == "Say hello"
    assert metadata["inputSchema"]["required"] == ["name", "age"]
    assert metadata["inputSchema"]["properties"]["name"]["type"] == "string"
    assert metadata["inputSchema"]["properties"]["age"]["type"] == "integer"


def test_metadata_infers_all_supported_types():
    def func(a: str, b: int, c: float, d: bool, e: list, f: dict):
        return None

    tool = safe_tool(func)
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
    def greet(name: str):
        return f"Hi {name}"

    invalid_metadata = {
        "name": "greet",
        "description": "Greet someone",
    }

    with pytest.raises(ValueError) as exc_info:
        safe_tool(greet, metadata=invalid_metadata)

    assert "inputSchema" in str(exc_info.value)
    assert "greet" in str(exc_info.value)


# ---------------------------------------------------------------------
# find_tools() Tests
# ---------------------------------------------------------------------


def test_find_tools_returns_metadata_only():
    def say_hi(user: str):
        return f"Hi {user}"

    tool = safe_tool(say_hi)

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
        return msg

    tool = safe_tool(echo)

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
    fake_module = cast(Any, ModuleType("no_hook_ext"))  # No tool function
    extension_manager = Mock()
    extension_manager.extensions = ["no_hook_ext"]

    with patch("importlib.import_module", return_value=fake_module):
        result = find_tools(extension_manager)

    assert result == []


# ---------------------------------------------------------------------
# run_tools() Tests
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_tools_sync_function_executes_correctly():
    def say_hello(user: str) -> str:
        return f"Hello {user}"

    tool = safe_tool(say_hello)
    ext_mod = cast(Any, ModuleType("mock_ext"))
    ext_mod.jupyter_server_extension_tools = lambda: [tool]

    extension_manager = Mock()
    extension_manager.extensions = ["mock_ext"]

    with patch("importlib.import_module", return_value=ext_mod):
        results = await run_tools(
            extension_manager,
            tool_calls=[{"name": "say_hello", "input": {"user": "Abigayle"}}],
            parse_fn="mcp",
        )

    assert results == ["Hello Abigayle"]


@pytest.mark.asyncio
async def test_run_tools_async_function_executes_correctly():
    async def shout(message: str) -> str:
        return message.upper()

    tool = safe_tool(shout)
    ext_mod = cast(Any, ModuleType("mock_async"))
    ext_mod.jupyter_server_extension_tools = lambda: [tool]

    extension_manager = Mock()
    extension_manager.extensions = ["mock_async"]

    with patch("importlib.import_module", return_value=ext_mod):
        results = await run_tools(
            extension_manager,
            tool_calls=[{"name": "shout", "input": {"message": "hi"}}],
            parse_fn="mcp",
        )

    assert results == ["HI"]


@pytest.mark.asyncio
async def test_run_tools_parser_failure_returns_error():
    def say_hi(user: str) -> str:
        return f"Hi {user}"

    tool = safe_tool(say_hi)
    ext_mod = cast(Any, ModuleType("bad_parser"))
    ext_mod.jupyter_server_extension_tools = lambda: [tool]

    extension_manager = Mock()
    extension_manager.extensions = ["bad_parser"]

    def bad_parser(_: dict) -> tuple:
        raise ValueError("Bad parser")

    with patch("importlib.import_module", return_value=ext_mod):
        results = await run_tools(
            extension_manager, tool_calls=[{"some": "value"}], parse_fn=bad_parser
        )

    assert isinstance(results[0], dict)
    assert "failed to parse" in results[0]["error"]


@pytest.mark.asyncio
async def test_run_tools_with_unknown_tool_name():
    def tool_a(name: str) -> str:
        return f"Hello {name}"

    tool = safe_tool(tool_a)
    ext_mod = cast(Any, ModuleType("missing_tool"))
    ext_mod.jupyter_server_extension_tools = lambda: [tool]

    extension_manager = Mock()
    extension_manager.extensions = ["missing_tool"]

    with patch("importlib.import_module", return_value=ext_mod):
        results = await run_tools(
            extension_manager,
            tool_calls=[{"name": "not_registered", "input": {"x": 1}}],
            parse_fn="mcp",
        )

    assert "Tool call #1 execution failed" in results[0]["error"]


@pytest.mark.asyncio
async def test_run_tools_with_custom_parser():
    def my_tool(x: int) -> int:
        return x + 1

    tool = safe_tool(my_tool)
    ext_mod = cast(Any, ModuleType("custom_parser_ext"))
    ext_mod.jupyter_server_extension_tools = lambda: [tool]

    extension_manager = Mock()
    extension_manager.extensions = ["custom_parser_ext"]

    def custom_parser(call: dict) -> tuple[str, dict]:
        return call["custom_name"], call["args"]

    with patch("importlib.import_module", return_value=ext_mod):
        results = await run_tools(
            extension_manager,
            tool_calls=[{"custom_name": "my_tool", "args": {"x": 5}}],
            parse_fn=custom_parser,
        )

    assert results == [6]


@pytest.mark.asyncio
async def test_run_tools_parser_returns_invalid_format():
    def dummy(x: int) -> int:
        return x

    tool = safe_tool(dummy)
    ext_mod = cast(Any, ModuleType("bad_return"))
    ext_mod.jupyter_server_extension_tools = lambda: [tool]

    extension_manager = Mock()
    extension_manager.extensions = ["bad_return"]

    def invalid_parser(_: dict) -> Any:
        return None  # invalid

    with patch("importlib.import_module", return_value=ext_mod):
        results = await run_tools(
            extension_manager, tool_calls=[{"some": "data"}], parse_fn=invalid_parser
        )

    assert "failed to parse" in results[0]["error"]
    assert "non-iterable" in results[0]["error"]

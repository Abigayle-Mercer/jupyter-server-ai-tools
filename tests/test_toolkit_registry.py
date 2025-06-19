import pytest
from typing import Callable
from jupyter_server_ai_tools.models import Tool, Toolkit, ToolSet, ToolkitRegistry, ToolkitSet

# Existing tests from previous file...
# (Keep all the existing tests from the previous file)


def test_toolkit_find_tools():
    def read_func():
        pass

    def write_func():
        pass

    def execute_func():
        pass

    tool1 = Tool(callable=read_func, read=True)
    tool2 = Tool(callable=write_func, write=True)
    tool3 = Tool(callable=execute_func, execute=True)

    toolkit = Toolkit(name="TestToolkit")
    toolkit.add_tool(tool1)
    toolkit.add_tool(tool2)
    toolkit.add_tool(tool3)

    read_tools = toolkit.find_tools(read=True)
    write_tools = toolkit.find_tools(write=True)
    execute_tools = toolkit.find_tools(execute=True)

    assert len(read_tools) == 1
    assert tool1 in read_tools

    assert len(write_tools) == 1
    assert tool2 in write_tools

    assert len(execute_tools) == 1
    assert tool3 in execute_tools


def test_toolkit_registry_initialization():
    registry = ToolkitRegistry(toolkits=ToolkitSet())
    assert len(registry.toolkits) == 0


def test_toolkit_registry_register_toolkit():
    def sample_func():
        pass

    tool = Tool(callable=sample_func, read=True)
    toolkit1 = Toolkit(name="Toolkit1", tools=ToolSet({tool}))
    toolkit2 = Toolkit(name="Toolkit2", tools=ToolSet({tool}))

    registry = ToolkitRegistry(toolkits=ToolkitSet())
    registry.register_toolkit(toolkit1)
    registry.register_toolkit(toolkit2)

    assert len(registry.toolkits) == 2
    assert toolkit1 in registry.toolkits
    assert toolkit2 in registry.toolkits


def test_toolkit_registry_duplicate_toolkit():
    toolkit = Toolkit(name="DuplicateToolkit")
    registry = ToolkitRegistry(toolkits=ToolkitSet())

    registry.register_toolkit(toolkit)

    with pytest.raises(ValueError, match="Toolkit with name 'DuplicateToolkit' already exists."):
        registry.register_toolkit(toolkit)


def test_toolkit_registry_get_toolkit():
    def read_func():
        pass

    def write_func():
        pass

    read_tool = Tool(callable=read_func, read=True)
    write_tool = Tool(callable=write_func, write=True)

    toolkit = Toolkit(name="TestToolkit")
    toolkit.add_tool(read_tool)
    toolkit.add_tool(write_tool)

    registry = ToolkitRegistry(toolkits=ToolkitSet())
    registry.register_toolkit(toolkit)

    # Get toolkit with read tools
    read_toolkit = registry.get_toolkit("TestToolkit", read=True)
    assert read_toolkit.name == "TestToolkit"
    assert len(read_toolkit.tools) == 1
    assert read_tool in read_toolkit.tools

    # Get toolkit with write tools
    write_toolkit = registry.get_toolkit("TestToolkit", write=True)
    assert write_toolkit.name == "TestToolkit"
    assert len(write_toolkit.tools) == 1
    assert write_tool in write_toolkit.tools


def test_toolkit_registry_get_toolkit_not_found():
    registry = ToolkitRegistry(toolkits=ToolkitSet())

    with pytest.raises(
        LookupError, match="Tookit with name='NonExistentToolkit' not found in registry."
    ):
        registry.get_toolkit("NonExistentToolkit")


def test_toolkit_registry_get_toolkit_no_matching_tools():
    def read_func():
        pass

    read_tool = Tool(callable=read_func, read=True)
    toolkit = Toolkit(name="TestToolkit")
    toolkit.add_tool(read_tool)

    registry = ToolkitRegistry(toolkits=ToolkitSet())
    registry.register_toolkit(toolkit)

    # Try to get toolkit with write tools when only read tools exist
    result = registry.get_toolkit("TestToolkit", write=True)
    assert result.name == "TestToolkit"
    assert len(result.tools) == 0

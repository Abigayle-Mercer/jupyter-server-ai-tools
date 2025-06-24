import pytest

from jupyter_server_ai_tools.models import Tool, Toolkit, ToolkitRegistry, ToolkitSet, ToolSet


def test_toolkit_find_tools():
    """Test the find_tools method of the Toolkit class."""
    # Create a toolkit
    toolkit = Toolkit(name="test_toolkit")

    # Create tools with different permission combinations
    read_only_tool = Tool(callable=lambda: None, name="read_only", read=True)
    write_tool = Tool(callable=lambda: None, name="write_tool", write=True)
    execute_tool = Tool(callable=lambda: None, name="execute_tool", execute=True)
    delete_tool = Tool(callable=lambda: None, name="delete_tool", delete=True)
    read_execute_tool = Tool(callable=lambda: None, name="read_execute", read=True, execute=True)
    write_execute_tool = Tool(callable=lambda: None, name="write_execute", write=True, execute=True)
    all_perms_tool = Tool(
        callable=lambda: None, name="all_perms", read=True, write=True, execute=True, delete=True
    )
    no_perms_tool = Tool(callable=lambda: None, name="no_perms")

    # Add tools to the toolkit
    toolkit.add_tool(read_only_tool)
    toolkit.add_tool(write_tool)
    toolkit.add_tool(execute_tool)
    toolkit.add_tool(delete_tool)
    toolkit.add_tool(read_execute_tool)
    toolkit.add_tool(write_execute_tool)
    toolkit.add_tool(all_perms_tool)
    toolkit.add_tool(no_perms_tool)

    # Test 1: Default parameters (all False)
    default_tools = toolkit.find_tools()
    assert len(default_tools) == 0, "No tools should be returned with default parameters"

    # Test 2: Find tools with read permission
    read_tools = toolkit.find_tools(read=True)
    assert len(read_tools) == 5
    assert read_only_tool in read_tools
    assert write_tool in read_tools  # write implies read
    assert read_execute_tool in read_tools
    assert write_execute_tool in read_tools
    assert all_perms_tool in read_tools
    assert execute_tool not in read_tools
    assert delete_tool not in read_tools
    assert no_perms_tool not in read_tools

    # Test 3: Find tools with write permission
    write_tools = toolkit.find_tools(write=True)
    assert len(write_tools) == 3  # Same as read because write implies read
    assert write_tool in write_tools
    assert write_execute_tool in write_tools
    assert all_perms_tool in write_tools
    assert read_only_tool not in write_tools
    assert read_execute_tool not in write_tools
    assert execute_tool not in write_tools
    assert delete_tool not in write_tools
    assert no_perms_tool not in write_tools

    # Test 4: Find tools with execute permission (note the unusual logic here)
    execute_tools = toolkit.find_tools(execute=True)
    assert len(execute_tools) == 4
    assert (
        execute_tool not in execute_tools
    )  # Because the condition is (execute and not tool.execute)
    assert read_execute_tool not in execute_tools
    assert write_execute_tool not in execute_tools
    assert all_perms_tool not in execute_tools
    assert read_only_tool in execute_tools
    assert write_tool in execute_tools
    assert delete_tool in execute_tools
    assert no_perms_tool in execute_tools

    # Test 5: Find tools with delete permission
    delete_tools = toolkit.find_tools(delete=True)
    assert len(delete_tools) == 2
    assert delete_tool in delete_tools
    assert all_perms_tool in delete_tools
    assert read_only_tool not in delete_tools
    assert write_tool not in delete_tools
    assert execute_tool not in delete_tools
    assert read_execute_tool not in delete_tools
    assert write_execute_tool not in delete_tools
    assert no_perms_tool not in delete_tools

    # Test 6: Combined permissions (read and delete)
    read_delete_tools = toolkit.find_tools(read=True, delete=True)
    assert len(read_delete_tools) == 6
    assert read_only_tool in read_delete_tools
    assert write_tool in read_delete_tools
    assert delete_tool in read_delete_tools
    assert read_execute_tool in read_delete_tools
    assert write_execute_tool in read_delete_tools
    assert all_perms_tool in read_delete_tools
    assert execute_tool not in read_delete_tools
    assert no_perms_tool not in read_delete_tools

    # Test 7: All permissions
    all_perm_tools = toolkit.find_tools(read=True, write=True, execute=True, delete=True)
    assert len(all_perm_tools) == 7
    assert read_only_tool in all_perm_tools
    assert write_tool in all_perm_tools
    assert delete_tool in all_perm_tools
    assert no_perms_tool in all_perm_tools
    assert read_execute_tool in all_perm_tools
    assert write_execute_tool in all_perm_tools
    assert all_perms_tool in all_perm_tools


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

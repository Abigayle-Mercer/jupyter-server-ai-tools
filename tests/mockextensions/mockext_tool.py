from jupyter_server_ai_tools.models import ToolDefinition


def say_hello(name: str):
    '''Say hello to a user.'''
    return f"Hello, {name}!"


def jupyter_server_extension_tools():
    tool = ToolDefinition(callable=say_hello)
    return [tool]


def _jupyter_server_extension_points():
    return [{"module": "tests.mockextensions.mockext_tool"}]


def _load_jupyter_server_extension(serverapp):
    serverapp.log.info("Mock extension loaded.")

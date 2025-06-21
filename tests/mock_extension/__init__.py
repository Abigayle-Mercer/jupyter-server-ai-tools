from jupyter_server_ai_tools.models import Tool, Toolkit, ToolSet


def say_hello(name: str):
    """Say hello to a user."""
    return f"Hello, {name}!"

def _jupyter_server_extension_points():
    return [{"module": "tests.mock_extension"}]

def _load_jupyter_server_extension(serverapp):
    serverapp.log.info("Mock extension loaded.")

async def _start_jupyter_server_extension(serverapp):
    registry = serverapp.web_app.settings["toolkit_registry"]
    if registry:
        toolset = ToolSet({ Tool(callable=callable) })
        registry.register_toolkit(
            Toolkit(name="hello_toolkit", tools=toolset)
        )
        serverapp.log.info("Added toolkit to registry.")
    else:
        serverapp.log.warning(
            f"toolkit_registry not found in {serverapp.web_app.settings}."
        )

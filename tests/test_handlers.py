import json

import pytest


@pytest.fixture
def jp_server_config():
    return {
        "ServerApp": {
            "jpserver_extensions": {
                "jupyter_server_ai_tools": True,
                "tests.mockextensions.mockext_tool": True,
            }
        }
    }


async def test_tools_handler_with_mock_extension(jp_fetch):
    response = await jp_fetch("jupyter_server_ai_tools", "tools")
    assert response.code == 200

    payload = json.loads(response.body)
    assert "discovered_tools" in payload
    tools = payload["discovered_tools"]
    assert isinstance(tools, list)
    assert tools[0]["name"] == "say_hello"
    assert "inputSchema" in tools[0]

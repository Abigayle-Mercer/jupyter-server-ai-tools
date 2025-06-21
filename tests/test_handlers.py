import asyncio
import json

import pytest


@pytest.fixture
def jp_server_config():
    return {
        "ServerApp": {
            "jpserver_extensions": {
                "jupyter_server_ai_tools": True,
                "tests.mock_extension": True,
            }
        }
    }


async def test_toolkit_handler(jp_fetch):
    response = await jp_fetch("api", "toolkits")
    assert response.code == 200

    toolkits = json.loads(response.body)
    assert isinstance(toolkits, list)
    assert len(toolkits) == 1

    toolkit = toolkits[0]
    assert toolkit["name"] == "hello_toolkit"
    assert len(toolkit.tools) == 1

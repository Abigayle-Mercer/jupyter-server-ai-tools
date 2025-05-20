# 🧠 jupyter-server-ai-tools

[![CI](https://github.com/Abigayle-Mercer/jupyter-server-ai-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/Abigayle-Mercer/jupyter-server-ai-tools/actions/workflows/ci.yml)

A Jupyter Server extension for discovering and aggregating callable tools from other extensions.

This project provides a structured way for extensions to declare tools using `ToolDefinition` objects, and for agents or other consumers to retrieve those tools — with optional metadata validation.

______________________________________________________________________

## ✨ Features

- ✅ Simple, declarative `ToolDefinition` API
- ✅ Automatic metadata inference from function signature and docstring

- ✅ Tool discovery across all installed Jupyter extensions
- ✅ Clean separation between metadata and callable execution

______________________________________________________________________

## 📦 Install

```bash
pip install jupyter_server_ai_tools
```

To install for development:

```bash
git clone https://github.com/Abigayle-Mercer/jupyter-server-ai-tools.git
cd jupyter-server-ai-tools
pip install -e ".[lint,test]"
```

## Usage

#### Expose tools in your own extensions:

```python
from jupyter_server_ai_tools.models import ToolDefinition

def greet(name: str):
    """Say hello to someone."""
    return f"Hello, {name}!"

def jupyter_server_extension_tools():
    return [ToolDefinition(callable=greet)]
```

#### Discover tools from all extensions:

```python
from jupyter_server_ai_tools.tool_registry import find_tools

tools = find_tools(extension_manager)
```

## 🧪 Running Tests

```bash
pip install -e ".[test]"
pytest
```

## 🧼 Linting and Formatting

```bash
pip install -e ".[lint]"
bash .github/workflows/lint.sh
```

## Tool Output Example

Given the `greet()` tool above, `find_tools(return_metadata_only=True)` will return:

```json
[
  {
    "name": "greet",
    "description": "Say hello to someone.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "name": { "type": "string" }
      },
      "required": ["name"]
    }
  }
]
```

## Impact

This system enables:

- Extension authors to register tools with minimal effort
- Agent builders to dynamically discover and bind tools
- Optional schema enforcement when needed
- Future compatibility with MCP and OpenAPI-based agents

## 🧹 Uninstall

```bash
pip uninstall jupyter_server_ai_tools
```

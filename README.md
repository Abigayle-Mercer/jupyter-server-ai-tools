# 🧠 jupyter-server-ai-tools

[![CI](https://github.com/Abigayle-Mercer/jupyter-server-ai-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/Abigayle-Mercer/jupyter-server-ai-tools/actions/workflows/ci.yml)

A Jupyter Server extension for discovering and aggregating callable tools from other extensions.

This project provides a structured way for extensions to declare tools using `Tool` objects, and for agents or other consumers to retrieve those tools.

______________________________________________________________________

## ✨ Features

- ✅ Simple, declarative `Toolkit` API for registering callable tools
- ✅ Toolkit registration with unique names
- ✅ Retrieve toolkits by name and capabilities
- ✅ Clean separation between tool metadata and callable execution
- ✅ Optional tool capability filtering (read, write, execute)

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
from jupyter_server_ai_tools.models import Tool, Toolkit

def greet(name: str):
    """Say hello to someone."""
    return f"Hello, {name}!"

# In the extension app
def start(self):
    # Get the registry from the extension manager
    registry = serverapp.extension_manager.extensions.get("jupyter_server_ai_tools")
    
    # Create a tool
    greet_tool = Tool(callable=greet, read=True)
    
    # Create a toolkit
    greeting_toolkit = Toolkit(name="GreetingToolkit")
    greeting_toolkit.add_tool(greet_tool)
    
    # Register the toolkit
    registry.register_toolkit(greeting_toolkit)
```

#### Retrieve Toolkits:

```python
# Get a specific toolkit
greeting_toolkit = registry.get_toolkit("GreetingToolkit")

# Get toolkit with specific tool capabilities
read_toolkits = registry.get_toolkit("GreetingToolkit", read=True)
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

## Impact

This system enables:

- Extension authors to register tools with minimal effort
- Flexible tool discovery and retrieval
- Capability-based tool filtering

## 🧹 Uninstall

```bash
pip uninstall jupyter_server_ai_tools

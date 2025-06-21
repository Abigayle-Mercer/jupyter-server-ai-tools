from .app import AIServerToolsApp

__version__ = "0.1.2"


def _jupyter_server_extension_points():
    return [
        {
            "module": "jupyter_server_ai_tools", 
            "app": AIServerToolsApp
        }
    ]

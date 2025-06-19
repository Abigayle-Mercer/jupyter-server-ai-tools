from jupyter_server.extension.application import ExtensionApp

from .handlers import ToolkitHandler
from .models import Toolkit, ToolkitRegistry


class AiServerToolsApp(ExtensionApp):
    name = "jupyter_server_ai_tools"  
    load_other_extensions = True

    handlers = [
        (r"api/toolkits", ToolkitHandler),
    ]

    def initialize_settings(self):
        self._registry = ToolkitRegistry()
        self.settings["toolkit_registry"] = self._registry

    def register_toolkit(self, toolkit: Toolkit):
        self._registry.register_toolkit(toolkit)

    def get_toolkit(
        self, 
        name: str, 
        read: bool = False, 
        write: bool = False, 
        execute: bool = False, 
        delete: bool = False
    ) -> Toolkit:
        return self._registry.get_toolkit(
            name=name, read=read, write=write, execute=execute, delete=delete
        )

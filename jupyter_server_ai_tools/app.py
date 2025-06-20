from jupyter_server.extension.application import ExtensionApp

from .handlers import ToolkitHandler
from .models import Toolkit, ToolkitRegistry


class AiServerToolsApp(ExtensionApp):
    name = "jupyter_server_ai_tools"  
    load_other_extensions = True

    handlers = [
        (r"api/toolkits", ToolkitHandler),
    ]

    @property
    def toolkit_registry(self):
        return self.settings["toolkit_registry"]

    def initialize_settings(self):
        self.settings["toolkit_registry"] = ToolkitRegistry()

    def register_toolkit(self, toolkit: Toolkit):
        self.toolkit_registry.register_toolkit(toolkit)

    def get_toolkit(
        self, 
        name: str, 
        read: bool = False, 
        write: bool = False, 
        execute: bool = False, 
        delete: bool = False
    ) -> Toolkit:
        return self.toolkit_registry.get_toolkit(
            name=name, read=read, write=write, execute=execute, delete=delete
        )

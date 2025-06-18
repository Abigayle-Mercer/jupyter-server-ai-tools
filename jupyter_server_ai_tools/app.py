from jupyter_server.extension.application import ExtensionApp
from jupyter_server.utils import url_path_join
from traitlets import Instance, Unicode

from .handlers import ListToolInfoHandler
from .models import Toolkit, ToolkitRegistry


class AiServerToolsApp(ExtensionApp):
    # Required traits
    name = "jupyter_server_ai_tools"  # is this the right name?
    default_url = Unicode("/jupyter_server_ai_tools").tag(config=True)
    load_other_extensions = True

    @property
    def toolkit_registry(self) -> ToolkitRegistry | None:
        return self.settings.get("toolkit_registry", None)


    def initialize_handlers(self):
        assert self.serverapp is not None
        base_url = self.serverapp.web_app.settings["base_url"]
        route_pattern = url_path_join(base_url, self.default_url, "tools")
        self.serverapp.web_app.add_handlers(".*$", [(route_pattern, ListToolInfoHandler)])

    def initialize_settings(self):
        self.settings["toolkit_registry"] = ToolkitRegistry()

    def register_toolkit(self, toolkit: Toolkit):
        self.toolkit_registry.register_toolkit(toolkit)

    def get_toolkit(
        self, name: str, read: bool, write: bool, execute: bool, delete: bool
    ) -> Toolkit:
        pass

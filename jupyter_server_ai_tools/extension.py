from jupyter_server.extension.application import ExtensionApp
from jupyter_server.utils import url_path_join
from traitlets import Unicode

from .handlers import ListToolInfoHandler


class Extension(ExtensionApp):
    # Required traits
    name = "jupyter_server_ai_tools"  # is this the right name?
    default_url = Unicode("/jupyter_server_ai_tools").tag(config=True)
    load_other_extensions = True

    def initialize_handlers(self):
        assert self.serverapp is not None
        base_url = self.serverapp.web_app.settings["base_url"]
        route_pattern = url_path_join(base_url, self.default_url, "tools")
        self.serverapp.web_app.add_handlers(".*$", [(route_pattern, ListToolInfoHandler)])

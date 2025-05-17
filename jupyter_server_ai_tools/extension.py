from jupyter_server.extension.application import ExtensionApp
from jupyter_server.utils import url_path_join
from traitlets import Unicode

from .handlers import ListToolInfoHandler


class Extension(ExtensionApp):
    # Required traits
    name = "jupyter-server-ai-tools"  # is this the right name?
    default_url = Unicode("/jupyter-server-ai-tools").tag(config=True)
    load_other_extensions = True

    def initialize_handlers(self):
        """Register API route handlers."""
        assert self.serverapp is not None
        base_url = self.serverapp.web_app.settings["base_url"]
        route_pattern = url_path_join(base_url, self.default_url, "tools")

        self.handlers.extend(
            [
                (route_pattern, ListToolInfoHandler),
            ]
        )

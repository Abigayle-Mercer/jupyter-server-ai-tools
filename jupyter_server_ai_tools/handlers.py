import json

import tornado
from jupyter_server.base.handlers import APIHandler


class ToolkitHandler(APIHandler):
    
    @tornado.web.authenticated
    async def get(self):
        assert self.serverapp is not None
        registry = self.settings["toolkit_registry"]
        toolkits = registry.list_toolkits()
        self.finish(toolkits.model_dump())

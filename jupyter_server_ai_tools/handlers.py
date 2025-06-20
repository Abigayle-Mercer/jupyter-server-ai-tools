import json

import tornado
from jupyter_server.base.handlers import APIHandler


class ToolkitHandler(APIHandler):

    @property
    def toolkit_registry(self):
        return self.settings["toolkit_registry"]
    
    @tornado.web.authenticated
    async def get(self):
        assert self.serverapp is not None
        toolkits = self.toolkit_registry.list_toolkits()
        self.finish(toolkits.model_dump_json())
        

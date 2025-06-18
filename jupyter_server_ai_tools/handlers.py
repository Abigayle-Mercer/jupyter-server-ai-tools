import json

import tornado
from jupyter_server.base.handlers import APIHandler


class ListToolInfoHandler(APIHandler):
    @tornado.web.authenticated
    async def get(self):
        assert self.serverapp is not None
        # If metadata_only=True, raw_tools is already safe
        self.finish(json.dumps({"discovered_tools": []}))

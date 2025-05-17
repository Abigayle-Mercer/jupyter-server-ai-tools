import json

import tornado
from jupyter_server.base.handlers import APIHandler

from jupyter_server_ai_tools.tool_registry import find_tools


class ListToolInfoHandler(APIHandler):
    @tornado.web.authenticated
    async def get(self):
        metadata_only = True  # Optionally make this dynamic from query param later
        assert self.serverapp is not None
        raw_tools = find_tools(self.serverapp.extension_manager, return_metadata_only=metadata_only)

        # If metadata_only=True, raw_tools is already safe
        self.finish(json.dumps({"discovered_tools": raw_tools}))

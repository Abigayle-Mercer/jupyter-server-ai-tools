MCP_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "inputSchema": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["object"]},
                "properties": {"type": "object"},
                "required": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["type", "properties"],
        },
        "annotations": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "readOnlyHint": {"type": "boolean"},
                "destructiveHint": {"type": "boolean"},
                "idempotentHint": {"type": "boolean"},
                "openWorldHint": {"type": "boolean"},
            },
            "additionalProperties": True,
        },
    },
    "required": ["name", "inputSchema"],
    "additionalProperties": False,
}

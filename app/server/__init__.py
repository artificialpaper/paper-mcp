"""MCP Server implementation for Paper AI Ecosystem."""
from __future__ import annotations
import sys
import json
import asyncio
from paper_common.logging.logger import get_logger
from ..tools import MCPToolManager
from ..resources import MCPResourceManager
from ..prompts import MCPPromptManager

log = get_logger(__name__)

MCP_PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "paper-mcp"
SERVER_VERSION = "1.0.0"


class MCPServer:
    """Model Context Protocol (MCP) JSON-RPC Server over stdio / async transport."""

    def __init__(self) -> None:
        self._tools = MCPToolManager()
        self._resources = MCPResourceManager()
        self._prompts = MCPPromptManager()
        self._initialized = False

    def _capabilities(self) -> dict:
        return {
            "tools": {"listChanged": False},
            "resources": {"subscribe": False, "listChanged": False},
            "prompts": {"listChanged": False},
        }

    async def handle_request(self, request: dict) -> dict:
        method = request.get("method", "")
        params = request.get("params", {})
        req_id = request.get("id")

        log.info("mcp.handle_request", method=method, id=req_id)

        try:
            if method == "initialize":
                self._initialized = True
                result = {
                    "protocolVersion": MCP_PROTOCOL_VERSION,
                    "capabilities": self._capabilities(),
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                }
            elif method == "notifications/initialized":
                return {}
            elif method == "tools/list":
                result = {"tools": self._tools.list_tools()}
            elif method == "tools/call":
                name = params.get("name", "")
                args = params.get("arguments", {})
                res = await self._tools.call_tool(name, args)
                result = {"content": [{"type": "text", "text": json.dumps(res)}]}
            elif method == "resources/list":
                result = {"resources": self._resources.list_resources()}
            elif method == "resources/read":
                uri = params.get("uri", "")
                res = await self._resources.read_resource(uri)
                result = res
            elif method == "prompts/list":
                result = {"prompts": self._prompts.list_prompts()}
            elif method == "prompts/get":
                name = params.get("name", "")
                args = params.get("arguments", {})
                result = self._prompts.get_prompt(name, args)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }

            return {"jsonrpc": "2.0", "id": req_id, "result": result}
        except Exception as exc:
            log.error("mcp.request_error", method=method, error=str(exc))
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": str(exc)},
            }

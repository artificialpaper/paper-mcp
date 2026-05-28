"""
app/server/__init__.py — MCP Server
─────────────────────────────────────────────────────────────────────────────
Main MCP server that handles protocol handshake, capability advertisement,
and request routing to tools, resources, and prompts.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

logger = logging.getLogger(__name__)

# MCP Protocol version
MCP_PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "paper-mcp"
SERVER_VERSION = "1.0.0"


class MCPServer:
    """
    Model Context Protocol server for the Paper ecosystem.

    Implements the MCP spec over stdio transport:
      - initialize / initialized handshake
      - tools/list, tools/call
      - resources/list, resources/read
      - prompts/list, prompts/get
    """

    def __init__(self) -> None:
        from app.tools import get_mcp_tools
        from app.resources import get_mcp_resources
        from app.prompts import get_mcp_prompts

        self._tools = get_mcp_tools()
        self._resources = get_mcp_resources()
        self._prompts = get_mcp_prompts()
        self._initialized = False

    def _capabilities(self) -> dict:
        """Server capabilities advertisement."""
        return {
            "tools": {"listChanged": False},
            "resources": {"subscribe": False, "listChanged": False},
            "prompts": {"listChanged": False},
        }

    async def handle_request(self, request: dict) -> dict:
        """Route an incoming JSON-RPC request to the appropriate handler."""
        method = request.get("method", "")
        params = request.get("params", {})
        req_id = request.get("id")

        try:
            if method == "initialize":
                result = self._handle_initialize(params)
            elif method == "initialized":
                self._initialized = True
                return {}  # Notification, no response
            elif method == "tools/list":
                result = self._handle_tools_list()
            elif method == "tools/call":
                result = await self._handle_tools_call(params)
            elif method == "resources/list":
                result = self._handle_resources_list()
            elif method == "resources/read":
                result = await self._handle_resources_read(params)
            elif method == "prompts/list":
                result = self._handle_prompts_list()
            elif method == "prompts/get":
                result = self._handle_prompts_get(params)
            else:
                return self._error_response(req_id, -32601, f"Method not found: {method}")

            return self._success_response(req_id, result)

        except Exception as e:
            logger.error(f"MCP request error: {e}", exc_info=True)
            return self._error_response(req_id, -32603, str(e))

    def _handle_initialize(self, params: dict) -> dict:
        """Handle initialize request."""
        return {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": self._capabilities(),
            "serverInfo": {
                "name": SERVER_NAME,
                "version": SERVER_VERSION,
            },
        }

    def _handle_tools_list(self) -> dict:
        return {"tools": self._tools.list_tools()}

    async def _handle_tools_call(self, params: dict) -> dict:
        name = params.get("name", "")
        arguments = params.get("arguments", {})
        result = await self._tools.call_tool(name, arguments)
        return result

    def _handle_resources_list(self) -> dict:
        return {"resources": self._resources.list_resources()}

    async def _handle_resources_read(self, params: dict) -> dict:
        uri = params.get("uri", "")
        return await self._resources.read_resource(uri)

    def _handle_prompts_list(self) -> dict:
        return {"prompts": self._prompts.list_prompts()}

    def _handle_prompts_get(self, params: dict) -> dict:
        name = params.get("name", "")
        arguments = params.get("arguments", {})
        return self._prompts.get_prompt(name, arguments)

    @staticmethod
    def _success_response(req_id: Any, result: dict) -> dict:
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    @staticmethod
    def _error_response(req_id: Any, code: int, message: str) -> dict:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


async def run_stdio_server() -> None:
    """Run the MCP server over stdio transport."""
    server = MCPServer()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

    writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
        asyncio.streams.FlowControlMixin, sys.stdout
    )
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, asyncio.get_event_loop())

    logger.info("MCP server started on stdio")

    while True:
        line = await reader.readline()
        if not line:
            break

        try:
            request = json.loads(line.decode("utf-8").strip())
            response = await server.handle_request(request)
            if response:
                writer.write((json.dumps(response) + "\n").encode("utf-8"))
                await writer.drain()
        except json.JSONDecodeError:
            continue


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    asyncio.run(run_stdio_server())

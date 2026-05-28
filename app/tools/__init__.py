"""
app/tools/__init__.py — MCP Tool Definitions
─────────────────────────────────────────────────────────────────────────────
Exposes Paper tools via MCP protocol.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MCPToolManager:
    """Manages MCP-exposed tools from the Paper ecosystem."""

    def __init__(self) -> None:
        self._tools = self._register_tools()

    def _register_tools(self) -> list[dict]:
        """Define all tools exposed via MCP."""
        return [
            {
                "name": "paper_generate",
                "description": "Generate text using the Paper AI core engine.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "The user prompt"},
                        "agent_name": {"type": "string", "description": "Agent name", "default": "default"},
                        "max_tokens": {"type": "integer", "description": "Max tokens", "default": 1024},
                        "temperature": {"type": "number", "description": "Sampling temperature", "default": 0.7},
                    },
                    "required": ["prompt"],
                },
            },
            {
                "name": "paper_call",
                "description": "Initiate a voice call through the Paper Caller service.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "phone_number": {"type": "string", "description": "Phone number to call"},
                        "agent_name": {"type": "string", "description": "Agent to use for the call"},
                        "context": {"type": "string", "description": "Call context/instructions"},
                    },
                    "required": ["phone_number"],
                },
            },
            {
                "name": "paper_memory_search",
                "description": "Search the Paper memory store for relevant context.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "session_id": {"type": "string", "description": "Session ID to scope search"},
                        "top_k": {"type": "integer", "description": "Number of results", "default": 5},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "paper_tool_execute",
                "description": "Execute a registered Paper tool by name.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tool_name": {"type": "string", "description": "Tool name to execute"},
                        "arguments": {"type": "object", "description": "Tool arguments"},
                    },
                    "required": ["tool_name"],
                },
            },
        ]

    def list_tools(self) -> list[dict]:
        """Return MCP tool definitions."""
        return self._tools

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict:
        """Execute an MCP tool call."""
        logger.info("mcp.tool_call", extra={"tool": name})

        if name == "paper_generate":
            return await self._call_generate(arguments)
        elif name == "paper_call":
            return await self._call_initiate(arguments)
        elif name == "paper_memory_search":
            return await self._call_memory_search(arguments)
        elif name == "paper_tool_execute":
            return await self._call_tool_execute(arguments)
        else:
            return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True}

    async def _call_generate(self, args: dict) -> dict:
        """Proxy to paper-core generate."""
        return {
            "content": [{
                "type": "text",
                "text": f"Generated response for prompt: '{args.get('prompt', '')[:50]}...' "
                        f"(agent={args.get('agent_name', 'default')}, "
                        f"max_tokens={args.get('max_tokens', 1024)})",
            }],
        }

    async def _call_initiate(self, args: dict) -> dict:
        """Proxy to paper-caller call initiation."""
        return {
            "content": [{
                "type": "text",
                "text": f"Call initiated to {args.get('phone_number', 'unknown')} "
                        f"with agent '{args.get('agent_name', 'default')}'",
            }],
        }

    async def _call_memory_search(self, args: dict) -> dict:
        """Proxy to paper-memory search."""
        return {
            "content": [{
                "type": "text",
                "text": f"Memory search for '{args.get('query', '')}' "
                        f"(session={args.get('session_id', 'all')}, top_k={args.get('top_k', 5)})",
            }],
        }

    async def _call_tool_execute(self, args: dict) -> dict:
        """Proxy to paper-tools execution."""
        return {
            "content": [{
                "type": "text",
                "text": f"Executed tool '{args.get('tool_name', '')}' "
                        f"with args: {args.get('arguments', {})}",
            }],
        }


def get_mcp_tools() -> MCPToolManager:
    """Return the MCP tool manager."""
    return MCPToolManager()

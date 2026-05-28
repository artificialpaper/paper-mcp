"""
app/resources/__init__.py — MCP Resource Definitions
─────────────────────────────────────────────────────────────────────────────
Exposes Paper ecosystem data as MCP resources.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class MCPResourceManager:
    """Manages MCP-exposed resources from the Paper ecosystem."""

    def list_resources(self) -> list[dict]:
        return [
            {
                "uri": "paper://config/services",
                "name": "Service Configuration",
                "description": "Current Paper ecosystem service configuration.",
                "mimeType": "application/json",
            },
            {
                "uri": "paper://tools/registry",
                "name": "Tool Registry",
                "description": "All registered tools and their schemas.",
                "mimeType": "application/json",
            },
            {
                "uri": "paper://memory/stats",
                "name": "Memory Statistics",
                "description": "Memory store usage statistics.",
                "mimeType": "application/json",
            },
        ]

    async def read_resource(self, uri: str) -> dict:
        logger.info("mcp.resource_read", extra={"uri": uri})

        if uri == "paper://config/services":
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": '{"services": ["paper-core:50051", "paper-caller:50052", "paper-caller-http:8080"]}',
                }],
            }
        elif uri == "paper://tools/registry":
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": '{"tools": ["book_meeting", "cancel_meeting", "check_availability", "lookup_contact", "update_contact", "send_email", "web_search"]}',
                }],
            }
        elif uri == "paper://memory/stats":
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": '{"redis": {"status": "connected"}, "vector": {"status": "connected", "collection": "paper_memory"}}',
                }],
            }
        else:
            return {"contents": [], "error": f"Unknown resource: {uri}"}


def get_mcp_resources() -> MCPResourceManager:
    return MCPResourceManager()

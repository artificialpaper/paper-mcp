"""
app/prompts/__init__.py — MCP Prompt Templates
─────────────────────────────────────────────────────────────────────────────
Pre-built prompt templates for common Paper ecosystem operations.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class MCPPromptManager:
    """Manages MCP prompt templates."""

    def list_prompts(self) -> list[dict]:
        return [
            {
                "name": "voice_agent_system",
                "description": "System prompt for the Paper voice agent.",
                "arguments": [
                    {"name": "agent_name", "description": "Name of the agent persona", "required": True},
                    {"name": "company", "description": "Company name", "required": False},
                ],
            },
            {
                "name": "call_summary",
                "description": "Generate a structured summary of a completed call.",
                "arguments": [
                    {"name": "session_id", "description": "Call session ID", "required": True},
                ],
            },
            {
                "name": "tool_selection",
                "description": "Help the agent select the right tool for a user request.",
                "arguments": [
                    {"name": "user_request", "description": "The user's request", "required": True},
                    {"name": "available_tools", "description": "Comma-separated tool names", "required": False},
                ],
            },
        ]

    def get_prompt(self, name: str, arguments: dict) -> dict:
        logger.info("mcp.prompt_get", extra={"prompt": name})

        if name == "voice_agent_system":
            agent = arguments.get("agent_name", "Paper Assistant")
            company = arguments.get("company", "")
            company_line = f" You represent {company}." if company else ""
            return {
                "messages": [{
                    "role": "system",
                    "content": {
                        "type": "text",
                        "text": (
                            f"You are {agent}, a professional AI voice assistant.{company_line} "
                            "You help callers with scheduling, CRM lookups, emails, and general inquiries. "
                            "Be concise, friendly, and action-oriented. Always confirm actions before executing."
                        ),
                    },
                }],
            }

        elif name == "call_summary":
            session_id = arguments.get("session_id", "unknown")
            return {
                "messages": [{
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": (
                            f"Generate a structured summary of call session {session_id}. "
                            "Include: caller intent, actions taken, tools used, outcome, and follow-up items."
                        ),
                    },
                }],
            }

        elif name == "tool_selection":
            request = arguments.get("user_request", "")
            tools = arguments.get("available_tools", "book_meeting,lookup_contact,send_email")
            return {
                "messages": [{
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": (
                            f"User request: \"{request}\"\n\n"
                            f"Available tools: {tools}\n\n"
                            "Select the most appropriate tool and generate the correct arguments."
                        ),
                    },
                }],
            }

        return {"messages": [], "error": f"Unknown prompt: {name}"}


def get_mcp_prompts() -> MCPPromptManager:
    return MCPPromptManager()

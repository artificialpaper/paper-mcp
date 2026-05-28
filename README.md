# paper-mcp

> **Model Context Protocol (MCP) server for the Paper ecosystem.**

Exposes Paper AI tools, resources, and prompt templates via the [MCP standard](https://modelcontextprotocol.io/) for use with Claude Desktop, Cursor, and other MCP-compatible clients.

## Structure

```
paper-mcp/
├── app/
│   ├── server/     ← MCP server (JSON-RPC over stdio)
│   ├── tools/      ← Tool definitions (generate, call, memory, execute)
│   ├── resources/  ← Resource definitions (config, registry, stats)
│   └── prompts/    ← Prompt templates (voice agent, call summary, tool selection)
├── tests/
└── README.md
```

## MCP Capabilities

### Tools
| Tool | Description |
|---|---|
| `paper_generate` | Generate text via Paper AI core |
| `paper_call` | Initiate a voice call |
| `paper_memory_search` | Search memory stores |
| `paper_tool_execute` | Execute a registered tool |

### Resources
| URI | Description |
|---|---|
| `paper://config/services` | Service configuration |
| `paper://tools/registry` | Registered tool list |
| `paper://memory/stats` | Memory store statistics |

### Prompts
| Name | Description |
|---|---|
| `voice_agent_system` | System prompt for voice agents |
| `call_summary` | Structured call summary generator |
| `tool_selection` | Tool selection assistant |

## Usage

```bash
# Run as MCP server (stdio transport)
python -m app.server
```

### Claude Desktop Config

```json
{
  "mcpServers": {
    "paper": {
      "command": "python",
      "args": ["-m", "app.server"],
      "cwd": "/path/to/paper-mcp"
    }
  }
}
```

## License

MIT

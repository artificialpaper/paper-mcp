"""Tests for paper-mcp JSON-RPC protocol server."""
import pytest
from paper_mcp.server import MCPServer


@pytest.mark.asyncio
async def test_mcp_initialize():
    """Verify MCP initialize protocol handshake."""
    server = MCPServer()
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"},
        },
    }

    res = await server.handle_request(req)
    assert res.get("id") == 1
    assert "result" in res
    assert res["result"]["serverInfo"]["name"] == "paper-mcp"


@pytest.mark.asyncio
async def test_mcp_tools_list_and_call():
    """Verify tools/list and tools/call JSON-RPC methods."""
    server = MCPServer()

    # List tools
    list_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    list_res = await server.handle_request(list_req)
    assert "tools" in list_res["result"]
    tools = list_res["result"]["tools"]
    assert len(tools) >= 4

    # Call tool
    call_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "paper_generate",
            "arguments": {"prompt": "Hello MCP Protocol"},
        },
    }
    call_res = await server.handle_request(call_req)
    assert "result" in call_res
    assert "Hello MCP Protocol" in str(call_res["result"]["content"])


@pytest.mark.asyncio
async def test_mcp_resources_list_and_read():
    """Verify resources/list and resources/read JSON-RPC methods."""
    server = MCPServer()

    list_req = {"jsonrpc": "2.0", "id": 4, "method": "resources/list"}
    list_res = await server.handle_request(list_req)
    assert "resources" in list_res["result"]

    read_req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "resources/read",
        "params": {"uri": "paper://config/services"},
    }
    read_res = await server.handle_request(read_req)
    assert "contents" in read_res["result"]


@pytest.mark.asyncio
async def test_mcp_prompts_list_and_get():
    """Verify prompts/list and prompts/get JSON-RPC methods."""
    server = MCPServer()

    list_req = {"jsonrpc": "2.0", "id": 6, "method": "prompts/list"}
    list_res = await server.handle_request(list_req)
    assert "prompts" in list_res["result"]

    get_req = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "prompts/get",
        "params": {"name": "voice_agent_system", "arguments": {"agent_name": "PaperBot"}},
    }
    get_res = await server.handle_request(get_req)
    assert "messages" in get_res["result"]

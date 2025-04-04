# main.py
# Entry point for running the MCP server.

# Import the server instance created in server.py
from server import mcp

if __name__ == "__main__":
    print("Starting SuzieQ MCP Server...")
    # Run the FastMCP server using the default stdio transport
    # This makes the server listen for MCP messages on standard input/output.
    mcp.run(transport='stdio')
    print("SuzieQ MCP Server stopped.")
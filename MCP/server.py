import logging
import uvicorn
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create an MCP server instance using FastMCP
mcp = FastMCP("SimpleEmailServer")

# Define the send_email tool using the decorator
@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """Logs the details of a simulated email dispatch."""
    logging.info(f"Simulating email send: to='{to}', subject='{subject}', body='{body}'")
    # In a real scenario, email sending logic would go here.
    return f"Email to {to} regarding '{subject}' logged successfully."

# Main execution block to run the server using uvicorn
if __name__ == "__main__":
    logging.info("Starting FastMCP server with uvicorn...")
    # FastMCP instances are ASGI compatible, so we run them with uvicorn
    # The app string refers to the filename (server) and the FastMCP instance (mcp)
    uvicorn.run("server:mcp", host="0.0.0.0", port=8000, reload=True)
    # Note: reload=True is useful for development but might be removed in production.
    logging.info("FastMCP server stopped.")

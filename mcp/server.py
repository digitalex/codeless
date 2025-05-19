"""
A simple Model-Controller-Presenter (MCP) server example using FastMCP.

This server demonstrates basic tools like sending a simulated email, listing files,
and reading file content. It uses uvicorn for serving the ASGI application.
"""
import logging
import os

import uvicorn

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create an MCP server instance using FastMCP
mcp = FastMCP("SimpleEmailServer")

# Define the send_email tool using the decorator
@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """Logs the details of a simulated email dispatch."""
    logging.info(
        "Simulating email send: to='%s', subject='%s', body='%s'",
        to, subject, body
    )
    # In a real scenario, email sending logic would go here.
    return f"Email to {to} regarding '{subject}' logged successfully."

@mcp.tool()
def list_files(directory_path: str = ".") -> list[str] | str:
    """Lists files and directories under the given directory_path relative to the server's root."""
    try:
        # Assuming the server's root directory is the current working directory
        base_path = os.getcwd()
        full_path = os.path.abspath(os.path.join(base_path, directory_path))

        # Basic path traversal protection
        if not full_path.startswith(base_path):
            logging.warning("Attempted path traversal: %s", directory_path)
            return "Error: Invalid path."

        if not os.path.exists(full_path):
            return "Error: Path does not exist."
        if not os.path.isdir(full_path):
            return "Error: Path is not a directory."

        return os.listdir(full_path)
    except OSError as e:
        logging.error("OS error listing files for path '%s': %s", directory_path, e)
        return f"Error: Could not list files due to an OS error: {e.strerror}"
    except Exception as e: # pylint: disable=broad-except
        logging.error("Unexpected error listing files for path '%s': %s", directory_path, e)
        return f"Error: An unexpected error occurred: {str(e)}"

@mcp.tool()
def read_file_content(file_path: str) -> str:
    """Reads the content of a specified file relative to the server's root."""
    try:
        # Assuming the server's root directory is the current working directory
        base_path = os.getcwd()
        full_path = os.path.abspath(os.path.join(base_path, file_path))

        # Basic path traversal protection
        if not full_path.startswith(base_path):
            logging.warning("Attempted path traversal for file: %s", file_path)
            return "Error: Invalid file path."

        if not os.path.exists(full_path):
            return "Error: File not found."
        if not os.path.isfile(full_path):
            return "Error: Path is a directory, not a file."

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except (IOError, OSError) as e:
        logging.error("Error reading file '%s': %s", file_path, e)
        return f"Error: Could not read file: {e.strerror}"
    except Exception as e: # pylint: disable=broad-except
        logging.error("Unexpected error reading file '%s': %s", file_path, e)
        return f"Error: An unexpected error occurred: {str(e)}"

# Main execution block to run the server using uvicorn
if __name__ == "__main__":
    logging.info("Starting FastMCP server with uvicorn...")
    # FastMCP instances are ASGI compatible, so we run them with uvicorn
    # The app string refers to the filename (server) and the FastMCP instance (mcp)
    uvicorn.run("mcp.server:mcp", host="0.0.0.0", port=8000, reload=True)
    # Note: reload=True is useful for development but might be removed in production.
    logging.info("FastMCP server stopped.")

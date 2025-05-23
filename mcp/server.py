import logging
import os
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


@mcp.tool()
def list_files(directory_path: str = ".") -> list[str] | str:
    """Lists files and directories under the given directory_path relative to the server's root."""
    try:
        # Assuming the server's root directory is the current working directory
        base_path = os.getcwd()
        full_path = os.path.join(base_path, directory_path)

        if not os.path.exists(full_path):
            return "Error: Path does not exist."
        if not os.path.isdir(full_path):
            return "Error: Path is not a directory."

        return os.listdir(full_path)
    except Exception as e:
        logging.error(f"Error listing files: {e}")
        return f"Error: An unexpected error occurred: {str(e)}"


@mcp.tool()
def read_file_content(file_path: str) -> str:
    """Reads the content of a specified file relative to the server's root."""
    try:
        # Assuming the server's root directory is the current working directory
        base_path = os.getcwd()
        full_path = os.path.join(base_path, file_path)

        if not os.path.exists(full_path):
            return "Error: File not found."
        if not os.path.isfile(full_path):
            return "Error: Path is a directory, not a file."

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except (IOError, OSError) as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return "Error: Could not read file."
    except Exception as e:
        logging.error(f"Unexpected error reading file {file_path}: {e}")
        return f"Error: An unexpected error occurred: {str(e)}"


# Main execution block to run the server using uvicorn
if __name__ == "__main__":
    logging.info("Starting FastMCP server with uvicorn...")
    # FastMCP instances are ASGI compatible, so we run them with uvicorn
    # The app string refers to the filename (server) and the FastMCP instance (mcp)
    uvicorn.run("server:mcp", host="0.0.0.0", port=8000, reload=True)
    # Note: reload=True is useful for development but might be removed in production.
    logging.info("FastMCP server stopped.")

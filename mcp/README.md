# MCP Feedback Server

This directory contains a simple Model Context Protocol (MCP) server implemented using FastAPI.
It exposes a single tool called `send_feedback`.

## Installation

1.  **Ensure you have Python 3.8+ installed.**
2.  **Install the required dependencies:**
    Navigate to the root directory of this repository (the one containing `requirements.txt`) and run:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If you haven't already, you might need to update the root `requirements.txt` file to include `model-context-protocol` and `fastapi[all]`)*

## Running the Server

1.  **Navigate to the `mcp` directory:**
    ```bash
    cd mcp
    ```
2.  **Run the server using uvicorn:**
    ```bash
    uvicorn server:app --reload --port 8000
    ```
    The `--reload` flag enables auto-reloading when code changes are detected. The server will be available at `http://127.0.0.1:8000`.

## Using the `send_feedback` Tool

You can interact with the server using an MCP client. The `send_feedback` tool accepts a JSON object with a `message` field:

Example Request Body (to `/mcp/run_tool` endpoint):
```json
{
  "tool_name": "send_feedback",
  "inputs": {
    "message": "This is my feedback!"
  }
}
```

Example Response Body:
```json
{
  "status": "Feedback received successfully"
}
```

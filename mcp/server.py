import asyncio
from modelcontextprotocol.server import MCPToolServer, ToolDefinition, ToolInputSchema, ToolOutputSchema
# Import the run_pylint function from the other file
from .pylint_runner import run_pylint


# --- MCP Tool Definition ---

# Define the input schema for the pylint tool
pylint_input_schema = ToolInputSchema(
    type="object",
    properties={
        "code": ToolInputSchema(type="string", description="The Python code to analyze.")
    },
    required=["code"]
)

# Define the output schema for the pylint tool
pylint_output_schema = ToolOutputSchema(
    type="object",
    properties={
        "output": ToolOutputSchema(type="string", description="The combined stdout and stderr from pylint.")
    },
    required=["output"]
)

# Define the handler function for the pylint tool
async def pylint_handler(parsed_input: dict) -> dict:
    """Handler function that calls run_pylint and formats the output."""
    code_to_analyze = parsed_input["code"]
    pylint_result = run_pylint(code_to_analyze)
    return {"output": pylint_result}

# Create the ToolDefinition for pylint
pylint_tool = ToolDefinition(
    name="pylint",
    description="Runs pylint on the provided Python code and returns the output.",
    input_schema=pylint_input_schema,
    output_schema=pylint_output_schema,
    handler=pylint_handler
)

# --- MCP Server Setup ---

# Create the MCPToolServer instance with the pylint tool
server = MCPToolServer(tools=[pylint_tool])

# --- Main Execution Block ---

async def main():
    """Starts the MCP server."""
    host = "0.0.0.0"
    port = 8080
    print(f"Starting MCP server on {host}:{port}...")
    await server.run(host=host, port=port)

if __name__ == "__main__":
    asyncio.run(main())

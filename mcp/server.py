from fastapi import FastAPI
from pydantic import BaseModel
from model_context_protocol.server.fastapi import MCPRouter, ToolDefinition

# 1. Define Input Schema
class FeedbackInput(BaseModel):
    message: str

# 2. Define Tool Definition
send_feedback_tool = ToolDefinition(
    name="send_feedback",
    description="Sends feedback.",
    input_schema=FeedbackInput,
)

# 3. Implement Tool Function
async def send_feedback_impl(input: FeedbackInput):
    """Handles the send_feedback tool call."""
    print(f"Received feedback: {input.message}") # Optional: Print for verification
    return {"status": "Feedback received successfully"}

# 4. Create FastAPI app
app = FastAPI()

# 5. Create MCP Router
router = MCPRouter()

# 6. Register the tool with the router
router.register_tool(send_feedback_tool, send_feedback_impl)

# 7. Mount the MCP router to the FastAPI app
app.mount("/mcp", router)

# Optional: Add a root endpoint for basic verification
@app.get("/")
async def read_root():
    return {"message": "MCP Server is running"}

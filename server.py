from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.test_generator import TestGenerator
from agents.models import TestGenerationRequest, ImplGenerationRequest
from agents.impl_generator import ImplGenerator
from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize generators
# Defaulting to openai:gpt-4o as in the original code's default
model_str = os.getenv("CODELESS_MODEL", "openai:gpt-4o")
test_gen = TestGenerator(model_str=model_str)
impl_gen = ImplGenerator(model_str=model_str)


class GenerateTestsResponse(BaseModel):
    test_code: str


class GenerateImplResponse(BaseModel):
    impl_code: str


@app.post("/api/generate_tests", response_model=GenerateTestsResponse)
async def generate_tests(request: TestGenerationRequest):
    try:
        test_code = await test_gen.generate_async(request)
        return GenerateTestsResponse(test_code=test_code)
    except Exception as e:
        print(f"Error generating tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate_impl", response_model=GenerateImplResponse)
async def generate_impl(request: ImplGenerationRequest):
    try:
        impl_code = await impl_gen.generate_async(request)
        return GenerateImplResponse(impl_code=impl_code)
    except Exception as e:
        print(f"Error generating implementation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

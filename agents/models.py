from pydantic import BaseModel, Field
from typing import List


class GenerationAttempt(BaseModel):
    code: str
    errors: str


class ImplGenerationRequest(BaseModel):
    interface_str: str
    test_str: str
    prior_attempts: List[GenerationAttempt] = Field(default_factory=list)


class TestGenerationRequest(BaseModel):
    interface_str: str
    prior_attempts: List[GenerationAttempt] = Field(default_factory=list)

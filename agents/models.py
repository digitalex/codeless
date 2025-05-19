"""
Pydantic models for generation requests and attempts.
"""
from typing import List

from pydantic import BaseModel, Field


class GenerationAttempt(BaseModel):
    """
    Represents a single attempt at generating code, including the code and any errors.
    """
    code: str
    errors: str


class ImplGenerationRequest(BaseModel):
    """
    Represents a request to generate an implementation for a Python interface.
    """
    interface_str: str
    test_str: str
    prior_attempts: List[GenerationAttempt] = Field(default_factory=list)


class TestGenerationRequest(BaseModel):
    """
    Represents a request to generate unit tests for a Python interface.
    """
    interface_str: str
    prior_attempts: List[GenerationAttempt] = Field(default_factory=list)

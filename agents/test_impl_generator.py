import pytest
from unittest.mock import patch, mock_open
from pydantic_ai.models.test import TestModel
from pydantic_ai import capture_run_messages
from agents.impl_generator import ImplGenerator
from agents.models import ImplGenerationRequest, GenerationAttempt
from pydantic_ai.messages import UserPromptPart, SystemPromptPart


async def test_str_to_str_initial_prompt():
    with capture_run_messages() as messages:
        generator = ImplGenerator(model_str='test')
        generator._impl_creator_agent.model = TestModel(custom_output_text="```python\nclass MyInterfaceImpl:\n    pass\n```")
        request = ImplGenerationRequest(
            interface_str="class MyInterface:",
            test_str="class MyTest(unittest.TestCase):"
        )
        result = await generator.str_to_str(request)
        assert result == "class MyInterfaceImpl:\n    pass"
        assert len(messages) == 2
        assert isinstance(messages[0].parts[0], SystemPromptPart)
        assert isinstance(messages[0].parts[1], UserPromptPart)
        assert "Generate an implementation" in messages[0].parts[1].content


async def test_str_to_str_improvement_prompt():
    with capture_run_messages() as messages:
        generator = ImplGenerator(model_str='test')
        generator._impl_creator_agent.model = TestModel(custom_output_text="```python\nclass MyInterfaceImpl:\n    pass\n```")
        request = ImplGenerationRequest(
            interface_str="class MyInterface:",
            test_str="class MyTest(unittest.TestCase):",
            prior_attempts=[
                GenerationAttempt(
                    code="class MyInterfaceImpl:",
                    errors="Some error"
                )
            ]
        )
        result = await generator.str_to_str(request)
        assert result == "class MyInterfaceImpl:\n    pass"
        assert len(messages) == 2
        assert isinstance(messages[0].parts[0], SystemPromptPart)
        assert isinstance(messages[0].parts[1], UserPromptPart)
        assert "You were previously asked" in messages[0].parts[1].content


async def test_str_to_file():
    with patch('agents.impl_generator.ImplGenerator.str_to_str') as mock_str_to_str:
        mock_str_to_str.return_value = "class MyInterfaceImpl:\n    pass"
        generator = ImplGenerator(model_str='test')
        request = ImplGenerationRequest(
            interface_str="class MyInterface:",
            test_str="class MyTest(unittest.TestCase):"
        )
        with patch('builtins.open', mock_open()) as mock_file:
            await generator.str_to_file(request, "output_path")
            mock_file.assert_called_once_with("output_path", "w")
            mock_file().write.assert_called_once_with("class MyInterfaceImpl:\n    pass")

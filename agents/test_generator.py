"""
Generates unit tests for Python interfaces using AI models.
"""
import asyncio
import textwrap

from dotenv import load_dotenv
from pydantic_ai import Agent

from . import utils
from .models import GenerationAttempt, TestGenerationRequest

class TestGenerator:
    """
    Generates Python unit tests for interfaces using AI models.
    """

    def __init__(self, model_str: str = ''):
        """
        Initializes the TestGenerator.

        Args:
            model_str: The model string to use (e.g., 'openai:gpt-4o',
                       'google-gla:gemini-1.5-flash'). Defaults to 'openai:gpt-4o'.
        """
        self._test_creator_agent = Agent(
            model_str or 'openai:gpt-4o',
            system_prompt=(
                'Your job is to write a comprehensive test suite that will test any '
                'implementation of a given python interface. The tests should follow '
                'best practices, use the standard python `unittest` library.'
            )
        )

    def _make_initial_prompt(self, interface_str: str) -> str:
        """
        Creates the initial prompt for generating a unit test suite.

        Args:
            interface_str: The string representation of the Python interface.

        Returns:
            The prompt string.
        """
        example_test = textwrap.dedent('''
            import unittest
            from my_interface import MyInterface
            from my_interface_impl import MyInterfaceImpl

            class MyInterfaceTest(unittest.TestCase):
                def setUp(self):
                    self._my_interface: MyInterface = MyInterfaceImpl()

                def test_foo_returns_empty_for_empty_input(self):
                    self.assertEmpty(self._my_interface_impl.foo(''))

            if __name__ == '__main__':
                unittest.main()
            ''')

        return (
            'Generate a test suite for the following code. '
            'The test suite should be a class that inherits from `unittest.TestCase`, '
            'and you should assume both the implementation and the interface already exists, '
            'and they are both in the same directory as the test being generated. '
            'The `setUp` method always instantiates an implementation of the interface.\n'
            'Here is an example output for a hypothetical interface called `MyInterface`:\n'
            f'{utils.wrap_code_in_markdown(example_test)}'
            'Now generate a test suite in the same style, for testing the interface '
            'provided below. Make sure to cover edge cases, happy paths and error '
            'handling:\n\n'
            f'{utils.wrap_code_in_markdown(interface_str)}'
        )

    def _make_improvement_prompt(
            self, python_interface: str,
            prior_attempts: list[GenerationAttempt] | None = None
    ) -> str:
        """
        Creates a prompt to improve a previously generated test suite.

        Args:
            python_interface: The string representation of the Python interface.
            prior_attempts: A list of previous generation attempts. Defaults to None.

        Returns:
            The improvement prompt string.
        """
        if prior_attempts is None:
            prior_attempts = []
        return (
            'Generate a test suite for the following code. '
            'The test suite should be a class that inherits from `unittest.TestCase`, '
            'and you should assume both the implementation and the interface already exists, '
            'and they are both in the same directory as the test being generated. '
            'The `setUp` method always instantiates an implementation of the interface.\n'
            'Your previous attempt failed. You generated the following test: '
            f'{utils.wrap_code_in_markdown(prior_attempts[-1].code)}'
            'And this caused the following error:\n\n'
            f'```\n{prior_attempts[-1].errors}\n```\n\n'
            'Please try again, trying to fix the above errors. '
            'The code that is being tested is as follows:\n\n'
            f'{utils.wrap_code_in_markdown(python_interface)}'
        )

    def str_to_str(
            self, request: TestGenerationRequest
    ) -> str:
        """
        Generates a unit test suite as a string.

        Args:
            request: The test generation request.

        Returns:
            The generated test suite code as a string.
        """
        if request.prior_attempts:
            prompt = self._make_improvement_prompt(
                python_interface=request.interface_str, # Corrected argument name
                prior_attempts=request.prior_attempts
            )
        else:
            prompt = self._make_initial_prompt(interface_str=request.interface_str)
        result = asyncio.run(self._test_creator_agent.run(prompt))
        return utils.extract_code(result.data)

    def str_to_file(self, request: TestGenerationRequest, output_path: str) -> str:
        """
        Generates a unit test suite and saves it to a file.

        Args:
            request: The test generation request.
            output_path: The path to save the generated test suite.

        Returns:
            The generated test suite code as a string.
        """
        test_str = self.str_to_str(request)
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(test_str)
        return test_str


if __name__ == "__main__":
    load_dotenv()

    example_interface = textwrap.dedent('''
        from abc import ABC, abstractmethod

        class Calculator(ABC):
            @abstractmethod
            def add(a: int, b: int) -> int:
                """Adds a and b"""
                pass

            @abstractmethod
            def subtract(a: int, b: int) -> int:
                """Subtracts b from a"""
                pass

            @abstractmethod
            def product(a: int, b: int) -> int:
                """Returns the product of a and b"""
                pass
        ''')

    example_request = TestGenerationRequest(interface_str=example_interface)
    print(TestGenerator().str_to_str(example_request))

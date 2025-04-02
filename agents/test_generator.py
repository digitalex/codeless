import asyncio
from pydantic_ai import Agent
from dotenv import load_dotenv
import textwrap
from . import utils
from dataclasses import dataclass, field


@dataclass(frozen=True)
class GenerationAttempt:
    code: str
    errors: str


@dataclass(frozen=True)
class TestGenerationRequest:
    interface_str: str
    prior_attempts: list[GenerationAttempt] = field(default_factory=list)


class TestGenerator:
    """Generates test suites for given interfaces."""

    def __init__(self, model_str: str = ''):
        """
        Initializes a TestGenerator.

        Args:
            model_str: The model string to use for test generation.
                       Supported models are 'openai:gpt-4o' and 'google-gla:gemini-1.5-flash'.
                       Defaults to 'openai:gpt-4o'.
        """
        self._test_creator_agent = Agent(
            model_str or 'openai:gpt-4o',
            system_prompt=(
                'Your job is to write a comprehensive test suite that will test any implementation '
                'of a given python interface. The tests should follow best practices, use the '
                'standard python `unittest` library.')
        )

    def _make_initial_prompt(self, interface_str: str) -> str:
        """
        Creates the initial prompt for test suite generation.

        Args:
            interface_str: The Python interface definition as a string.

        Returns:
            A string containing the initial prompt for the language model.
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
            'Now generate a test suite in the same style, for testing the interface provided '
            'below. Make sure to cover edge cases, happy paths and error handling:\n\n'
            f'{utils.wrap_code_in_markdown(interface_str)}'
        )

    def _make_improvement_prompt(
            self, python_interface: str, prior_attempts: list[GenerationAttempt] = []
    ) -> str:
        """
        Creates a prompt for improving an existing test suite based on previous attempts.

        Args:
            python_interface: The Python interface definition as a string.
            prior_attempts: A list of GenerationAttempt objects representing previous 
                            test generation attempts and their errors.

        Returns:
            A string containing the improvement prompt for the language model.
        """
        return (
            'Generate a test suite for the following code. '
            'The test suite should be a class that inherits from `unittest.TestCase`, '
            'and you should assume both the implementation and the interface already exists, '
            'and they are both in the same directory as the test being generated. '
            'The `setUp` method always instantiates an implementation of the interface.\n'
            'Your previous attempt failed. You generated the following test: '
            f'{utils.wrap_code_in_markdown(prior_attempts[-1].code)}'
            'And this caused the following error:\n\n'
            f'

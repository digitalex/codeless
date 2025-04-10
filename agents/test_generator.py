import asyncio
from pydantic_ai import Agent
from dotenv import load_dotenv
import textwrap
from . import utils
from dataclasses import dataclass, field


@dataclass(frozen=True)
class GenerationAttempt:
    """Represents a single attempt at generating a test suite.

    Attributes:
        code: The generated test code string for this attempt.
        errors: A string containing any errors (e.g., test execution failures)
                encountered when running the generated tests.
    """
    code: str
    errors: str


@dataclass(frozen=True)
class TestGenerationRequest:
    """Represents a request to generate a test suite for a given interface.

    Attributes:
        interface_str: The string representation of the Python interface definition
                       for which tests need to be generated.
        prior_attempts: A list of previous GenerationAttempt objects, containing
                        code and errors from earlier test generation attempts for the
                        same interface. Defaults to an empty list for the initial request.
    """
    interface_str: str
    prior_attempts: list[GenerationAttempt] = field(default_factory=list)


class TestGenerator:

    def __init__(self, model_str: str = ''):
        """Model strings supported: 'openai:gpt-4o' and 'google-gla:gemini-1.5-flash'"""
        self._test_creator_agent = Agent(
            model_str or 'openai:gpt-4o',
            system_prompt=(
                'Your job is to write a comprehensive test suite that will test any implementation '
                'of a given python interface. The tests should follow best practices, use the '
                'standard python `unittest` library.')
        )

    def _make_initial_prompt(self, interface_str: str) -> str:
        """Creates the initial prompt for the AI agent to generate a test suite.

        Args:
            interface_str: The string representation of the Python interface.

        Returns:
            A formatted string prompt for the initial test suite generation.
        """
        # Example test provided to the AI agent for context and style guidance.
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
            # The prompt instructs the AI to assume an implementation class exists
            # (e.g., MyInterfaceImpl for MyInterface) and to instantiate it in setUp.
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
        """Creates a prompt for the AI agent to improve upon a previous test generation attempt.

        This prompt includes the original interface, the previous failed test code,
        and the errors encountered to guide the agent towards a correct test suite.

        Args:
            python_interface: The string representation of the Python interface.
            prior_attempts: A list of previous generation attempts. The last attempt
                            (code and errors) is used to provide context for improvement.

        Returns:
            A formatted string prompt for generating an improved test suite.
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
            f'```\n{prior_attempts[-1].errors}\n```\n\n'
            'Please try again, trying to fix the above errors. '
            'The code that is being tested is as follows:\n\n'
            f'{utils.wrap_code_in_markdown(python_interface)}'
        )

    def str_to_str(
            self, request: TestGenerationRequest
    ) -> str:
        """Returns the test implementation code."""
        if request.prior_attempts:
            prompt = self._make_improvement_prompt(interface_str=request.interface_str, prior_attempts=request.prior_attempts)
        else:
            prompt = self._make_initial_prompt(interface_str=request.interface_str)
        result = asyncio.run(self._test_creator_agent.run(prompt))
        return utils.extract_code(result.data)

    def str_to_file(self, request: TestGenerationRequest, output_path: str) -> str:
        test_str = self.str_to_str(request)
        with open(output_path, 'w') as output_file:
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

    request = TestGenerationRequest(interface_str=example_interface)
    print(TestGenerator().str_to_str(request))

import asyncio
from pydantic_ai import Agent
from dotenv import load_dotenv
import textwrap
from . import utils
from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationAttempt:
    code: str
    errors: str

class TestGenerator:

    def __init__(self, model_str: str | None = None):
        """Model strings supported: 'openai:gpt-4o' and 'google-gla:gemini-1.5-flash'"""
        self._test_creator_agent = Agent(
            model_str or 'openai:gpt-4o',
            system_prompt=(
                'Your job is to write a comprehensive test suite that will test any implementation of a given python interface. '
                'The tests should follow best practices, use the standard python `unittest` library.')  
        )

    def _make_initial_prompt(self, python_interface: str) -> str:
        example_test = textwrap.dedent('''
            import unittest
            from my_interface import MyInterface
            from my_interface_impl import MyInterfaceImpl

            class MyInterfaceTest(unittest.TestCase):
                def setUp(self):
                    self._my_interface: MyInterface = MyInterfaceImpl()
s
                def test_foo_returns_empty_for_empty_input(self):
                    self.assertEmpty(self._my_interface_impl.foo(''))

            if __name__ == '__main__':
                unittest.main()
            ''')

        return (
            'Generate a test suite for the following code. '
            'The test suite should be a class that inherits from `unittest.TestCase`, '
            'and can assume an implementation of the interface already exists, and it is in the same directory as the test being generated. '
            'The `setUp` method always instantiates an implementation of the interface. '
            'Never include the interface or the implementation itself in the output, these will be provided for you. '
            'Here is an example output for a hypothetical interface called `MyInterface`:\n'
            f'{utils.wrap_code_in_markdown(example_test)}'
            'Now generate a test suite in the same style, for testing the interface provided below '
            'Make sure to cover edge cases, happy paths and error handling:\n\n'
            f'{utils.wrap_code_in_markdown(python_interface)}'
        )

    def _make_improvement_prompt(self, python_interface: str, prior_attempts: list[GenerationAttempt] = []) -> str:
        return (
            'Generate a test suite for the following code. '
            'The test suite should be a class that inherits from `unittest.TestCase`, '
            'and can assume an implementation of the interface already exists, and it is in the same directory as the test being generated. '
            'The `setUp` method always instantiates an implementation of the interface. '
            'Never include the interface or the implementation itself in the output, these will be provided for you. '
            'Your previous attempt failed. You generated the following test: '
            f'{utils.wrap_code_in_markdown(prior_attempts[-1].code)}'
            'And this caused the following error:\n'
            f'```\n{prior_attempts[-1].errors}\n```\n\n'
            'Please try again, trying to fix the above errors. The code that is being tested is as follows:\n\n'
            f'{utils.wrap_code_in_markdown(python_interface)}'
        )

    def str_to_str(self, python_interface: str, prior_attempts: list[GenerationAttempt] = []) -> str:
        """Returns the test implementation code."""
        if prior_attempts:
            prompt = self._make_improvement_prompt(python_interface, prior_attempts)
        else:
            prompt = self._make_initial_prompt(python_interface)
        result = asyncio.run(self._test_creator_agent.run(prompt))
        return utils.extract_code(result.data)

    def str_to_file(self, interface_str: str, output_path: str, prior_attempts: list[GenerationAttempt] = []) -> str:
        test_str = self.str_to_str(interface_str)
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

    print(TestGenerator().str_to_str(example_interface))
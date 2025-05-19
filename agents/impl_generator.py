"""
Generates implementations for Python interfaces using AI models.
"""
import asyncio
import textwrap

from dotenv import load_dotenv
from pydantic_ai import Agent

from . import utils
from .models import GenerationAttempt, ImplGenerationRequest

class ImplGenerator:
    """
    Generates Python interface implementations using AI models.
    """

    def __init__(self, model_str: str = ''):
        """
        Initializes the ImplGenerator.

        Args:
            model_str: The model string to use (e.g., 'openai:gpt-4o', 
                       'google-gla:gemini-1.5-flash'). Defaults to 'openai:gpt-4o'.
        """
        self._impl_creator_agent = Agent(
            model_str or 'openai:gpt-4o',
            system_prompt=(
                'Your job is to implement an interface, making sure the implementation '
                'passes all the unit tests. The implementation should be fast, '
                'memory-efficient, and as simple as possible while meeting all '
                'requirements.'
            )
        )

    def _make_initial_prompt(self, python_interface: str, test_str: str) -> str:
        """
        Creates the initial prompt for generating an interface implementation.

        Args:
            python_interface: The string representation of the Python interface.
            test_str: The string representation of the unit tests for the interface.

        Returns:
            The prompt string.
        """
        example_impl = textwrap.dedent('''
            from my_interface import MyInterface

            class MyInterfaceImpl(MyInterface):
                def __init__(self, message: str):
                    super().__init__()
                    self._message = message

                def foo(self) -> str:
                    return self._message
            ''')

        return (
            'Generate an implementation of the following python interface:\n\n'
            f'{utils.wrap_code_in_markdown(python_interface)}'
            'Make sure the name of the class ends with "Impl", and it inherits from '
            'the interface. The code you will generate is *not* an abstract class, '
            'and does *not* have any `@abstractmethod` annotations. The interface '
            'itself already exists in the same directory, so do not add it here. '
            'The test suite that should pass looks like this:\n\n'
            f'{utils.wrap_code_in_markdown(test_str)}'
            'An example implementation might look something like this:\n\n'
            f'{utils.wrap_code_in_markdown(example_impl)}'
        )

    def _make_improvement_prompt(
            self, python_interface: str, test_str: str,
            prior_attempts: list[GenerationAttempt] | None = None
    ) -> str:
        """
        Creates a prompt to improve a previously generated implementation.

        Args:
            python_interface: The string representation of the Python interface.
            test_str: The string representation of the unit tests for the interface.
            prior_attempts: A list of previous generation attempts. Defaults to None.

        Returns:
            The improvement prompt string.
        """
        if prior_attempts is None:
            prior_attempts = []

        # This variable is currently unused, but kept for possible future use
        _ = textwrap.dedent('''
            from my_interface import MyInterface

            class MyInterfaceImpl(MyInterface):
                def __init__(self, message: str):
                    super().__init__()
                    self._message = message

                def foo(self) -> str:
                    return self._message
            ''')

        return (
            'You were previously asked to generate an implementation of the following python interface:\n\n'
            f'{utils.wrap_code_in_markdown(python_interface)}'
            'Your response was as follows:\n\n'
            f'{utils.wrap_code_in_markdown(prior_attempts[-1].code)}'
            'Your instructions were to make sure the name of the class ends with "Impl", '
            'and it inherits from the interface. You can assume the interface exists '
            'the same directory as the implementation being generated. '
            'The test suite that was run looks like this:\n\n'
            f'{utils.wrap_code_in_markdown(test_str)}'
            'When the tests were run, the following output indicates some problems:'
            f'```\n{prior_attempts[-1].errors}\n```\n\n'
            'Please generate a new implementation according to the same instructions, '
            'and make sure the problems are addressed so that all tests pass.'
        )

    def str_to_str(self, request: ImplGenerationRequest) -> str:
        """
        Generates an interface implementation as a string.

        Args:
            request: The implementation generation request.

        Returns:
            The generated implementation code as a string.
        """
        if request.prior_attempts:
            prompt = self._make_improvement_prompt(
                request.interface_str, request.test_str, request.prior_attempts
            )
        else:
            prompt = self._make_initial_prompt(request.interface_str, request.test_str)

        result = asyncio.run(self._impl_creator_agent.run(prompt))
        return utils.extract_code(result.data)

    def str_to_file(self, request: ImplGenerationRequest, output_path: str) -> str:
        """
        Generates an interface implementation and saves it to a file.

        Args:
            request: The implementation generation request.
            output_path: The path to save the generated implementation.

        Returns:
            The generated implementation code as a string.
        """
        impl_str = self.str_to_str(request)
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(impl_str)
        return impl_str


if __name__ == "__main__":
    load_dotenv()

    example_interface = textwrap.dedent("""
        from abc import ABC, abstractmethod

        class Calculator(ABC):

            @abstractmethod
            def add(a: int, b: int) -> int:
                \"\"\"Adds a and b\"\"\"
                pass

            @abstractmethod
            def subtract(a: int, b: int) -> int:
                \"\"\"Subtracts b from a\"\"\"
                pass

            @abstractmethod
            def product(a: int, b: int) -> int:
                \"\"\"Returns the product of a and b\"\"\"
                pass
        """)

    # Create the request object separately to keep the print line shorter.
    example_req = ImplGenerationRequest(
        interface_str=example_interface,
        test_str=""
    )
    print(ImplGenerator().str_to_str(request=example_req))

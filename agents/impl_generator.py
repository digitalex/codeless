import asyncio
from pydantic_ai import Agent
from dotenv import load_dotenv
import textwrap
from . import utils
from .models import GenerationAttempt, ImplGenerationRequest


class ImplGenerator:

    def __init__(self, model_str: str = ''):
        """Model strings supported: 'openai:gpt-4o' and 'google-gla:gemini-1.5-flash'"""
        self._impl_creator_agent = Agent(
            model_str or 'openai:gpt-4o',
            system_prompt=(
                'Your job is to implement an interface, making sure the implementation passes all the unit tests. '
                'The implementation should be fast, memory-efficient, and as simple as possible while meeting all requirements.')
        )

    def _make_initial_prompt(self, python_interface: str, test_str: str) -> str:
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
            'Make sure the name of the class ends with "Impl", and it inherits from the interface. '
            'The code you will generate is *not* an abstract class, and does *not* have any `@abstractmethod` annotations. '
            'The interface itself already exists in the same directory, so do not add it here. '
            'The test suite that should pass looks like this:\n\n'
            f'{utils.wrap_code_in_markdown(test_str)}'
            'An example implementation might look something like this:\n\n'
            f'{utils.wrap_code_in_markdown(example_impl)}'
        )

    def _make_improvement_prompt(
            self, python_interface: str, test_str: str, prior_attempts: list[GenerationAttempt] = []
    ) -> str:
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
            'Your instructions were to make sure the name of the class ends with "Impl", and it inherits from the interface. '
            'You can assume the interface exists the same directory as the implementation being generated. '
            'The test suite that was run looks like this:\n\n'
            f'{utils.wrap_code_in_markdown(test_str)}'
            'When the tests were run, the following output indicates some problems:'
            f'```\n{prior_attempts[-1].errors}\n```\n\n'
            'Please generate a new implementation according to the same instructions, '
            'and make sure the problems are addressed so that all tests pass.'
        )

    def str_to_str(self, request: ImplGenerationRequest) -> str:
        """Returns the test implementation code."""
        if request.prior_attempts:
            prompt = self._make_improvement_prompt(request.interface_str, request.test_str, request.prior_attempts)
        else:
            prompt = self._make_initial_prompt(request.interface_str, request.test_str)

        result = asyncio.run(self._impl_creator_agent.run(prompt))
        return utils.extract_code(result.data)

    def str_to_file(self, request: ImplGenerationRequest, output_path: str) -> str:
        impl_str = self.str_to_str(request)
        with open(output_path, 'w') as output_file:
            output_file.write(impl_str)
        return impl_str


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

    request = ImplGenerationRequest(interface_str=example_interface, test_str="")
    print(ImplGenerator().str_to_str(request))

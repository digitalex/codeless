from pydantic_ai import Agent
from dotenv import load_dotenv
import textwrap
from . import utils


class ImplGenerator:

    def __init__(self, model_str: str | None = None):
        """Model strings supported: 'openai:gpt-4o' and 'google-gla:gemini-1.5-flash'"""
        self._impl_creator_agent = Agent(
            model_str or 'openai:gpt-4o',
            system_prompt=(
                'Your job is to implement an interface, making sure the implementation passes all the unit tests. '
                'The implementation should be fast, memory-efficient, and as simple as possible while meeting all requirements.')  
        )

    def _make_initial_prompt(self, python_interface: str) -> str:
        example_impl = textwrap.dedent('''
            from interfaces.my_interface import MyInterface

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
            'You can assume the interface exists in a package named `interfaces`, like in the following example:\n\n'
            f'{utils.wrap_code_in_markdown(example_impl)}'
        )

    def _make_improvement_prompt(self, python_interface: str, test_str: str, previous_impl: str, test_output: str) -> str:
        example_impl = textwrap.dedent('''
            from interfaces.my_interface import MyInterface

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
            f'{utils.wrap_code_in_markdown(previous_impl)}'
            'Your instructions were to make sure the name of the class ends with "Impl", and it inherits from the interface. '
            'You can assume the interface exists in a package named `interfaces`. '
            'The test suite that was run looks like this:\n'
            f'{utils.wrap_code_in_markdown(test_str)}'
            'When the tests were run, the following output indicates some problems:'
            f'```\n{test_output}\n\n'
            'Please generate a new implementation according to the same instructions, '
            'and make sure the problems are addressed so that all tests pass.'
        )

    def str_to_str(self, python_interface: str, previous_impl:str | None = None, test_str: str | None = None, feedback: str | None = None) -> str:
        """Returns the test implementation code."""
        if previous_impl and feedback:
            prompt = self._make_improvement_prompt(python_interface, test_str, previous_impl, feedback)
        else:
            prompt = self._make_initial_prompt(python_interface)

        result = self._impl_creator_agent.run_sync(prompt)
        return utils.extract_code(result.data)

    def str_to_file(self, interface_str: str, output_path: str, previous_impl:str | None = None, test_str: str | None = None, feedback: str | None = None) -> str:
        impl_str = self.str_to_str(interface_str, test_str=test_str, previous_impl=previous_impl, feedback=feedback)
        with open(output_path, 'w') as output_file:
            output_file.write(impl_str)
        return impl_str


if __name__ == "__main__":
    load_dotenv()

    example_interface = textwrap.dedent('''
        class Calculator:
            def add(a: int, b: int) -> int:
                """Adds a and b"""
                pass

            def subtract(a: int, b: int) -> int:
                """Subtracts b from a"""
                pass

            def product(a: int, b: int) -> int:
                """Returns the product of a and b"""
                pass
        ''')

    print(ImplGenerator().str_to_str(example_interface))
"""
A demonstration script for generating and testing interface implementations using AI.

This script showcases the capabilities of the `ImplGenerator` and `TestGenerator`
agents to automatically create Python code based on interface definitions and
to generate unit tests for these interfaces.

It allows users to select from predefined examples (math, microblog, calculator, snake)
and observes the AI's attempts to generate implementations and tests that satisfy
the requirements.
"""
import os
import py_compile
import sys
import textwrap
import unittest

from dotenv import load_dotenv
import logfire # type: ignore
from pydantic import BaseModel

from agents import impl_generator, test_generator


# Define the Pydantic model Example
class Example(BaseModel):
    """
    Represents an example interface to be implemented.
    """
    code: str
    project_name: str
    filename: str


math_utils = Example(
    project_name='math-utils',
    filename='math_utils.py',
    code=textwrap.dedent("""
        from abc import ABC, abstractmethod

        class MathUtils(ABC):
            @abstractmethod
            def fibonacci(self, n: int) -> int:
                \"\"\"An optimal implementation that returns the Nth fibonacci number.\"\"\"
                pass

            @abstractmethod
            def gcd(self, nums: list[int]) -> int:
                \"\"\"Returns the largest positive integer that can divide each of input numbers without a remainder.\"\"\"
                pass
        """))

calculator = Example(
    project_name='calculator',
    filename='calculator.py',
    code=textwrap.dedent("""
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
        """))

microblog_dao = Example(
    project_name='microblog-dao',
    filename='microblog_dao.py',
    code=textwrap.dedent("""
        from abc import ABC, abstractmethod

        class MicroblogDao(ABC):
            @abstractmethod
            def post(self, user_id: str, post_content: str) -> str:
                \"\"\"Stores the post in the database, returning the post ID.\"\"\"
                pass

            @abstractmethod
            def delete_post(self, post_id: str) -> None:
                \"\"\"Deletes the given post. Raises ValueError if post is not found.\"\"\"
                pass
        """))

# This is a more difficult example, but really fun to try!
snake_game_engine = Example(
    project_name='snake-game-engine',
    filename='snake_game_engine.py',
    code=textwrap.dedent("""
        from abc import ABC, abstractmethod

        class SnakeGameEngine(ABC):
            \"\"\"A game engine for the classic Snake game. This calculates the state of the board at each tick.
            The board is a rectangle. There is no food for the snake, which means it will never grow.
            It is assumed that the snake moves forward in its current direction at a speed of one position per tick.
            \"\"\"

            def __init__(self, snake_length: int = 5, board_width: int = 240, board_height: int = 180):
                pass

            @abstractmethod
            def tick(self, snake_direction: int = 0) -> int:
                \"\"\"Advances the state of the board, e.g. moves the snake 1 spot in the given direction.
                Directions are 0 for down, 1 for left, 2 for up and 3 for right.
                \"\"\"
                pass

            @abstractmethod
            def get_snake_state(self) -> list[tuple[int, int]]:
                \"\"\"Returns a list of positions of the board on which to draw the snake..\"\"\"
                pass
        """))


def run_tests(start_dir: str) -> tuple[bool, str]:
    """
    Discovers and runs unit tests in a specified directory.

    Args:
        start_dir: The directory to search for tests (pattern: *_test.py).

    Returns:
        A tuple containing:
            - bool: True if all tests passed, False otherwise.
            - str: A string detailing test errors and failures, or "All tests pass!".
    """
    test_suite = unittest.defaultTestLoader.discover(start_dir=start_dir,
                                                     pattern='*_test.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite) # type: unittest.TextTestResult
    if result.wasSuccessful():
        return True, "All tests pass!"

    output = []
    if result.errors:
        output.append("\nErrors:")
        for test, err in result.errors:
            output.append(f"  Test: {test}")
            output.append(f"  Error: {err}")

    if result.failures:
        output.append("\nFailures:")
        for test, fail in result.failures:
            output.append(f"  Test: {test}")
            output.append(f"  Failure: {fail}")

    return False, '\n'.join(output)


def try_compile_file(code_file: str) -> str:
    """
    Attempts to compile a Python file and returns any compilation errors.

    Args:
        code_file: The path to the Python file to compile.

    Returns:
        An empty string if compilation is successful, otherwise the error message.
    """
    try:
        py_compile.compile(code_file, doraise=True)
        return ''
    except py_compile.PyCompileError as e:
        return str(e)


def main(example_name: str):
    """
    Main function to run the AI code generation and testing demo.

    Args:
        example_name: The name of the example to run (e.g., 'math', 'calculator').
    """
    load_dotenv()
    try:
        logfire.configure(send_to_logfire='if-token-present')
    except Exception as e: # pylint: disable=broad-except
        print(f"Couldn't configure logfire: {e}")

    example: Example | None = None
    if example_name == 'math':
        example = math_utils
    elif example_name == 'microblog':
        example = microblog_dao
    elif example_name == 'calculator':
        example = calculator
    elif example_name == 'snake':
        example = snake_game_engine
    else:
        print(f'Unknown example `{example_name}`. Valid ones: math, microblog, '
              'calculator, snake')
        return # Exit if example is not found

    # Ensure example is assigned before use, though the return above should prevent this.
    if example is None:
        print("Error: Example not initialized.")
        return

    project_dir = os.path.join('output', example.project_name)
    os.makedirs(project_dir, exist_ok=True)
    iface_path = os.path.join(project_dir, example.filename)
    test_path = os.path.join(project_dir, example.filename.replace('.py', '_test.py'))
    impl_path = os.path.join(project_dir, example.filename.replace('.py', '_impl.py'))

    model = 'openai:gpt-4o' # Or 'google-gla:gemini-1.5-flash'
    test_gen = test_generator.TestGenerator(model_str=model)
    impl_gen = impl_generator.ImplGenerator(model_str=model)

    with open(iface_path, 'w', encoding='utf-8') as iface_file:
        iface_file.write(example.code)

    # Explicitly use keyword arguments for Pydantic models
    test_gen_request = test_generator.TestGenerationRequest(interface_str=example.code)
    if compilation_error := try_compile_file(iface_path):
        print(f'Your interface file has errors: {compilation_error}')
        return

    test_str = test_gen.str_to_file(request=test_gen_request, output_path=test_path)
    impl_gen_request = impl_generator.ImplGenerationRequest(
        interface_str=example.code,
        test_str=test_str
    )
    impl_str = impl_gen.str_to_file(request=impl_gen_request, output_path=impl_path)
    tests_pass, test_output = run_tests(project_dir)

    if not tests_pass:
        print(test_output)

    # We limit these rounds to curtail the API cost, but feel free to go wild.
    max_test_rounds = 10
    max_impl_rounds = 3
    num_test_rounds = max_test_rounds
    num_impl_rounds = max_impl_rounds
    test_attempts: list[impl_generator.GenerationAttempt] = [] # Type hint
    while not tests_pass and num_test_rounds > 0:
        impl_attempts: list[impl_generator.GenerationAttempt] = [] # Type hint
        while not tests_pass and num_impl_rounds > 0:
            print('Tests did not pass, trying another round of impl generation.')
            impl_attempts.append(
                impl_generator.GenerationAttempt(code=impl_str, errors=test_output)
            )
            # Explicitly use keyword arguments
            current_impl_request = impl_generator.ImplGenerationRequest(
                interface_str=example.code,
                test_str=test_str,
                prior_attempts=impl_attempts
            )
            impl_str = impl_gen.str_to_file(request=current_impl_request, output_path=impl_path)
            tests_pass, test_output = run_tests(project_dir)
            num_impl_rounds -= 1
        if tests_pass:
            break

        print('Could not make tests pass after max_impl_rounds, will regenerate tests instead')
        test_attempts.append(
            test_generator.GenerationAttempt(code=test_str, errors=test_output)
        )
        # Explicitly use keyword arguments
        current_test_request = test_generator.TestGenerationRequest(
            interface_str=example.code,
            prior_attempts=test_attempts
        )
        test_str = test_gen.str_to_file(request=current_test_request, output_path=test_path)
        tests_pass, test_output = run_tests(project_dir)
        num_impl_rounds = max_impl_rounds # Reset impl rounds for new test
        num_test_rounds -= 1

    if num_test_rounds > 0 or tests_pass: # Check tests_pass for the last attempt
        print(f"All done! Check out the implementation at {impl_path}")
    else:
        print(f'Unable to solve this after {max_test_rounds} test rounds '
              f'and {max_impl_rounds} implementation rounds per test.')


if __name__ == "__main__":
    SELECTED_EXAMPLE = 'math' # Default example
    if len(sys.argv) > 1:
        SELECTED_EXAMPLE = sys.argv[1]
    main(SELECTED_EXAMPLE)

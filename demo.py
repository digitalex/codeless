from agents import impl_generator
from agents import test_generator
from dataclasses import dataclass
from dotenv import load_dotenv
import os
import py_compile
import sys
import textwrap
import unittest
import logfire


@dataclass
class Example:
    code: str
    project_name: str
    filename: str


math_utils = Example(
    project_name='math-utils',
    filename='math_utils.py',
    code=textwrap.dedent('''
        from abc import ABC, abstractmethod

        class MathUtils(ABC):
            @abstractmethod
            def fibonacci(self, n: int) -> int:
                """An optimal implementation that returns the Nth fibonacci number."""
                pass

            @abstractmethod
            def gcd(self, nums: list[int]) -> int:
                """Returns the largest positive integer that can divide each of input numbers without a remainder."""
                pass
        ''')
)

calculator = Example(
    project_name='calculator',
    filename='calculator.py',
    code=textwrap.dedent('''
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
)

microblog_dao = Example(
    project_name='microblog-dao',
    filename='microblog_dao.py',
    code=textwrap.dedent('''
        from abc import ABC, abstractmethod

        class MicroblogDao(ABC):
            @abstractmethod
            def post(self, user_id: str, post_content: str) -> str:
                """Stores the post in the database, returning the post ID."""
                pass

            @abstractmethod
            def delete_post(self, post_id: str) -> None:
                """Deletes the given post. Raises ValueError if post is not found."""
                pass
        ''')
)

# This is a more difficult example, but really fun to try\!
snake_game_engine = Example(
    project_name='snake-game-engine',
    filename='snake_game_engine.py',
    code=textwrap.dedent('''
        from abc import ABC, abstractmethod

        class SnakeGameEngine(ABC):
            """A game engine for the classic Snake game. This calculates the state of the board at each tick.
            The board is a rectangle. There is no food for the snake, which means it will never grow.
            It is assumed that the snake moves forward in its current direction at a speed of one position per tick.
            """

            def __init__(self, snake_length: int = 5, board_width: int = 240, board_height: int = 180):
                pass

            @abstractmethod
            def tick(self, snake_direction: int = 0) -> int:
                """Advances the state of the board, e.g. moves the snake 1 spot in the given direction.
                Directions are 0 for down, 1 for left, 2 for up and 3 for right.
                """
                pass

            @abstractmethod
            def get_snake_state(self) -> list[tuple[int, int]]:
                """Returns a list of positions of the board on which to draw the snake.."""
                pass
        ''')
)


def run_tests(start_dir: str) -> tuple[bool, str]:
    test_suite = unittest.defaultTestLoader.discover(start_dir=start_dir, pattern='*_test.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result: unittest.TextTestResult = runner.run(test_suite)
    if result.wasSuccessful():
        return True, "All tests pass!"
    else:
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
    try:
        py_compile.compile(code_file, doraise=True)
        return ''
    except py_compile.PyCompileError as e:
        return str(e)


def main(example_name: str):
    load_dotenv()
    try:
        logfire.configure(send_to_logfire='if-token-present')
    except:  # noqa: E722
        print("Couldn't configure logfire, please check your environment variables.")

    if example_name == 'math':
        example = math_utils
    elif example_name == 'microblog':
        example = microblog_dao
    elif example_name == 'calculator':
        example = calculator
    elif example_name == 'snake':
        example = snake_game_engine
    else:
        print(f'Unknown example `{example_name}`. Valid ones: math, microblog, calculator, snake')

    project_dir = os.path.join('output', example.project_name)
    os.makedirs(project_dir, exist_ok=True)
    iface_path = os.path.join(project_dir, example.filename)
    test_path = os.path.join(project_dir, example.filename.replace('.py', '_test.py'))
    impl_path = os.path.join(project_dir, example.filename.replace('.py', '_impl.py'))

    model = 'openai:gpt-4o'
    test_gen = test_generator.TestGenerator(model_str=model)
    impl_gen = impl_generator.ImplGenerator(model_str=model)

    with open(iface_path, 'w') as iface_file:
        iface_file.write(example.code)

    request = test_generator.TestGenerationRequest(interface_str=example.code)
    if compilation_error := try_compile_file(iface_path):
        print(f'Your interface file has errors: {compilation_error}')
        return

    test_str = test_gen.str_to_file(request, test_path)
    impl_str = impl_gen.str_to_file(impl_generator.ImplGenerationRequest(example.code, test_str), impl_path)
    tests_pass, test_output = run_tests(project_dir)

    if not tests_pass:
        print(test_output)

    # We limit these rounds to curtail the API cost, but feel free to go wild.
    max_test_rounds = 10
    max_impl_rounds = 3
    num_test_rounds = max_test_rounds
    num_impl_rounds = max_impl_rounds
    test_attempts = []
    while not tests_pass and num_test_rounds > 0:
        impl_attempts = []
        while not tests_pass and num_impl_rounds > 0:
            print('Tests did not pass, trying another round of impl generation.')
            impl_attempts.append(impl_generator.GenerationAttempt(impl_str, test_output))
            impl_request = impl_generator.ImplGenerationRequest(example.code, test_str, impl_attempts)
            impl_str = impl_gen.str_to_file(impl_request, impl_path)
            tests_pass, test_output = run_tests(project_dir)
            num_impl_rounds -= 1
        if tests_pass:
            break

        print('Could not make tests pass after 5 attempts, will regenerate tests instead')
        test_attempts.append(test_generator.GenerationAttempt(test_str, test_output))
        request = test_generator.TestGenerationRequest(interface_str=example.code, prior_attempts=test_attempts)
        test_str = test_gen.str_to_file(request, test_path)
        tests_pass, test_output = run_tests(project_dir)
        num_impl_rounds = max_impl_rounds
        num_test_rounds -= 1

    if num_test_rounds > 0:
        print(f"All done! Check out the implementation at {impl_path}")
    else:
        print(f'Unable to solve this after {max_impl_rounds * max_test_rounds} attempts.')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main('math')

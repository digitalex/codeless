import os
import re
import textwrap
import unittest
from dotenv import load_dotenv
from agents import impl_generator
from agents import test_generator

def camel_to_snake(input: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', input).lower()

def run_tests(start_dir: str) -> tuple[bool, str]:
    test_suite = unittest.defaultTestLoader.discover(start_dir=start_dir, pattern='*_test.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result: unittest.TextTestResult = runner.run(test_suite)
    if result.wasSuccessful():
        return True, ''
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


def main():
    load_dotenv()

    # take the interface (or fake it) and a name - write to output/{project}/interfaces
    # generate unit tests, write to output/{project}/
    # generate initial impl, write to output/{project}/*_impl.py
    # hand-make unit test harness
    # while (no tests or tests failing):
        # run the test harness, collect output
        # generate improved impl, write to output/{project}/*_impl.py
    # project_id = 'garbanzo-beans'
    # example_interface_classname = 'Calculator'
    # example_interface = textwrap.dedent('''
    #     class Calculator:
    #         def add(a: int, b: int) -> int:
    #             """Adds a and b"""
    #             pass

    #         def subtract(a: int, b: int) -> int:
    #             """Subtracts b from a"""
    #             pass

    #         def product(a: int, b: int) -> int:
    #             """Returns the product of a and b"""
    #             pass
    #     ''')

    # project_id = 'microblog-dao'
    # example_interface_classname = 'MicroblogDao'
    # example_interface = textwrap.dedent('''
    #     from abc import ABC, abstractmethod

    #     class MicroblogDao(ABC):
    #         @abstractmethod
    #         def post(self, user_id: str, post_content: str) -> str:
    #             """Stores the post in the database, returning the post ID."""
    #             pass

    #         @abstractmethod
    #         def delete_post(self, post_id: str) -> None:
    #             """Deletes the given post. Raises ValueError if post is not found."""
    #             pass
    #     ''')

    # project_id = 'math-utils'
    # example_interface_classname = 'MathUtils'
    # example_interface = textwrap.dedent('''
    #     from abc import ABC, abstractmethod

    #     class MathUtils(ABC):
    #         @abstractmethod
    #         def fibonacci(self, n: int) -> int:
    #             """An optimal implementation that returns the Nth fibonacci number."""
    #             pass

    #         @abstractmethod
    #         def gcd(self, nums: list[int]) -> int:
    #             """Returns the largest positive integer that can divide each of input numbers without a remainder."""
    #             pass
    #     ''')

    project_id = 'snake-game-engine'
    example_interface_classname = 'SnakeGameEngine'
    example_interface = textwrap.dedent('''
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

    filename_prefix = camel_to_snake(example_interface_classname)
    project_dir = os.path.join('output', project_id)
    os.makedirs(project_dir, exist_ok=True)
    
    iface_path = os.path.join(project_dir, filename_prefix + '.py')
    test_path = os.path.join(project_dir, filename_prefix + '_test.py')    
    impl_path = os.path.join(project_dir, filename_prefix + '_impl.py')

    model = 'claude-3-5-sonnet-latest'
    test_gen = test_generator.TestGenerator(model_str=model)
    impl_gen = impl_generator.ImplGenerator(model_str=model)

    with open(iface_path, 'w') as iface_file:
        iface_file.write(example_interface)

    test_str = test_gen.str_to_file(example_interface, test_path)
    impl_str = impl_gen.str_to_file(example_interface, impl_path)
    tests_pass, test_output = run_tests(project_dir)
    
    if not tests_pass:
        print(test_output)

    num_test_rounds = 10
    num_impl_rounds = 3
    while not tests_pass and num_test_rounds > 0:
        while not tests_pass and num_impl_rounds > 0:
            print('Tests did not pass, trying another round of impl generation.')
            new_impl_str = impl_gen.str_to_str(example_interface, impl_str, test_str, test_output)
            with open(impl_path, 'w') as impl_file:
                impl_file.write(new_impl_str)

            tests_pass, test_output = run_tests(project_dir)
            num_impl_rounds -= 1
        
        if tests_pass:
            break
        print('Could not make tests pass after 5 attempts, will regenerate tests instead')
        test_str = test_gen.str_to_file(example_interface, test_path)
        tests_pass, test_output = run_tests(project_dir)
        num_impl_rounds = 5
        num_test_rounds -= 1


    if num_test_rounds > 0:
        print('All done!')
    else:
        print('Unable to solve this after 15 attempts.')


if __name__ == "__main__":
    main()
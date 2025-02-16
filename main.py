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

    project_id = 'microblog-dao'
    example_interface_classname = 'MicroblogDao'
    example_interface = textwrap.dedent('''
        class MicroblogDao:
            def post(self, user_id: str, post_content: str) -> str:
                """Stores the post in the database, returning the post ID."""
                pass

            def delete_post(self, post_id: str) -> None:
                """Deletes the given post. Raises ValueError if post is not found."""
                pass
        ''')

    filename_prefix = camel_to_snake(example_interface_classname)
    project_dir = os.path.join('output', project_id)
    os.makedirs(os.path.join(project_dir, 'interfaces'), exist_ok=True)
    
    iface_package_path = os.path.join('output', project_id, 'interfaces', '__init__.py')
    iface_path = os.path.join(project_dir, 'interfaces', filename_prefix + '.py')
    test_path = os.path.join(project_dir, filename_prefix + '_test.py')    
    impl_path = os.path.join(project_dir, filename_prefix + '_impl.py')

    test_gen = test_generator.TestGenerator()
    impl_gen = impl_generator.ImplGenerator()

    with open(iface_package_path, 'w') as iface_package_file:
        iface_package_file.write('')

    with open(iface_path, 'w') as iface_file:
        iface_file.write(example_interface)

    test_str = test_gen.str_to_file(example_interface, test_path)
    impl_str = impl_gen.str_to_file(example_interface, impl_path)
    tests_pass, test_output = run_tests(project_dir)
    
    if not tests_pass:
        print(test_output)
    
    while not tests_pass:
        print('Tests did not pass, trying another round of impl generation.')
        new_impl_str = impl_gen.str_to_str(example_interface, impl_str, test_str, test_output)
        with open(impl_path, 'w') as impl_file:
            impl_file.write(new_impl_str)

        tests_pass, test_output = run_tests(project_dir)

    print('All tests pass!')


if __name__ == "__main__":
    main()
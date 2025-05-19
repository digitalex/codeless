"""
This script provides a command-line interface (CLI) to manage an AI-driven
code generation workflow. It watches a project directory for changes to
interface files, then automatically generates tests and implementations.

Workflow:
- Watches a specified project directory under `./output/`.
- On new/modified interface file:
    - Triggers test generation loop.
    - User is prompted to review/modify tests.
- On new/modified test file (and interface compiles):
    - Triggers implementation generation loop.
    - Notifies user of success or if it gives up after multiple attempts.
"""
import os
import py_compile
import sys
import time
import unittest
from enum import Enum

from dotenv import load_dotenv
import logfire # type: ignore
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from agents import impl_generator, test_generator


def run_tests(start_dir: str) -> tuple[bool, str]:
    """
    Discovers and runs tests within a specified directory using unittest.

    Args:
        start_dir: The directory path from which to discover tests
                   (files matching '*_test.py').

    Returns:
        A tuple containing:
            - bool: True if all tests passed, False otherwise.
            - str: A formatted string containing details of any errors or failures,
                   or an empty string if all tests passed.
    """
    test_suite = unittest.defaultTestLoader.discover(start_dir=start_dir,
                                                     pattern='*_test.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite) # type: unittest.TextTestResult
    if result.wasSuccessful():
        return True, ''

    # De-indented else block
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
    Attempts to compile a given Python source file.

    Uses `py_compile.compile` to check for syntax errors.

    Args:
        code_file: The path to the Python file to compile.

    Returns:
        An empty string if the compilation is successful.
        The error message string from PyCompileError if compilation fails.
    """
    try:
        py_compile.compile(code_file, doraise=True)
        return ''
    except py_compile.PyCompileError as e:
        return str(e)


class FileKind(Enum):
    """Enumeration for the kind of Python file being handled."""
    IFACE = 1
    TEST = 2
    IMPL = 3


def guess_file_kind(filename: str) -> FileKind:
    """
    Guesses the kind of file based on its name.

    Args:
        filename: The name of the file.

    Returns:
        The guessed FileKind.
    """
    if '_impl.py' in filename: # More specific check
        return FileKind.IMPL
    if '_test.py' in filename: # More specific check
        return FileKind.TEST
    return FileKind.IFACE


class ProjectEventHandler(FileSystemEventHandler):
    """
    Handles file system events for a project, triggering code generation loops.
    """
    def __init__(self, working_dir: str,
                 test_gen: test_generator.TestGenerator,
                 impl_gen: impl_generator.ImplGenerator):
        """
        Initializes the ProjectEventHandler.

        Args:
            working_dir: The root directory of the project being watched.
            test_gen: An instance of TestGenerator.
            impl_gen: An instance of ImplGenerator.
        """
        super().__init__()
        self._test_gen = test_gen
        self._impl_gen = impl_gen
        self._working_dir = working_dir

    def test_iteration_loop(self, iface_path: str) -> None:
        """
        Iterates on test creation until the generated test file compiles.

        Args:
            iface_path: Path to the interface file.
        """
        print(f"Starting test iteration loop for {iface_path}...")
        try:
            with open(iface_path, 'r', encoding='utf-8') as iface_file:
                iface_str = iface_file.read()
        except IOError as e:
            print(f"Error reading interface file {iface_path}: {e}")
            return

        test_path = iface_path.replace('.py', '_test.py')
        # Explicit keyword args for Pydantic model
        request = test_generator.TestGenerationRequest(interface_str=iface_str)
        test_str = self._test_gen.str_to_file(request=request, output_path=test_path)
        compilation_error = try_compile_file(test_path)

        attempts_count = 0
        max_attempts = 5 # Limit attempts to prevent infinite loops

        while compilation_error and attempts_count < max_attempts:
            attempts_count += 1
            print(f"Test compilation failed (Attempt {attempts_count}/{max_attempts}): {compilation_error}")
            # Explicit keyword args for Pydantic model
            attempt = test_generator.GenerationAttempt(code=test_str, errors=compilation_error)
            request_args = {
                "interface_str": iface_str,
                "prior_attempts": [attempt],
            }
            request = test_generator.TestGenerationRequest(**request_args)
            test_str = self._test_gen.str_to_file(request=request, output_path=test_path)
            compilation_error = try_compile_file(test_path)

        if compilation_error:
            print_msg = (f"Failed to generate a compilable test for {iface_path} "
                         f"after {max_attempts} attempts.")
            print(print_msg)
        else:
            print(f"Successfully generated compilable test file: {test_path}")


    def impl_iteration_loop(self, iface_path: str, test_path: str) -> None:
        """
        Iterates on implementation creation until tests pass or max attempts are reached.

        Args:
            iface_path: Path to the interface file.
            test_path: Path to the test file.
        """
        print(f"Starting implementation iteration loop for {iface_path} with test {test_path}...")
        try:
            with open(iface_path, 'r', encoding='utf-8') as iface_file:
                iface_str = iface_file.read()
            with open(test_path, 'r', encoding='utf-8') as test_file:
                test_str = test_file.read()
        except IOError as e:
            print(f"Error reading interface or test file: {e}")
            return

        impl_path = iface_path.replace('.py', '_impl.py')
        # Explicit keyword args for Pydantic model
        request = impl_generator.ImplGenerationRequest(
            interface_str=iface_str,
            test_str=test_str
        )
        impl_str = self._impl_gen.str_to_file(request=request, output_path=impl_path)
        tests_pass, test_output = run_tests(self._working_dir)
        attempts: list[impl_generator.GenerationAttempt] = [] # Type hint
        attempts_count = 0
        max_attempts = 5 # Limit attempts

        while not tests_pass and attempts_count < max_attempts:
            attempts_count +=1
            print(f"Implementation tests failed (Attempt {attempts_count}/{max_attempts}). Output:\n{test_output}")
            # Explicit keyword args for Pydantic model
            attempts.append(impl_generator.GenerationAttempt(code=impl_str, errors=test_output))
            request_args = {
                "interface_str": iface_str,
                "test_str": test_str,
                "prior_attempts": attempts,
            }
            request = impl_generator.ImplGenerationRequest(**request_args)
            impl_str = self._impl_gen.str_to_file(request=request, output_path=impl_path)
            tests_pass, test_output = run_tests(self._working_dir)

        if tests_pass:
            print(f"Successfully generated implementation and passed all tests for {iface_path}!")
        else:
            print_msg = (f"Failed to pass tests for {iface_path} after {max_attempts} "
                         "implementation attempts.")
            print(print_msg)


    def on_created(self, event):
        """Called when a file or directory is created."""
        super().on_created(event)
        if not event.is_directory:
            print(f'File created: {event.src_path}')
            kind = guess_file_kind(event.src_path)
            if kind == FileKind.IFACE:
                input_str = (f"Interface file {event.src_path} detected. "
                             "Press Enter to continue generating tests.")
                user_input = input(input_str)
                if user_input == "": # Check if user pressed Enter
                    if compilation_errors := try_compile_file(event.src_path):
                        print(f'Your interface file has errors: {compilation_errors}')
                    else:
                        self.test_iteration_loop(event.src_path)

    def on_modified(self, event):
        """Called when a file or directory is modified."""
        super().on_modified(event)
        if not event.is_directory:
            print(f'File modified: {event.src_path}')
            kind = guess_file_kind(event.src_path)
            if kind == FileKind.IFACE:
                if compilation_errors := try_compile_file(event.src_path):
                    print(f'Your interface file has errors: {compilation_errors}')
                else:
                    input_str = (f"Interface file {event.src_path} change detected. "
                                 "Press Enter to continue generating tests.")
                    user_input = input(input_str)
                    if user_input == "":
                        self.test_iteration_loop(event.src_path)
            elif kind == FileKind.TEST: # Use elif for clarity
                if compilation_error := try_compile_file(event.src_path):
                    print(f'Test file {event.src_path} has errors: {compilation_error}')
                else:
                    prompt_message = (
                        f"Test file {event.src_path} change detected. "
                        "Press Enter to continue implementing the interface."
                    )
                    user_input = input(prompt_message)
                    if user_input == "":
                        # Ensure iface_path is correctly derived if original was _test.py
                        iface_path = event.src_path.replace('_test.py', '.py')
                        # Check if original might have been _impl.py (less likely here but good practice)
                        iface_path = iface_path.replace('_impl.py', '.py')
                        self.impl_iteration_loop(iface_path, event.src_path)

    def on_deleted(self, event):
        """Called when a file or directory is deleted."""
        super().on_deleted(event)
        if not event.is_directory:
            print(f"File deleted: {event.src_path}")
        # Potentially clean up related generated files if an interface is deleted.

    def on_moved(self, event):
        """Called when a file or directory is moved or renamed."""
        super().on_moved(event)
        if not event.is_directory: # is_directory can be None for moved events
            print(f"File moved: from {event.src_path} to {event.dest_path}")
        # Handle moved files, potentially re-triggering loops for the new path.


def main(project_id: str):
    """
    Main function to set up the project directory, AI generators, and file watcher.

    Args:
        project_id: A unique identifier for the project.
    """
    load_dotenv()
    try:
        logfire.configure(send_to_logfire='if-token-present')
    except Exception as e: # pylint: disable=broad-except
        print(f"Could not configure logfire: {e}")

    project_dir = os.path.join('output', project_id)
    os.makedirs(project_dir, exist_ok=True)
    print(f"Watching project directory: {os.path.abspath(project_dir)}")

    # model = 'claude-3-5-sonnet-latest'
    # model = 'google-gla:gemini-1.5-flash'
    model = 'openai:gpt-4o'
    test_gen_instance = test_generator.TestGenerator(model_str=model)
    impl_gen_instance = impl_generator.ImplGenerator(model_str=model)

    event_handler = ProjectEventHandler(
        working_dir=project_dir,
        test_gen=test_gen_instance,
        impl_gen=impl_gen_instance
    )
    observer = Observer()
    observer.schedule(event_handler, project_dir, recursive=False)
    observer.start()
    print("File watcher started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("File watcher stopping...")
        observer.stop()
    observer.join()
    print("File watcher stopped.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python start.py <unique_project_id>')
    else:
        main(project_id=sys.argv[1])

# Create project dir, then watch it for changes
# If new interface file: enter test iteration loop.
# If test changes and compiles, enter impl iteration loop.
#
# Test iteration loop
# 1. Run test gen w/compile loop
# 2. When compiles, pause and ask user to nudge when ready.
# 3. Start impl iteration loop
#
# Impl iteration loop
# 1. Impl generation/test loop.
# 2. Notify user when done, or when giving up.

from agents import impl_generator
from agents import test_generator
from dotenv import load_dotenv
from enum import Enum
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import logfire
import os
import py_compile
import sys
import time
import unittest


def run_tests(start_dir: str) -> tuple[bool, str]:
    """Discovers and runs tests within a specified directory using unittest.

    Args:
        start_dir: The directory path from which to discover tests (files matching '*_test.py').

    Returns:
        A tuple containing:
            - bool: True if all tests passed, False otherwise.
            - str: A formatted string containing details of any errors or failures,
                   or an empty string if all tests passed.
    """
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


def try_compile_file(code_file: str) -> str:
    """Attempts to compile a given Python source file.

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
    IFACE = 1
    TEST = 2
    IMPL = 3


def guess_file_kind(filename: str) -> FileKind:
    if '_impl' in filename:
        return FileKind.IMPL
    if '_test' in filename:
        return FileKind.TEST
    return FileKind.IFACE


class ProjectEventHandler(FileSystemEventHandler):
    def __init__(self, working_dir: str, test_gen: test_generator.TestGenerator, impl_gen: impl_generator.ImplGenerator):
        self._test_gen = test_gen
        self._impl_gen = impl_gen
        self._working_dir = working_dir

    def test_iteration_loop(self, iface_path: str) -> None:
        """Iterates on test creation, returning the finished file."""
        with open(iface_path, 'r') as iface_file:
            iface_str = iface_file.read()

        test_path = iface_path.replace('.py', '_test.py')
        request = test_generator.TestGenerationRequest(interface_str=iface_str)
        test_str = self._test_gen.str_to_file(request, test_path)
        if compilation_error := try_compile_file(test_path):
            attempt = test_generator.GenerationAttempt(code=test_str, errors=compilation_error)
            request = test_generator.TestGenerationRequest(interface_str=iface_str, prior_attempts=[attempt])
            test_str = self._test_gen.str_to_file(request, test_path)

    def impl_iteration_loop(self, iface_path: str, test_path: str) -> None:
        """Iterates on impl creation, returning the finished file."""
        with open(iface_path, 'r') as iface_file:
            iface_str = iface_file.read()
        with open(test_path, 'r') as test_file:
            test_str = test_file.read()

        impl_path = iface_path.replace('.py', '_impl.py')
        request = impl_generator.ImplGenerationRequest(iface_str, test_str)
        impl_str = self._impl_gen.str_to_file(request, impl_path)
        tests_pass, test_output = run_tests(self._working_dir)
        attempts = []
        while not tests_pass:
            attempts.append(impl_generator.GenerationAttempt(code=impl_str, errors=test_output))
            request = impl_generator.ImplGenerationRequest(iface_str, test_str, attempts)
            impl_str = self._impl_gen.str_to_file(request, impl_path)
            tests_pass, test_output = run_tests(self._working_dir)

    def on_created(self, event):
        if not event.is_directory:
            print(f'File created: {event.src_path}')
            kind = guess_file_kind(event.src_path)
            if kind == FileKind.IFACE:
                input(f"Interface file {event.src_path} detected. Press Enter to continue generating tests.")
                if compilation_errors := try_compile_file(event.src_path):
                    print(f'Your interface file has errors: {compilation_errors}')
                else:
                    self.test_iteration_loop(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            print(f'File modified: {event.src_path}')
            kind = guess_file_kind(event.src_path)
            if kind == FileKind.IFACE:
                if compilation_errors := try_compile_file(event.src_path):
                    print(f'Your interface file has errors: {compilation_errors}')
                else:
                    input(f"Interface file {event.src_path} change detected. Press Enter to continue generating tests.")
                    self.test_iteration_loop(event.src_path)
            if kind == FileKind.TEST:
                if compilation_error := try_compile_file(event.src_path):
                    print(f'Test file {event.src_path} has errors: {compilation_error}')
                else:
                    input(f"Test file {event.src_path} change detected. Press Enter to continue implementing the interface.")
                    iface_path = event.src_path.replace('_impl.py', '.py')
                    self.impl_iteration_loop(iface_path, event.src_path)

    def on_deleted(self, event):
        pass

    def on_moved(self, event):
        pass


def main(project_id: str):
    load_dotenv()
    logfire.configure(send_to_logfire='if-token-present')
    project_dir = os.path.join('output', project_id)
    os.makedirs(project_dir, exist_ok=True)
    model = 'claude-3-5-sonnet-latest'
    test_gen = test_generator.TestGenerator(model_str=model)
    impl_gen = impl_generator.ImplGenerator(model_str=model)

    event_handler = ProjectEventHandler(project_dir, test_gen, impl_gen)
    observer = Observer()
    observer.schedule(event_handler, project_dir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: cli <unique project ID>')
    else:
        main(sys.argv[1])

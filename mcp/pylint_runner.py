import tempfile
import os
from pylint.lint import Run
from io import StringIO
import contextlib

def run_pylint(code: str) -> str:
    """
    Runs pylint on the given Python code string using pylint.lint.Run
    and returns the captured output.

    Args:
        code: The Python code to analyze.

    Returns:
        The combined stdout and stderr from the pylint execution.
    """
    # Create a temporary file to store the code
    # We use delete=False because pylint needs to be able to open the file by path.
    # We will manually delete the file later in the finally block.
    tmp_file_path = None # Initialize to None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
            tmp_file_path = tmp_file.name
            tmp_file.write(code)
            tmp_file.flush() # Ensure the code is written before pylint runs

        # Capture stdout and stderr from pylint.lint.Run
        output_capture = StringIO()
        with contextlib.redirect_stdout(output_capture), contextlib.redirect_stderr(output_capture):
            # Run pylint programmatically
            # exit=False prevents pylint from exiting the current process
            Run([tmp_file_path], exit=False)

        # Get the captured output
        result = output_capture.getvalue()
        return result

    finally:
        # Ensure the temporary file is deleted even if errors occur
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

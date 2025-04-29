import unittest
from mcp.pylint_runner import run_pylint # Absolute import

# Example valid Python code for testing
VALID_PYTHON_CODE = """
def my_function(param1, param2):
    \"\"\"This is a docstring.\"\"\"
    if param1 > param2:
        print(f"{param1} is greater")
    else:
        print(f"{param2} is greater or equal")
    return param1 + param2

MY_VARIABLE = my_function(1, 2)
print(MY_VARIABLE)
"""

class PylintRunnerTests(unittest.TestCase):
    """Tests for the pylint_runner module."""

    def test_run_pylint_simple_code(self):
        """Test running pylint on a simple, valid code snippet."""
        result = run_pylint(VALID_PYTHON_CODE)

        # Assert that we got some string output (pylint likely reports style issues)
        self.assertIsInstance(result, str)
        # Check it's not empty - pylint should output something, even if just ratings
        self.assertGreater(len(result.strip()), 0, "Pylint output should not be empty")

if __name__ == "__main__":
    unittest.main()

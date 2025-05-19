"""
Unit tests for the utility functions in utils.py.
"""
import unittest

from utils import camel_to_snake, guess_classname


class UtilsTest(unittest.TestCase):
    """Tests for utility functions."""

    def test_guess_classname_happy_path(self):
        """Tests classname guessing with a valid class definition."""
        code = "class MyClass(ABC): pass"
        self.assertEqual(guess_classname(code), "MyClass")

    def test_guess_classname_edge_case_no_class(self):
        """Tests classname guessing with no class definition."""
        code = "def my_func(): pass"
        with self.assertRaises(ValueError):
            guess_classname(code)

    def test_guess_classname_edge_case_lowercase(self):
        """Tests classname guessing with a lowercase class name (should fail)."""
        code = "class myclass(ABC): pass"
        with self.assertRaises(ValueError):
            guess_classname(code)

    def test_camel_to_snake_edge_case(self):
        """Tests camel_to_snake with empty string and single uppercase letter."""
        self.assertEqual(camel_to_snake(""), "")
        self.assertEqual(camel_to_snake("A"), "a")

    def test_camel_to_snake_happy_path_multiple_capitals(self):
        """Tests camel_to_snake with a typical multi-word camelCase string."""
        self.assertEqual(camel_to_snake("MyClassIsReallyCool"),
                         "my_class_is_really_cool")

    def test_camel_to_snake_with_acronyms(self):
        """Tests camel_to_snake with strings containing acronyms."""
        self.assertEqual(camel_to_snake("HTTPRequest"), "http_request")
        self.assertEqual(camel_to_snake("CustomerID"), "customer_id")
        self.assertEqual(camel_to_snake("MyID"), "my_id")
        self.assertEqual(camel_to_snake("SimpleXMLParser"), "simple_xml_parser")
        self.assertEqual(camel_to_snake("APIFlagsSet"), "api_flags_set")

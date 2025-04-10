import unittest
from utils import guess_classname, camel_to_snake

class UtilsTest(unittest.TestCase):
    def test_guess_classname_happy_path(self):
        code = "class MyClass(ABC): pass"
        self.assertEqual(guess_classname(code), "MyClass")

    def test_guess_classname_edge_case(self):
        code = "def my_func(): pass"
        with self.assertRaises(ValueError):
            guess_classname(code)
    
    def test_guess_classname_edge_case_lowercase(self):
        code = "class myclass(ABC): pass"
        with self.assertRaises(ValueError):
            guess_classname(code)

    def test_camel_to_snake_edge_case(self):
        self.assertEqual(camel_to_snake(""), "")
        self.assertEqual(camel_to_snake("A"), "a")

    def test_camel_to_snake_happy_path_multiple_capitals(self):
        self.assertEqual(camel_to_snake("MyClassIsReallyCool"), "my_class_is_really_cool")

    def test_camel_to_snake_with_acronyms(self):
        self.assertEqual(camel_to_snake("HTTPRequest"), "http_request")
        self.assertEqual(camel_to_snake("CustomerID"), "customer_id")
        self.assertEqual(camel_to_snake("MyID"), "my_id")
        self.assertEqual(camel_to_snake("SimpleXMLParser"), "simple_xml_parser")
        self.assertEqual(camel_to_snake("APIFlagsSet"), "api_flags_set")

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

    def test_guess_classname_with_extra_whitespace(self):
        code = "class   MyClass  (ABC)  : pass"
        self.assertEqual(guess_classname(code), "MyClass")

    def test_guess_classname_with_multiple_classes(self):
        code = "class FirstClass(ABC): pass\nclass SecondClass(ABC): pass"
        self.assertEqual(guess_classname(code), "FirstClass")

    def test_guess_classname_with_complex_class_definition(self):
        code = "class MyComplexClass(object, metaclass=MyMeta): pass"
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

    def test_camel_to_snake_with_numbers(self):
        self.assertEqual(camel_to_snake("MyClass1"), "my_class1")
        self.assertEqual(camel_to_snake("MyClass123"), "my_class123")
        self.assertEqual(camel_to_snake("Class123Name"), "class123_name")

    def test_camel_to_snake_single_word(self):
        self.assertEqual(camel_to_snake("hello"), "hello")
        self.assertEqual(camel_to_snake("WORLD"), "world")

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
        self.assertEqual(guess_classname(code), "MyComplexClass")

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

    def test_guess_classname_no_parentheses(self):
        code = "class MyClass: pass"
        self.assertEqual(guess_classname(code), "MyClass")

    def test_guess_classname_other_parent(self):
        code = "class MyClass(Base): pass"
        self.assertEqual(guess_classname(code), "MyClass")

    def test_guess_classname_multiple_parents(self):
        code = "class MyClass(Base1, Base2): pass"
        self.assertEqual(guess_classname(code), "MyClass")

    def test_guess_classname_with_comment(self):
        code = "class MyClass(ABC): # This is a class\n    pass"
        self.assertEqual(guess_classname(code), "MyClass")

    def test_guess_classname_after_comments(self):
        code = "# Comment\n\nclass MyClass(ABC): pass"
        self.assertEqual(guess_classname(code), "MyClass")

    def test_camel_to_snake_already_snake(self):
        self.assertEqual(camel_to_snake("already_snake_case"), "already_snake_case")

    def test_camel_to_snake_mixed_case(self):
        self.assertEqual(camel_to_snake("My_Mixed_Case"), "my_mixed_case")

    def test_camel_to_snake_complex_numbers(self):
        self.assertEqual(camel_to_snake("A1B2C3"), "a1_b2_c3")
        self.assertEqual(camel_to_snake("v6Address"), "v6_address")

    def test_guess_classname_with_decorator(self):
        code = "@decorator\nclass MyClass: pass"
        self.assertEqual(guess_classname(code), "MyClass")

    def test_guess_classname_indented(self):
        code = "    class MyClass: pass"
        self.assertEqual(guess_classname(code), "MyClass")

    def test_guess_classname_multiline(self):
        code = "class MyClass(\n    ABC\n): pass"
        self.assertEqual(guess_classname(code), "MyClass")

    def test_camel_to_snake_with_trailing_capitals(self):
        self.assertEqual(camel_to_snake("MyHTTP"), "my_http")

    def test_camel_to_snake_consecutive_capitals(self):
        self.assertEqual(camel_to_snake("JSONParser"), "json_parser")
        self.assertEqual(camel_to_snake("SimpleJSONParser"), "simple_json_parser")

    def test_camel_to_snake_alphanumeric(self):
        self.assertEqual(camel_to_snake("ABC123Def"), "abc123_def")

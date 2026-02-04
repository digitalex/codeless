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

    def test_camel_to_snake_trailing_capital(self):
        self.assertEqual(camel_to_snake("MyClassA"), "my_class_a")

    def test_camel_to_snake_all_caps(self):
        self.assertEqual(camel_to_snake("HTTP"), "http")
        self.assertEqual(camel_to_snake("HTTPServer"), "http_server")

    def test_guess_classname_indented(self):
        code = "    class IndentedClass:\n        pass"
        self.assertEqual(guess_classname(code), "IndentedClass")

    def test_guess_classname_with_multiline_docstring_before(self):
        code = '"""\nThis is a docstring\n"""\nclass MyClass:\n    pass'
        self.assertEqual(guess_classname(code), "MyClass")

    def test_guess_classname_multiline_definition(self):
        # Test that it works with multiline class definitions
        code = "class MyClass(\n    Base\n):\n    pass"
        self.assertEqual(guess_classname(code), "MyClass")

    def test_camel_to_snake_with_middle_acronym(self):
        self.assertEqual(camel_to_snake("APIRequestResponse"), "api_request_response")

    def test_camel_to_snake_with_numbers_and_acronyms(self):
        self.assertEqual(camel_to_snake("HTML5Parser"), "html5_parser")
        self.assertEqual(camel_to_snake("JSON2HTML"), "json2_html")

    def test_camel_to_snake_starting_with_number(self):
        self.assertEqual(camel_to_snake("123ClassName"), "123_class_name")

    def test_camel_to_snake_already_snake_with_numbers(self):
        self.assertEqual(camel_to_snake("already_snake_123"), "already_snake_123")

    def test_camel_to_snake_with_special_characters(self):
        # camel_to_snake doesn't explicitly handle dashes, but let's see what it does
        self.assertEqual(camel_to_snake("StringWith-Dash"), "string_with-dash")

    def test_guess_classname_with_underscore(self):
        code = "class My_Class: pass"
        self.assertEqual(guess_classname(code), "My_Class")

    def test_guess_classname_not_at_start_of_line(self):
        code = "# class NotMe:\nclass Me: pass"
        self.assertEqual(guess_classname(code), "Me")

    def test_guess_classname_commented_out(self):
        code = "# class NotMe: pass"
        with self.assertRaises(ValueError):
            guess_classname(code)

import unittest
from main import *


class TestConfigParser(unittest.TestCase):

    def test_basic_constant_parsing(self):
        input_text = """
        const a = 10
        const b = 20
        const c = $a + $b
        """
        expected_output = {
            'a': 10,
            'b': 20,
            'c': 30
        }
        result = parse_input(input_text)
        self.assertEqual(result, expected_output)

    def test_min_function(self):
        input_text = """
        const max_connections = 15
        const min_connections = min(5, $max_connections$)
        """
        expected_output = {
            'max_connections': 15,
            'min_connections': 5
        }
        result = parse_input(input_text)
        self.assertEqual(result, expected_output)

    def test_string_parsing(self):
        input_text = """
        greeting = [[Hello, World!]]
        """
        expected_output = {
            'greeting': 'Hello, World!'
        }
        result = parse_input(input_text)
        self.assertEqual(result, expected_output)

    def test_combined_expressions(self):
        input_text = """
        const a = 3
        const b = 4
        const total = $a + $b + 2
        """
        expected_output = {
            'a': 3,
            'b': 4,
            'total': 9
        }
        result = parse_input(input_text)
        self.assertEqual(result, expected_output)

    def test_invalid_syntax(self):
        input_text = """
        const valid = 10
        invalid syntax
        """
        with self.assertRaises(ValueError) as context:
            parse_input(input_text)
        self.assertTrue('Неверный синтаксис строки' in str(context.exception))

    def test_empty_input(self):
        input_text = ""
        expected_output = {}
        result = parse_input(input_text)
        self.assertEqual(result, expected_output)

    def test_comment_removal(self):
        input_text = """
        (comment
        This is a comment
        )
        const a = 5
        """
        expected_output = {
            'a': 5
        }
        result = parse_input(input_text)
        self.assertEqual(result, expected_output)

    def test_evaluation_error(self):
        input_text = """
        const a = 5
        const b = $a + invalid_variable
        """
        with self.assertRaises(ValueError) as context:
            parse_input(input_text)
        self.assertTrue('Ошибка при вычислении выражения' in str(context.exception))

    def test_multiple_lines(self):
        input_text = """
        const width = 10
        const height = 5
        const area = $width * $height
        """
        expected_output = {
            'width': 10,
            'height': 5,
            'area': 50
        }
        result = parse_input(input_text)
        self.assertEqual(result, expected_output)


if __name__ == '__main__':
    unittest.main()

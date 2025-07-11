from jambo.parser import ConstTypeParser

from typing import Annotated, Literal, get_args, get_origin

from unittest import TestCase


class TestConstTypeParser(TestCase):
    def test_const_type_parser_hashable_value(self):
        parser = ConstTypeParser()

        expected_const_value = "United States of America"
        properties = {"const": expected_const_value}

        parsed_type, parsed_properties = parser.from_properties_impl(
            "country", properties
        )

        self.assertEqual(get_origin(parsed_type), Literal)
        self.assertEqual(get_args(parsed_type), (expected_const_value,))

        self.assertEqual(parsed_properties["default"], expected_const_value)

    def test_const_type_parser_non_hashable_value(self):
        parser = ConstTypeParser()

        expected_const_value = [1, 2, 3]
        properties = {"const": expected_const_value}

        parsed_type, parsed_properties = parser.from_properties_impl(
            "list_const", properties
        )

        self.assertEqual(get_origin(parsed_type), Annotated)
        self.assertIn(list, get_args(parsed_type))

        self.assertEqual(parsed_properties["default"], expected_const_value)

    def test_const_type_parser_integer_value(self):
        parser = ConstTypeParser()

        expected_const_value = 42
        properties = {"const": expected_const_value}

        parsed_type, parsed_properties = parser.from_properties_impl(
            "int_const", properties
        )

        self.assertEqual(get_origin(parsed_type), Literal)
        self.assertEqual(get_args(parsed_type), (expected_const_value,))

        self.assertEqual(parsed_properties["default"], expected_const_value)

    def test_const_type_parser_boolean_value(self):
        parser = ConstTypeParser()

        expected_const_value = True
        properties = {"const": expected_const_value}

        parsed_type, parsed_properties = parser.from_properties_impl(
            "bool_const", properties
        )

        self.assertEqual(get_origin(parsed_type), Literal)
        self.assertEqual(get_args(parsed_type), (expected_const_value,))

        self.assertEqual(parsed_properties["default"], expected_const_value)

    def test_const_type_parser_invalid_properties(self):
        parser = ConstTypeParser()

        expected_const_value = "United States of America"
        properties = {"notConst": expected_const_value}

        with self.assertRaises(ValueError) as context:
            parser.from_properties_impl("invalid_country", properties)

        self.assertIn(
            "Const type invalid_country must have 'const' property defined",
            str(context.exception),
        )

    def test_const_type_parser_invalid_const_value(self):
        parser = ConstTypeParser()

        properties = {"const": {}}

        with self.assertRaises(ValueError) as context:
            parser.from_properties_impl("invalid_country", properties)

        self.assertIn(
            "Const type invalid_country must have 'const' value of allowed types",
            str(context.exception),
        )

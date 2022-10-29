import base64
import unittest

from ..helpers import convert_to_base64_form, convert_camel_case_to_snake_case


class TestHelpers(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_convert_to_base64_form(self) -> None:
        test_values = ('abc', '123', '9238!!++-000@@##$$')
        for value in test_values:
            with self.subTest(f'testing for value:{value}'):
                self.assertEqual(base64.b64encode(value.encode('ascii')).decode('ascii'), convert_to_base64_form(value))

    def test_convert_camel_case_to_snake_case(self) -> None:
        test_values = (('ABC', 'a_b_c'), ('TestCase', 'test_case'), ('TestExample', 'test_example'))
        for value, expected_value in test_values:
            with self.subTest(f'testing for value:{value}'):
                self.assertEqual(expected_value, convert_camel_case_to_snake_case(value))

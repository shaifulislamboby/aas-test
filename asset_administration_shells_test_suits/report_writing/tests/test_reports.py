import unittest
from unittest.mock import patch

from asset_administration_shells_test_suits.base_classes.base_test import TestResult
from asset_administration_shells_test_suits.report_writing.report import (
    write_test_results_to_file,
    write_non_implemented_test_results_to_file,
)


class TestReports(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.test_result = TestResult()
        self.test_result_passed = TestResult(passed=True)
        self.base_preparation = patch(
            "asset_administration_shells_test_suits.base_classes.preparation.BaseAASPreparation"
        ).start()
        self.base_preparation.substituted_url = "test"

    def test_write_test_results_to_file(self) -> None:
        # given
        l_length = []
        with open("abc.txt", "w") as file:
            test_values = (("abc", "get", file, 145), ("bcd", "post", file, 146))
            for uri, operation, f, length in test_values:
                for test_result in (
                    self.test_result,
                    "not implemented",
                    111,
                    self.test_result_passed,
                ):
                    with self.subTest(f"testing for value:{uri, operation, f}"):
                        r = write_test_results_to_file(
                            test_result, uri, operation, self.base_preparation, f
                        )
                        l_length.append(r)
        self.assertListEqual([145, 113, 65, 65, 146, 114, 66, 66], l_length)

    def test_write_non_implemented_test_results_to_file(self) -> None:
        with open("abc.txt", "w") as file_one:
            test_values = (
                ("abc", "get", file_one, 130),
                ("bcd", "post", file_one, 133),
            )
            for uri, operation, f, length in test_values:
                for test_result in (
                    self.test_result,
                    "not implemented",
                    111,
                    self.test_result_passed,
                ):
                    with self.subTest(f"testing for value:{uri, operation, f}"):
                        r = write_non_implemented_test_results_to_file(
                            test_result, operation, self.base_preparation, "error", f
                        )
                        self.assertGreater(
                            r,
                            length,
                            "this written message is greater then the normal message",
                        )

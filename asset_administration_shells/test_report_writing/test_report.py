from typing import Optional

from asset_administration_shells.base_classes.test import TestResult, BaseTest
from asset_administration_shells.base_classes.preparation import BaseAASPreparation


def write_test_results_to_file(
        test_result: Optional[TestResult], path: str, operation: str, test: BaseAASPreparation, file
) -> int:
    if not isinstance(test_result, str) and not test_result.passed:
        length_of_dash_sign = len(
            f'|| Test fails ---> || {path, operation}, substituted-url ='
            f' {test.substituted_url}, error is {test_result} ||\n'
        )
        file.write(
            f'|| Test fails ---> || {path, operation}, substituted-url ='
            f' {test.substituted_url}, error is {test_result} ||\n'
        )
    elif test_result == BaseTest.error_message or (not isinstance(test_result, TestResult) and
                                                   'no matching' in test_result):
        length_of_dash_sign = len(
            f'|| This endpoint is not implemented  ---> || {path, operation}, substituted-url ='
            f' {test.substituted_url}, error is {test_result} ||\n'
        )
        file.write(
            f'|| This endpoint is not implemented  ---> || {path, operation}, substituted-url ='
            f' {test.substituted_url}, error is {test_result}  ||\n'
        )
    else:
        length_of_dash_sign = len(
            f'|| Test passed ---> || {path, operation}, substituted-url = {test.substituted_url} ||\n'
        )
        file.write(
            f'|| Test passed ---> || {path, operation}, substituted-url = {test.substituted_url} ||\n'
        )
    return length_of_dash_sign


def write_non_implemented_test_results_to_file(path, operation, test, error, file) -> int:
    length_of_dash_sign = len(f'|| Test returned non parable response or this endpoint is'
                              f' not implemented --->'
                              f' {path, operation}, substituted-url ='
                              f' {test.substituted_url}, error is {error}||\n')
    file.write(f'|| Test returned non parsable response or this endpoint is'
               f' not implemented --->'
               f' {path, operation}, substituted-url ='
               f' {test.substituted_url}, error is {error} ||\n')

    return length_of_dash_sign

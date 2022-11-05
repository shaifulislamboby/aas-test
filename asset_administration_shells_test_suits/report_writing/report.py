from asset_administration_shells_test_suits.base_classes.preparation import (
    Preparation
)
from asset_administration_shells_test_suits.helpers.helpers import aas_logger


@aas_logger
def write_test_results_to_file(
        test_result, uri: str, operation: str, prepared_instance: Preparation, file,
        count
) -> int:
    from asset_administration_shells_test_suits.runner.runner import TestRunner, NOT_IMPLEMENTATION_MSG
    if test_result.message in TestRunner.error_message or NOT_IMPLEMENTATION_MSG in test_result.message:
        length_of_dash_sign = len(
            f'|| This endpoint is not implemented  ---> || {uri, operation}, substituted-url ='
            f' {prepared_instance.substituted_url}, error is {test_result} ||\n'
        )
        file.write(
            f'|| This endpoint is not implemented  ---> || {uri, operation}, substituted-url ='
            f' {prepared_instance.substituted_url}, error is {test_result}  ||\n'
        )
        if isinstance(count, dict):
            count['non_implemented'].append(1)
    elif not test_result.passed:
        length_of_dash_sign = len(
            f'|| Test fails ---> || {uri, operation}, substituted-url ='
            f' {prepared_instance.substituted_url}, error is {test_result} ||\n'
        )
        file.write(
            f'|| Test fails ---> || {uri, operation}, substituted-url ='
            f' {prepared_instance.substituted_url}, error is {test_result} ||\n'
        )
        if isinstance(count, dict):
            count['failed'].append(1)
    else:
        length_of_dash_sign = len(
            f'|| Test passed ---> || {uri, operation}, substituted-url = {prepared_instance.substituted_url} ||\n'
        )
        file.write(
            f'|| Test passed ---> || {uri, operation}, substituted-url = {prepared_instance.substituted_url} ||\n'
        )
        if isinstance(count, dict):
            count['passed'].append(1)
    return length_of_dash_sign


@aas_logger
def write_non_implemented_test_results_to_file(uri, http_verb, test, error, file) -> int:
    length_of_dash_sign = len(f'|| Test returned non parable response or this endpoint is'
                              f' not implemented --->'
                              f' {uri, http_verb}, substituted-url ='
                              f' {test.substituted_url}, error is {error}||\n')
    file.write(f'|| Test returned non parsable response or this endpoint is'
               f' not implemented --->'
               f' {uri, http_verb}, substituted-url ='
               f' {test.substituted_url}, error is {error} ||\n')

    return length_of_dash_sign

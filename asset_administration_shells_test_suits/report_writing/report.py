from asset_administration_shells_test_suits.base_classes.executor import Executor
from asset_administration_shells_test_suits.helpers.helpers import aas_logger


@aas_logger
def write_test_results_to_file(
    test_result,
    uri: str,
    operation: str,
    executed_instance: Executor,
    file_name,
    count,
):
    from asset_administration_shells_test_suits.runner.runner import (
        TestRunner,
        NOT_IMPLEMENTATION_MSG,
    )

    with open(file_name, "a") as file:
        if (
            test_result.message in TestRunner.error_message
            or NOT_IMPLEMENTATION_MSG in test_result.message
        ):
            length_of_dash_sign = len(
                f"|| This endpoint is not implemented  ---> || {uri, operation}, substituted-url ="
                f" {executed_instance.substituted_url}, error is {test_result} ||\n"
            )
            file.write(
                f"|| This endpoint is not implemented  ---> || {uri, operation}, substituted-url ="
                f" {executed_instance.substituted_url}, error is {test_result}  ||\n"
            )
            if isinstance(count, dict):
                count["non_implemented"].append(1)
        elif not test_result.passed:
            length_of_dash_sign = len(
                f"|| Test fails ---> || {uri, operation}, substituted-url ="
                f" {executed_instance.substituted_url}, error is {test_result} ||\n"
            )
            file.write(
                f"|| Test fails ---> || {uri, operation}, substituted-url ="
                f" {executed_instance.substituted_url}, error is {test_result} ||\n"
            )
            if isinstance(count, dict):
                count["failed"].append(1)
        else:
            length_of_dash_sign = len(
                f"|| Test passed ---> || {uri, operation}, substituted-url = {executed_instance.substituted_url} ||\n"
            )
            file.write(
                f"|| Test passed ---> || {uri, operation}, substituted-url = {executed_instance.substituted_url} ||\n"
            )
            if isinstance(count, dict):
                count["passed"].append(1)
        file.write("-" * length_of_dash_sign + "\n")


def write_test_metrics(file, test_count: int, counts_dict: dict) -> None:
    with open(file, "a") as file:
        file.write(
            "Test run finished for this endpoint: " + "\n"
            f'Test passed till now : {len(counts_dict["passed"])} \n'
            f'Test failed till now : {len(counts_dict["failed"])} \n'
            f'Non implemented endpoints till now : {len(counts_dict["non_implemented"])} \n'
            "Number of total test done till now: " + str(test_count) + "\n"
        )

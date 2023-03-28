import logging
from positive_tests.endpoints_preparation.positive_test import PositiveTestExecutor
from runner.runner import TestRunner
from parsers.schema_parser import AasSchemaParser

if __name__ == "__main__":
    logging.basicConfig(
        filename="log_files/central_log.log", filemode="w", level=logging.INFO
    )
    file_location = "aas_openapi_specifications/open_api_specification_aas_v2.json"
    output_file_name = "test_reports/test_report_FAAAST_RESTA_API_server.txt"
    base_url = "http://fast-service:8080"
    aas = AasSchemaParser(file_location=file_location)
    TestRunner(
        aas_schema=aas,
        output_file_name=output_file_name,
        base_url=base_url,
        aas_path=f"{base_url}/shells/",
        concept_description_path=f"{base_url}/concept-descriptions/",
        sub_model_path=f"{base_url}/submodels/{{submodelIdentifier}}",
        _id=None,
        password=None,
        executor_class=PositiveTestExecutor,
    ).start_test()

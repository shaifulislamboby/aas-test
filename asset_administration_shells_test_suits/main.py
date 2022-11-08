import logging

from asset_administration_shells_test_suits.negative_tests.third.endpoints_preparation.negative_test_three import (
    PreparePPDNegativeThree,
)
from negative_tests.first_test.endpoints_preparation.negative_test_one import (
    PreparePPDNegative,
)
from negative_tests.second_test.endpoints_preparation.negative_test_two import (
    PreparePPDNegativeTwo,
)
from positive_tests.endpoints_preparation.positive_test import PreparePPDPositive
from runner.runner import TestRunner
from parsers.schema_parser import AasSchemaParser

if __name__ == "__main__":
    logging.basicConfig(
        filename="log_files/central_log.log", filemode="w", level=logging.INFO
    )
    file_location = "aas_openapi_specifications/open_api_specification_aas_v2.json"
    output_file_name = "test_reports/Test Report_fAAAST.txt"
    output_file_name_negative_first = (
        "test_reports/Test Report_fAAAST_negative_first.txt"
    )
    output_file_name_negative_second = (
        "test_reports/Test Report_fAAAST_negative_second.txt"
    )
    output_file_name_negative_third = (
        "test_reports/Test Report_fAAAST_negative_third.txt"
    )
    base_url = "http://localhost:8080"
    # base_url = 'http://192.168.0.2:60008'
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
        preparation_class=PreparePPDPositive,
    ).start_test()
    # TestRunner(
    #     aas_schema=aas,
    #     output_file_name=output_file_name_negative_first,
    #     base_url=base_url,
    #     aas_path=f'{base_url}/shells/',
    #     concept_description_path=f'{base_url}/concept-descriptions/',
    #     sub_model_path=f'{base_url}/submodels/{{submodelIdentifier}}',
    #     _id='OVGUAdmin',
    #     password='liaadmin',
    #     preparation_class=PreparePPDNegative
    # ).start_test(positive=False)
    # TestRunner(
    #     aas_schema=aas,
    #     output_file_name=output_file_name_negative_second,
    #     base_url=base_url,
    #     aas_path=f'{base_url}/shells/',
    #     concept_description_path=f'{base_url}/concept-descriptions/',
    #     sub_model_path=f'{base_url}/submodels/{{submodelIdentifier}}',
    #     _id=None,
    #     password=None,
    #     preparation_class=PreparePPDNegativeTwo
    # ).start_test()
    # TestRunner(
    #     aas_schema=aas,
    #     output_file_name=output_file_name_negative_third,
    #     base_url=base_url,
    #     aas_path=f'{base_url}/shells/',
    #     concept_description_path=f'{base_url}/concept-descriptions/',
    #     sub_model_path=f'{base_url}/submodels/{{submodelIdentifier}}',
    #     _id=None,
    #     password=None,
    #     preparation_class=PreparePPDNegativeThree
    # ).start_test()

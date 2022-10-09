from asset_administration_shells_test_suits.negative_tests.first_test.endpoints_preparation.negative_test_one import (
    PreparePPDNegative
)
from asset_administration_shells_test_suits.negative_tests.second_test.endpoints_preparation.negative_test_two import (
    PreparePPDNegativeTwo
)
from asset_administration_shells_test_suits.positive_tests.endpoints_preparation.positive_test import (
    PreparePPDPositive
)
from asset_administration_shells_test_suits.runner.test_runner import TestRunner
from asset_administration_shells_test_suits.parsers.schema_parser import AasSchemaParser

if __name__ == '__main__':
    file_location = 'aas_openapi_specifications/open_api_specification_aas_v2.json'
    output_file_name = 'test_reports/Test Report_fAAAST.txt'
    output_file_name_negative_first = 'test_reports/Test Report_fAAAST_negative_first.txt'
    output_file_name_negative_second = 'test_reports/Test Report_fAAAST_negative_second.txt'
    base_url = 'http://localhost:8080'
    Aas = AasSchemaParser(file_location=file_location)
    TestRunner(aas_schema=Aas,
               output_file_name=output_file_name,
               base_url=base_url,
               aas_path=f'{base_url}/shells/',
               concept_description_path=f'{base_url}/concept-descriptions/',
               sub_model_path=f'{base_url}/submodels/{{submodelIdentifier}}',
               _id=None, password=None,
               preparation_class=PreparePPDPositive).start_test()
    TestRunner(aas_schema=Aas,
               output_file_name=output_file_name_negative_first,
               base_url=base_url,
               aas_path=f'{base_url}/shells/',
               concept_description_path=f'{base_url}/concept-descriptions/',
               sub_model_path=f'{base_url}/submodels/{{submodelIdentifier}}',
               _id=None, password=None,
               preparation_class=PreparePPDNegative).start_test(positive=False)
    TestRunner(aas_schema=Aas,
               output_file_name=output_file_name_negative_second,
               base_url=base_url,
               aas_path=f'{base_url}/shells/',
               concept_description_path=f'{base_url}/concept-descriptions/',
               sub_model_path=f'{base_url}/submodels/{{submodelIdentifier}}',
               _id=None, password=None,
               preparation_class=PreparePPDNegativeTwo).start_test(positive=False)

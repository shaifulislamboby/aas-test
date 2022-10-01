from asset_administration_shells.negative_tests.first_test.endpoints_preparation \
    .prepare_endpoints_for_first_negative_test import (
    PrepareAASGETPOSTPUTEndPointForFirstNegativeTest
)
from asset_administration_shells.negative_tests.first_test.negative_test_runner_with_empty_request_body import (
    NegativeTestRunner
)
from asset_administration_shells.negative_tests.second_test.endpoints_preparation.prepare_endpoints_for_second_negative_test import \
    PrepareAASGETPOSTPUTEndPointForSecondNegativeTest
from asset_administration_shells.positive_tests.endpoints_preparation.prepare_endpoints_for_positive_test import (
    PrepareAASGETPOSTPUTEndPointForPositiveTest
)
from asset_administration_shells.positive_tests.positive_test_runner import PositiveTestRunner
from asset_administration_shells.parsers.schema_parser import AasSchemaParser

if __name__ == '__main__':
    file_location = 'aas_openapi_specifications/open_api_specification_aas_v2.json'
    output_file_name = 'test_reports/Test Report_fAAAST.txt'
    output_file_name_negative_first = 'test_reports/Test Report_fAAAST_negative_first.txt'
    output_file_name_negative_second = 'test_reports/Test Report_fAAAST_negative_second.txt'
    base_url = 'http://localhost:8080'
    Aas = AasSchemaParser(file_location=file_location)
    PositiveTestRunner(aas_schema=Aas,
                       output_file_name=output_file_name,
                       base_url=base_url,
                       aas_path=f'{base_url}/shells/',
                       concept_description_path=f'{base_url}/concept-descriptions/',
                       sub_model_path=f'{base_url}/submodels/{{submodelIdentifier}}',
                       _id=None, password=None,
                       preparation_class=PrepareAASGETPOSTPUTEndPointForPositiveTest).start_test()
    NegativeTestRunner(aas_schema=Aas,
                       output_file_name=output_file_name_negative_first,
                       base_url=base_url,
                       aas_path=f'{base_url}/shells/',
                       concept_description_path=f'{base_url}/concept-descriptions/',
                       sub_model_path=f'{base_url}/submodels/{{submodelIdentifier}}',
                       _id=None, password=None,
                       preparation_class=PrepareAASGETPOSTPUTEndPointForFirstNegativeTest).start_test()
    NegativeTestRunner(aas_schema=Aas,
                       output_file_name=output_file_name_negative_second,
                       base_url=base_url,
                       aas_path=f'{base_url}/shells/',
                       concept_description_path=f'{base_url}/concept-descriptions/',
                       sub_model_path=f'{base_url}/submodels/{{submodelIdentifier}}',
                       _id=None, password=None,
                       preparation_class=PrepareAASGETPOSTPUTEndPointForSecondNegativeTest).start_test()

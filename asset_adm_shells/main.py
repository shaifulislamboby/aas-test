from asset_adm_shells.aas_negative_test import NegativeTestRunner
from asset_adm_shells.aas_positive_test import PositiveTestRunner
from aas_schema_parser import AasSchemaParser

if __name__ == '__main__':
    file_location = 'open_api_specification_aas_v2.json'
    output_file_name = 'Test Report_fAAAST.txt'
    output_file_name_negative = 'Test Report_fAAAST_negative.txt'
    base_url = 'http://localhost:8080'
    Aas = AasSchemaParser(file_location=file_location)
    PositiveTestRunner(aas_schema=Aas, output_file_name=output_file_name, base_url=base_url,
                       aas_path=f'{base_url}/shells/',
                       concept_description_path=f'{base_url}/concept-descriptions/',
                       sub_model_path=f'{base_url}/submodels/{{submodelIdentifier}}',
                       _id=None, password=None).start_test()
    NegativeTestRunner(aas_schema=Aas, output_file_name=output_file_name_negative, base_url=base_url,
                       aas_path=f'{base_url}/shells/',
                       concept_description_path=f'{base_url}/concept-descriptions/',
                       sub_model_path=f'{base_url}/submodels/{{submodelIdentifier}}',
                       _id=None, password=None).start_test()

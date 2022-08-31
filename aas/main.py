from aas_schema_parser import AasSchemaParser
from base_test import BaseTest

if __name__ == '__main__':
    file_location = 'aas/open_api_specification_aas_v2.json'
    output_file_name = 'Test Report.txt'
    base_url = 'http://localhost:8080'
    Aas = AasSchemaParser(file_location=file_location)
    BaseTest(aas_schema=Aas, output_file_name=output_file_name, base_url=base_url, aas_path=f'{base_url}/shells/',
             concept_description_path=f'{base_url}/concept-descriptions/',
             sub_model_path=f'{base_url}/submodels/{{submodelIdentifier}}',
             _id=None, password=None).start_test()

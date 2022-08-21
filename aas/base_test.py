from dataclasses import dataclass

import requests

from aas_identifiers_parser import AssetAdministrationShell, ConceptDescription
from aas_schema_parser import AasSchemaParser
from shells_endpoints import AasGETPOSTPUTEndPoint


@dataclass
class BaseTest:
    aas_schema: AasSchemaParser
    output_file_name: str
    base_url: str
    aas_path: str
    sub_model_path: str
    concept_description_path: str
    error_message = "no matching request mapper found for URL"

    @staticmethod
    def check_get_response_conforms(response):
        if response.status_code != 200:
            if BaseTest.error_message in response.json().get('messages')[0]['text']:
                return BaseTest.error_message
            return 'fail'

    @staticmethod
    def check_post_response_conforms(response):
        if response.status_code != 201:
            if BaseTest.error_message in response.json().get('messages')[0]['text']:
                return BaseTest.error_message
            return 'fail'

    @staticmethod
    def check_put_response_conforms(response):
        if response.status_code not in (200, 204):
            if BaseTest.error_message in response.json().get('messages')[0]['text']:
                return BaseTest.error_message
            return 'fail'

    @staticmethod
    def check_delete_response_conforms(response):
        if response.status_code != 204:
            if BaseTest.error_message in response.json().get('messages')[0]['text']:
                return BaseTest.error_message
            return 'fail'

    def start_test(self):
        for path in self.aas_schema.paths:
            # if path.startswith('/shells'):
            test = AasGETPOSTPUTEndPoint(raw_endpoint=self.aas_schema.paths.get(path),
                                         base_url=self.base_url,
                                         full_url_path=path,
                                         asset_administration_shells=self.get_asset_administration_shells(),
                                         concept_description=self.get_concept_description(),
                                         packages=None)
            test.set_all_required_attributes()
            with open(self.output_file_name, 'a') as file:
                for value in test.operations:
                    if value != 'delete':
                        try:
                            func = getattr(self, f'check_{value}_response_conforms')
                            response = getattr(test, f'{value}_response')
                            if func(response) == 'fail':
                                file.write(f'test fails ---> {path, value}\n')
                            elif func(response) == BaseTest.error_message:
                                file.write(f'This endpoint is not implemented  ---> {path, value}\n')
                            else:
                                file.write(f'test passed ---> {path, value}\n')
                        except Exception as error:
                            file.write(f'test failed ---> {path, value}\n')

    def get_asset_administration_shells(self):
        response = requests.get(url=self.aas_path).json()
        initial_list = []
        for res in response:
            initial_list.append(AssetAdministrationShell(res, sub_model_collection_uri=self.sub_model_path))
        return initial_list

    def get_concept_description(self):
        return ConceptDescription(raw_concept_description=requests.get(url=self.concept_description_path).json()[0])

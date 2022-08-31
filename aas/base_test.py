from dataclasses import dataclass, field
from typing import Union

import requests

from aas_identifiers_parser import AssetAdministrationShell, ConceptDescription
from aas_schema_parser import AasSchemaParser
from shells_endpoints import AasGETPOSTPUTEndPoint


@dataclass
class TestResult:
    passed: bool = False
    failed: bool = False


@dataclass
class DeleteEndpoint:
    substituted_url: str
    path: str
    operation: str = 'delete'


@dataclass
class BaseTest:
    aas_schema: AasSchemaParser
    _id: Union[str, None]
    password: Union[str, None]
    output_file_name: str
    base_url: str
    aas_path: str
    sub_model_path: str
    concept_description_path: str
    error_message = "no matching request mapper found for URL"
    delete_urls: [DeleteEndpoint] = field(default_factory=lambda: [])

    @property
    def session(self):
        if self.password and self._id:
            session = requests.Session()
            session.auth = (self._id, self.password)
            return session
        return False

    @staticmethod
    def check_get_response_conforms(response):
        if response.status_code != 200:
            if BaseTest.error_message in response.json().get('messages')[0]['text']:
                return BaseTest.error_message
            return TestResult(failed=True)

    @staticmethod
    def check_post_response_conforms(response):
        if response.status_code != 201:
            if BaseTest.error_message in response.json().get('messages')[0]['text']:
                return BaseTest.error_message
            return TestResult(failed=True)

    @staticmethod
    def check_put_response_conforms(response):
        if response.status_code not in (200, 204):
            if BaseTest.error_message in response.json().get('messages')[0]['text']:
                return BaseTest.error_message
            return TestResult(failed=True)

    @staticmethod
    def check_delete_response_conforms(response):
        if response.status_code != 204:
            if BaseTest.error_message in response.json().get('messages')[0]['text']:
                return BaseTest.error_message
            return TestResult(failed=True)

    def start_test(self):
        for path in self.aas_schema.paths:
            test = AasGETPOSTPUTEndPoint(raw_endpoint=self.aas_schema.paths.get(path),
                                         base_url=self.base_url,
                                         full_url_path=path,
                                         asset_administration_shells=self.get_asset_administration_shells(),
                                         concept_description=self.get_concept_description(),
                                         packages=None,
                                         _id=self._id,
                                         password=self.password)
            test.set_all_required_attributes()
            with open(self.output_file_name, 'a') as file:
                for operation in test.operations:
                    if operation != 'delete':
                        try:
                            func = getattr(self, f'check_{operation}_response_conforms')
                            response = getattr(test, f'{operation}_response')
                            if isinstance(func(response), TestResult) and func(response):
                                length_of_equal_sign = len(f'|| Test fails ---> || {path, operation}, substituted-url ='
                                                           f' {test.substituted_url} ||\n')
                                file.write(f'|| Test fails ---> || {path, operation}, substituted-url ='
                                           f' {test.substituted_url} ||\n')
                            elif func(response) == BaseTest.error_message:
                                length_of_equal_sign = len(f'|| This endpoint is not implemented  ---> || '
                                                           f'{path, operation}, substituted-url ='
                                                           f' {test.substituted_url} ||\n')
                                file.write(
                                    f'|| This endpoint is not implemented  ---> || {path, operation}, substituted-url ='
                                    f' {test.substituted_url} ||\n')
                            else:
                                length_of_equal_sign = len(
                                    f'|| Test passed ---> || {path, operation}, substituted-url ='
                                    f' {test.substituted_url} ||\n')
                                file.write(f'|| Test passed ---> || {path, operation}, substituted-url ='
                                           f' {test.substituted_url} ||\n')
                        except Exception as error:
                            print(error)
                            length_of_equal_sign = len(f'|| Test returned non parable response or this endpoint is'
                                                       f' not implemented --->'
                                                       f' {path, operation}, substituted-url ='
                                                       f' {test.substituted_url} ||\n')
                            file.write(f'|| Test returned non parsable response or this endpoint is'
                                       f' not implemented --->'
                                       f' {path, operation} ||\n')
                        file.write('-' * length_of_equal_sign + '\n')
                    elif operation == 'delete' and len(test.operations) > 1:
                        self.delete_urls.append(DeleteEndpoint(substituted_url=test.substituted_url, path=path))
        with open(self.output_file_name, 'a') as file:
            self.test_delete_endpoints(file)

    def get_asset_administration_shells(self):
        if self.session:
            response = self.session.get(url=self.aas_path).json()
        else:
            response = requests.get(url=self.aas_path).json()
        initial_list = []
        for res in response:
            initial_list.append(AssetAdministrationShell(raw_asset_administration_shell=res,
                                                         sub_model_collection_uri=self.sub_model_path,
                                                         _id=self._id,
                                                         password=self.password))
        return initial_list

    def get_concept_description(self):
        return ConceptDescription(raw_concept_description=requests.get(url=self.concept_description_path).json()[0],
                                  _id=self._id,
                                  password=self.password)

    def test_delete_endpoints(self, file):
        for url in self.delete_urls:
            if not self.session:
                delete_response = requests.delete(url=f'{self.base_url}{url.substituted_url}')
            else:
                delete_response = self.session.delete(url=f'{self.base_url}{url.substituted_url}')
            func = self.check_delete_response_conforms
            try:
                if isinstance(func(delete_response), TestResult) and func(delete_response):
                    length_of_equal_sign = len(f'|| Test fails ---> || {url.path, url.operation}, substituted-url ='
                                               f' {url.substituted_url} ||\n')
                    file.write(f'|| Test fails ---> || {url.path, url.operation}, substituted-url ='
                               f' {url.substituted_url} ||\n')
                elif func(delete_response) == BaseTest.error_message:
                    length_of_equal_sign = len(f'|| This endpoint is not implemented  ---> || '
                                               f'{url.path, url.operation}, substituted-url ='
                                               f' {url.substituted_url} ||\n')
                    file.write(
                        f'|| This endpoint is not implemented  ---> || {url.path, url.operation}, substituted-url ='
                        f' {url.substituted_url} ||\n')
                else:
                    length_of_equal_sign = len(f'|| Test passed ---> || {url.path, url.operation}, substituted-url ='
                                               f' {url.substituted_url} ||\n')
                    file.write(f'|| Test passed ---> || {url.path, url.operation}, substituted-url ='
                               f' {url.substituted_url} ||\n')
            except Exception as error:
                print(error)
                length_of_equal_sign = len(f'|| Test returned non parable response or this endpoint is'
                                           f' not implemented --->'
                                           f' {url.path, url.operation}, substituted-url ='
                                           f' {url.substituted_url} ||\n')
                file.write(f'|| Test returned non parsable response or this endpoint is'
                           f' not implemented --->'
                           f' {url.path, url.operation} ||\n')
            file.write('-' * length_of_equal_sign + '\n')

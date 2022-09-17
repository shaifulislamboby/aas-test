from dataclasses import dataclass, field
from typing import Union

import jsonschema
import requests

from aas_schema_parser import AasSchemaParser
from asset_adm_shells.aas_identifiers_parser import AssetAdministrationShell, ConceptDescription


@dataclass
class TestResult:
    passed: bool = False
    status_code: bool = False
    schema_conformation: bool = False


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
    error_message = ('no matching request mapper found for URL', 'not allowed for', 'currently not supported',
                     'no handler defined')
    delete_urls: [DeleteEndpoint] = field(default_factory=lambda: [])

    @property
    def session(self):
        if self.password and self._id:
            session = requests.Session()
            session.auth = (self._id, self.password)
            return session
        return False

    def check_get_response_conforms(self, response):
        if response.status_code != 200:
            if any(error_m in response.json().get('messages')[0]['text'] for error_m in self.error_message):
                return BaseTest.error_message[0]
            return TestResult()
        try:
            # we will validate the json schema in case of json response, non-conforming
            # json response will raise an exception
            jsonschema.validate(response.json(), schema=self.aas_schema.raw_schema)
            return TestResult(passed=True, schema_conformation=True, status_code=True)
        except Exception as error:
            print(error)
            return TestResult(passed=True, schema_conformation=False, status_code=True)

    @staticmethod
    def check_post_response_conforms(response):
        if response.status_code != 201:
            if any(error_m in response.json().get('messages')[0]['text'] for error_m in BaseTest.error_message):
                return BaseTest.error_message[0]
            return TestResult()
        return TestResult(passed=True)

    @staticmethod
    def check_put_response_conforms(response):
        if response.status_code not in (200, 204):
            if any(error_m in response.json().get('messages')[0]['text'] for error_m in BaseTest.error_message):
                return BaseTest.error_message[0]
            return TestResult()
        return TestResult(passed=True)

    @staticmethod
    def check_delete_response_conforms(response):
        if response.status_code != 204:
            if any(error_m in response.json().get('messages')[0]['text'] for error_m in BaseTest.error_message):
                return BaseTest.error_message[0]
            return TestResult()
        return TestResult(passed=True)

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
        try:
            return ConceptDescription(raw_concept_description=requests.get(url=self.concept_description_path).json()[0],
                                      _id=self._id,
                                      password=self.password)
        except Exception as error:
            print(error)
            return 0

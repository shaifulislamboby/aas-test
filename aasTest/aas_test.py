import base64
import json
from dataclasses import dataclass
from typing import Optional

import jsonschema
import requests
from urllib import parse


SCHEMA_PATH = None
BASE_URL = None


def convert_to_base64_form(submodelIdentifier: str) -> base64:
    _bytes = submodelIdentifier.encode('ascii')
    base64_bytes = base64.b64encode(_bytes)
    return base64_bytes.decode('ascii')


def create_url_encoded_from_id(idShortPath: str) -> str:
    return parse.quote(idShortPath)


@dataclass
class AASEndPoints:
    raw_endpoint: dict
    base_url: str
    full_url_path: str
    operations: list = None
    path_params: list = None
    full_get_response: list = None
    single_get_response: dict = None
    get_response: dict = None
    post_data: dict = None
    post_response: dict = None
    put_response: dict = None
    delete_response: dict = None
    patch_response: dict = None
    number_of_objects_available: int = 0
    aas_identifier: str = None
    sub_model_identifier: str = None
    cd_identifier: str = None
    package_identifier: str = None

    def parse_endpoint_operations(self):
        operations = self.raw_endpoint.get(self.full_url_path)
        for operation in operations:
            self.operations.append(operation)

    def substitute_path_parameters(self):
        pass

    def call_and_validate_get_response(self, schema: dict):
        response = requests.get(url=f'{self.base_url}{self.substituted_url}/')
        jsonschema.validate(response, schema=schema)
        self.number_of_objects_available = len(response)
        self.full_get_response = response
        self.single_get_response = response[0]

    def call_and_validate_post_response(self):
        response = requests.post(url=f'{self.base_url}{self.substituted_url}/', json=self.post_data)
        return response

    def call_and_validate_put_response(self):
        response = requests.put(url=f'{self.base_url}{self.substituted_url}/', json=self.post_data)
        return response

    def call_and_validate_delete(self):
        response = requests.delete(url=f'{self.base_url}{self.substituted_url}/')
        return response

    @property
    def substituted_url(self):
        return

    @staticmethod
    def parse_response(response: Optional[dict[dict], list[dict[dict]]], asset_identifier: bool = False):
        if isinstance(response, list):
            response = response[0]
        if not asset_identifier:
            return response.get('identification').get('id')

    def get_sub_model_identifier_response(self) -> tuple[str, bool]:
        _error = None
        _response = None
        if self.full_url_path.startswith('/aas/submodels'):
            try:
                response = requests.get(url=f'{self.base_url}/aas/submodels/')
                _response = self.parse_response(response=response)
            except Exception as error:
                _error = error
        if self.full_url_path.startswith('/submodel'):
            try:
                response = requests.get(url=f'{self.base_url}/submodels/')
                _response = self.parse_response(response=response)
            except Exception as error:
                _error = error
        if self.full_url_path.startswith('/registry/'):
            try:
                response = requests.get(url=f'{self.base_url}/registry/shell-descriptors/{self.asset_identifier}/submodel-descriptor/')
                _response = self.parse_response(response=response)
            except Exception as error:
                _error = error

        if _response and not _error:
            return _response, False
        return str(_error), True

    def get_aas_identifier_response(self) -> tuple[str, bool]:
        _error = None
        _response = None
        if self.full_url_path.startswith('/shells'):
            try:
                response = requests.get(url=f'{self.base_url}/shells/')
                _response = self.parse_response(response=response, asset_identifier=True)
            except Exception as error:
                _error = error
        if self.full_url_path.startswith('/registry'):
            try:
                response = requests.get(url=f'{self.base_url}/registry/shell-descriptors')
                _response = self.parse_response(response=response, asset_identifier=True)
            except Exception as error:
                _error = error
        if _response:
            if _response.get('modelType')['name'] == 'AssetAdministrationShell':
                _response = _response.get('identification').get('id')
        if self.full_url_path.startswith('/lookup/'):
            try:
                response = requests.get(url=f'{self.base_url}/lookup/shells/')
                _response = self.parse_response(response=response)
                _response = _response.get('id')
            except Exception as error:
                _error = error

        if _response and not _error:
            return _response, False
        return str(_error), True

    def set_submodel_identifier(self) -> None:
        response, error = self.get_sub_model_identifier_response()
        if not error:
            response = convert_to_base64_form(response)
        self.sub_model_identifier = response

    def set_aas_identifier(self) -> None:
        response, error = self.get_aas_identifier_response()
        if not error:
            response = convert_to_base64_form(response)
        self.aas_identifier = response

    def set_cd_identifier(self):
        if self.full_url_path.startswith('/concept'):
            try:
                response = requests.get(url=f'{self.base_url}/concept-descriptions/')
                _response = self.parse_response(response=response)
                self.cd_identifier = convert_to_base64_form(_response.get('identification').get('id'))
            except Exception as error:
                # need to add things to log or file
                pass

    def set_package_identifier(self):
        if self.full_url_path.startswith('/packages'):
            try:
                response = requests.get(url=f'{self.base_url}/packages/')
                _response = self.parse_response(response=response)
                self.package_identifier = convert_to_base64_form(_response.get('identification').get('id'))
            except Exception as error:
                # need to add things to log or file
                pass


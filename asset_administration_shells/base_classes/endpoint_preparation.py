from copy import copy
from dataclasses import dataclass
from typing import Optional, Any, Union

import requests
from requests import Response

from asset_administration_shells.parsers import (
    AssetAdministrationShell, ConceptDescription, Packages
)
from asset_administration_shells.helpers import convert_to_base64_form

SCHEMA_PATH = None
BASE_URL = None


@dataclass
class BaseAASEndPointPreparation:
    """
    This class is the base class which has all the common attributes and methods in it.
    We can extend this class based on our requirements with more functionality
    """
    asset_administration_shells: [AssetAdministrationShell]
    base_url: str
    current_aas = None
    current_sub_model = None
    raw_endpoint: dict
    password: Union[str, None]
    _id: Union[str, None]
    concept_description: ConceptDescription
    packages: Union[Packages, None]
    full_url_path: str
    substituted_url: str = None
    general_path_params_in_schema = ['{aasIdentifier}', '{submodelIdentifier}', '{idShortPath}', '{cdIdentifier}',
                                     '{packageId}']
    path_params: list = None
    get_response_json: list = None
    get_response: Response = None
    single_get_response: dict = None
    post_data: dict = None
    patch_data: dict = None
    put_data: dict = None
    post_response: Response = None
    post_response_json: dict = None
    put_response_json: dict = None
    put_response: Response = None
    delete_response: Response = None
    delete_response_json: dict = None
    patch_response: dict = None
    not_implemented_error_msg: str = 'no matching request mapper found'
    number_of_objects_available: int = 0
    is_implemented: bool = True

    @property
    def session(self):
        if self.password and self._id:
            session = requests.Session()
            session.auth = (self._id, self.password)
            return session
        return False

    def parse_endpoint_operations(self) -> None:
        operations = self.raw_endpoint.get(self.full_url_path)
        for operation in operations:
            self.operations.append(operation)

    def substitute_path_parameters(self) -> None:
        self.substituted_url = copy(self.full_url_path)
        for param in self.general_path_params_in_schema:
            if param in self.full_url_path:
                replacement = None
                if param.startswith('{aas'):
                    for aas in self.asset_administration_shells:
                        for sub_models in aas.sub_models:
                            if sub_models.has_sub_model_elements:
                                self.current_aas = aas
                                replacement = aas.identifier
                                break
                            else:
                                continue
                            break
                if param.startswith('{submodel'):
                    for aas in self.asset_administration_shells:
                        for sub_models in aas.sub_models:
                            if sub_models.has_sub_model_elements:
                                self.current_aas = aas
                    try:
                        for sub_model in self.current_aas.sub_models:
                            if sub_model.has_sub_model_elements:
                                replacement = sub_model.identifier
                                self.current_sub_model = sub_model
                                break
                            else:
                                continue
                    except IndexError as error:
                        print(self.asset_administration_shells)
                        replacement = self.asset_administration_shells[-1].sub_models[-1].identifier
                if param.startswith('{idShort'):
                    replacement = self.current_sub_model.id_short_path_sub_model_elements
                if param.startswith('{cdIdentifier'):
                    replacement = self.concept_description.identifier
                if param.startswith('{package'):
                    if self.packages:
                        replacement = self.packages.identifier
                    else:
                        replacement = convert_to_base64_form('not_available')
                if replacement:
                    self.replace_(param, replacement=replacement)

    def replace_(self, param, replacement):
        self.substituted_url = self.substituted_url.replace(param, replacement)

    def parse_response(self, response: Optional[dict], asset_identifier: bool = False) -> Any:
        if isinstance(response, list):
            response: dict = response[0]
        self.is_implemented = self.has_implementation(response=response)
        if self.is_implemented and not asset_identifier:
            return response.get('identification').get('id')
        return response

    def has_implementation(self, response) -> bool:
        if response.get('success') == 'false' and response.get('messages').get('text') == \
                self.not_implemented_error_msg:
            return False
        return True

    @staticmethod
    def get_single_object_from_response(response: Union[list, dict]) -> dict:
        if isinstance(response, list) and len(response) > 0:
            return response[-1]
        return response

    @property
    def operations(self):
        operations: list = []
        for value in self.raw_endpoint:
            operations.append(value)
        return operations

    @property
    def has_path_parameters(self):
        return '{' in self.full_url_path

    def get_aas_identifier_response(self):
        pass

    def get_submodel_identifier_response(self):
        pass

    @staticmethod
    def get_updated_identification_data_for_post(identification: dict) -> dict:
        _id = identification.get('id')
        if isinstance(_id[-1], int):
            _id_list = list(_id)
            _id_list[-1] = str(int(_id_list[-1]) + 1)
            identification.update({'id': ''.join(_id_list)})
        else:
            _id = _id+'something'
            identification.update({'id': _id})
        return identification

    def create_post_or_put_request_data_from_response(self, put: bool = False, negative: bool = False) -> dict:
        data = copy(self.single_get_response)
        if 'identification' not in data:
            if isinstance(data, list) and len(data) > 0:
                return data[0]
            return data
        identification = data.get('identification')
        # in case of post which is creating another object, we need to provide a new identification, otherwise
        # the AAS server will complain that several objects can not contain same identification.
        if not put:
            if negative:
                # for negative test case we are passing an invalid id which is an int value, while
                # the server is expecting a string url in place of id, so that should fail to save and raise
                # an 404.
                updated_identification = {'id': 999_22}
            else:
                updated_identification = self.get_updated_identification_data_for_post(identification)
            data.update(updated_identification)
        # in case of put which is updating the object, we are just trying to replace the object with
        # exactly same values, that also should work in case of replacement, this is also necessary as we
        # already have those AAS and Submodels saved in memory, that we will use for other test cases, so it is
        # important that we do not alter the identification, which might cause the other tests to fail.
        else:
            if negative:
                # in case of negative test case we will try to put or update the object by providing a false
                # or unavailable object, to check if it is still raising a proper error or not.
                updated_identification = self.get_updated_identification_data_for_post(identification)
                data.update(updated_identification)
            return data

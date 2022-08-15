from copy import copy
from dataclasses import dataclass
from typing import Optional, Any, Union

from requests import Response

SCHEMA_PATH = None
BASE_URL = None


@dataclass
class AasBaseEndPoint:
    raw_endpoint: dict
    base_url: str
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
    aas_identifier: str = None
    is_implemented: bool = True

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
                    replacement = self.aas_identifier
                if param.startswith('{submodel'):
                    replacement = self.sub_model_identifier
                if param.startswith('{idShort'):
                    replacement = self.id_short
                if param.startswith('{cdIdentifier'):
                    replacement = self.cd_identifier
                if param.startswith('{package'):
                    replacement = self.package_identifer
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
        if isinstance(response, list):
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
        _id_list = list(_id)
        _id_list[-1] = str(int(_id_list[-1]) + 1)
        identification.update({'id': ''.join(_id_list)})
        return identification

    def create_request_data_from_response(self):
        data = copy(self.single_get_response)
        identification = data.get('identification')
        updated_identification = self.get_updated_identification_data_for_post(identification)
        data.update(updated_identification)
        return data

    def create_put_request_data_from_response(self):
        data = copy(self.single_get_response)
        # identification = data.pop('identification')
        # data['assetInformation']['globalAssetId']['keys'].append(data['assetInformation']['globalAssetId']['keys'][0])
        # identification = data.pop('idShort')
        # updated_identification = self.get_updated_identification_data_for_post(identification)
        # data.update(updated_identification)
        return data

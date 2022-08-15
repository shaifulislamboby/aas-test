import json

import requests

from aas_base_endpoint import AasBaseEndPoint
from helpers import convert_to_base64_form


class AasShellEndPoint(AasBaseEndPoint):

    def get_aas_identifier_response(self) -> tuple[str, bool]:
        _error = None
        _response = None
        try:
            response = requests.get(url=f'{self.base_url}/shells/').json()
            _response = self.parse_response(response=response, asset_identifier=True)
        except Exception as error:
            _error = error

        if _response and not _error:
            return _response, False
        return str(_error), True

    def set_aas_identifier(self):
        response, error = self.get_aas_identifier_response()
        if self.is_implemented:
            self.aas_identifier = convert_to_base64_form(response.get('identification').get('id'))

    def set_all_required_attributes(self):
        if self.has_path_parameters:
            self.set_aas_identifier()
        if self.is_implemented and 'get' in self.operations:
            self.substitute_path_parameters()
            self.get_response = requests.get(url=f'{self.base_url}{self.substituted_url}')
            self.get_response_json = self.get_response.json()
            self.single_get_response = self.get_single_object_from_response(self.get_response_json)
        self.create_post_and_put_data()
        self.set_all_responses()

    def create_post_and_put_data(self):
        if 'post' in self.operations:
            self.post_data = self.create_request_data_from_response()
        if 'put' in self.operations:
            self.put_data = self.create_request_data_from_response()

    def set_all_responses(self):
        url = f'{self.base_url}{self.substituted_url}'
        if self.is_implemented:
            if self.post_data:
                self.post_response = requests.post(url, json=self.post_data)
                self.post_response_json = self.post_response.json()
            if self.put_data:
                self.put_response = requests.put(url, json=self.put_data)
                self.put_response_json = self.put_response.json()
            if 'delete' in self.operations:
                headers = {'content-type': 'application/json;charset=utf-8'}
                self.delete_response = requests.delete(url, headers=headers, json=None)

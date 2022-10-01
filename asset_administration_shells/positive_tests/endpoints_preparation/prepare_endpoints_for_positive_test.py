import requests

from asset_administration_shells.base_classes.endpoint_preparation import BaseAASEndPointPreparation


class PrepareAASGETPOSTPUTEndPointForPositiveTest(BaseAASEndPointPreparation):

    def set_all_required_attributes(self):
        if self.is_implemented and 'get' in self.operations:
            self.substitute_path_parameters()
            if self.session:
                res = self.session.get(url=f'{self.base_url}{self.substituted_url}')
            else:
                res = requests.get(url=f'{self.base_url}{self.substituted_url}')
            self.get_response = res
            self.get_response_json = self.get_response.json()
            self.single_get_response = self.get_single_object_from_response(self.get_response_json)
        self.create_post_and_put_data()
        self.set_all_responses()

    def create_post_and_put_data(self):
        if 'get' in self.operations:
            if 'post' in self.operations:
                self.post_data = self.create_post_or_put_request_data_from_response()
            if 'put' in self.operations:
                self.put_data = self.create_post_or_put_request_data_from_response(put=True)

    def set_all_responses(self):
        url = f'{self.base_url}{self.substituted_url}'
        if self.is_implemented:
            if self.post_data is not None:
                if self.session:
                    self.post_response = self.session.post(url, json=self.post_data)
                else:
                    self.post_response = requests.post(url, json=self.post_data)
                self.post_response_json = self.post_response.json()
            if self.put_data:
                print(url), print(self.put_data)
                if self.session:
                    self.post_response = self.session.put(url, json=self.put_data)
                else:
                    self.put_response = requests.put(url, json=self.put_data)
                try:
                    self.put_response_json = self.put_response.json()
                except Exception as error:
                    print(error)
                    self.put_response_json = self.put_response.ok

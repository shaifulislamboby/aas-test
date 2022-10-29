import itertools
from itertools import combinations

import requests

from asset_administration_shells_test_suits.base_classes.preparation import (
    BaseAASPreparation
)
from asset_administration_shells_test_suits.helpers.helpers import aas_logger


class PreparePPDPositive(BaseAASPreparation):

    def set_all_required_attributes(self):
        if self.is_implemented and 'get' in self.operations:
            self.substitute_path_parameters()
            url = f'{self.base_url}{self.substituted_url}'
            res = self.session.get(url=url) if self.session else requests.get(url=url)
            # here the is_implemented value will be re-assigned which will
            # be used later on for others responses.
            self.is_implemented = self.has_implementation(res.json())
            if self.is_implemented:
                self.create_query_params(operation='get')
                if self.get_query_params:
                    self.create_response_with_query_params(operation='get', url=url)
                self.get_response = res
                self.get_response_json = self.get_response.json()
                self.single_get_response = self.get_single_object_from_response(self.get_response_json)
        self.create_post_and_put_data()
        self.set_all_responses()

    def create_post_and_put_data(self):
        if 'get' in self.operations and self.is_implemented:
            if 'post' in self.operations:
                self.post_data = self.create_post_or_put_request_data_from_response()
            if 'put' in self.operations:
                self.put_data = self.create_post_or_put_request_data_from_response(put=True)

    def set_all_responses(self):
        url = f'{self.base_url}{self.substituted_url}'
        if self.is_implemented:
            if self.post_data:
                self.post_response = self.session.post(
                    url, json=self.post_data
                ) if self.session else requests.post(url, json=self.post_data)
                self.post_response_json = self.post_response.json()
                self.create_query_params(operation='post')
                if self.post_query_params:
                    self.create_response_with_query_params(operation='post', url=url)
            if self.put_data:
                # todo remove this print statement once finalizing the code.
                print(url), print(self.put_data)
                self.put_response = self.session.put(
                    url, json=self.put_data
                ) if self.session else requests.put(url, json=self.put_data)
                self.create_query_params(operation='put')
                if self.put_query_params:
                    self.create_response_with_query_params(operation='put', url=url)
                try:
                    # this try is for checking if the put response is a json response or
                    # text type response, which is not json parsable.
                    self.put_response_json = self.put_response.json()
                except Exception as error:
                    # todo remove this print statement once finalizing the code.
                    print(error)
                    self.put_response_json = self.put_response.ok

    @aas_logger
    def create_response_with_query_params(self, operation, url) -> None:
        self.create_query_params(operation=operation)
        _attr = getattr(self, f'{operation}_query_params')
        if _attr:
            for param in _attr:
                url += param
                param = param.replace('?', 'question')
                param = param.replace('=', 'equal')
                param = param.replace('&', 'and')
                if self.session:
                    session_ = getattr(self.session, operation)
                request_ = getattr(requests, operation)
                setattr(
                    self, f'{operation}_{param}_response', session_(
                        url=url
                    ) if self.session else request_(
                        url=url
                    )
                )

    @aas_logger
    def create_query_params(self, operation):
        """
        This method will create all the possible combinations of query params for each endpoint.
        """
        query_params = self.query_params.get(operation, None)
        list_of_query_params = []
        if query_params:
            list_of_query_keys = [key for key in query_params]
            if list_of_query_keys:
                for query, value in query_params.items():
                    for val in value:
                        # this will add all the query params for single query.
                        list_of_query_params.append(f'?{query}={val}')
                # combination starts here, if there is multiple query params, then we will make
                # all possible combinations of them and make request.
                if len(list_of_query_keys) > 1:
                    query_combinations = self.create_list_combinations(list_of_query_keys)
                    for combination in query_combinations:
                        dict_combinations: list[dict] = [
                            self.query_params.get(operation).get(value) for value in combination
                        ]

                        _combinations = list(itertools.product(*dict_combinations))
                        for tup in _combinations:
                            _str = '?'
                            for index, _value in enumerate(tup):
                                _str += f'{combination[index]}={_value}&'
                            list_of_query_params.append(_str[:-1])
        setattr(self, f'{operation}_query_params', list_of_query_params)

    @staticmethod
    @aas_logger
    def create_list_combinations(value: list) -> list[list]:
        """
        This method will get all the possible combination for a list of values,
        we will use that for determining the combination of the keys that we have
        as query params.
        Example:
            [1, 2, 3]
            first step ---> [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]
            second step ---> [[1, 2], [1, 3], [2, 3], [1, 2, 3]]
        """
        initial = sum(
            [list(
                map(
                    list, combinations(value, i)
                )
            ) for i in range(
                len(value) + 1
            )
            ], []
        )
        return [element for element in initial if len(element) > 1]

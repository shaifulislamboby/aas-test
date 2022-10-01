from dataclasses import dataclass

import requests

from asset_administration_shells.positive_tests.endpoints_preparation.prepare_endpoints_for_positive_test import (
    PrepareAASGETPOSTPUTEndPointForPositiveTest as PTR
)
from asset_administration_shells.base_classes.base_test import BaseTest, DeleteEndpoint, TestResult


@dataclass
class PositiveTestRunner(BaseTest):
    def start_test(self):
        for path in self.aas_schema.paths:
            test = self.preparation_class(raw_endpoint=self.aas_schema.paths.get(path),
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
                            # this will get the function from the base class (BaseTest class)
                            # we are using getattr for dynamically getting the functions based on http verb
                            function = getattr(self, f'check_{operation}_response_conforms')
                            # in this line we will get response from AasGETPOSTPUTEndPoint class
                            # we are using getattr for dynamically getting the attributes based on http verb
                            response = getattr(test, f'{operation}_response')
                            test_result = function(response)
                            if not isinstance(test_result, str) and not test_result.passed:
                                length_of_dash_sign = len(f'|| Test fails ---> || {path, operation}, substituted-url ='
                                                          f' {test.substituted_url}, error is {test_result} ||\n')
                                file.write(f'|| Test fails ---> || {path, operation}, substituted-url ='
                                           f' {test.substituted_url}, error is {test_result} ||\n')
                            elif test_result == BaseTest.error_message or (not isinstance(test_result, TestResult) and
                                                                           'no matching' in test_result):
                                length_of_dash_sign = len(f'|| This endpoint is not implemented  ---> || '
                                                          f'{path, operation}, substituted-url ='
                                                          f' {test.substituted_url}, error is {test_result} ||\n')
                                file.write(
                                    f'|| This endpoint is not implemented  ---> || {path, operation}, substituted-url ='
                                    f' {test.substituted_url}, error is {test_result}  ||\n')
                            else:
                                length_of_dash_sign = len(
                                    f'|| Test passed ---> || {path, operation}, substituted-url ='
                                    f' {test.substituted_url} ||\n')
                                file.write(f'|| Test passed ---> || {path, operation}, substituted-url ='
                                           f' {test.substituted_url} ||\n')
                        except Exception as error:
                            print(error)
                            length_of_dash_sign = len(f'|| Test returned non parable response or this endpoint is'
                                                      f' not implemented --->'
                                                      f' {path, operation}, substituted-url ='
                                                      f' {test.substituted_url}, error is {error}||\n')
                            file.write(f'|| Test returned non parsable response or this endpoint is'
                                       f' not implemented --->'
                                       f' {path, operation}, substituted-url ='
                                       f' {test.substituted_url}, error is {error} ||\n')
                        file.write('-' * length_of_dash_sign + '\n')
                    elif operation == 'delete' and len(test.operations) > 1:
                        self.delete_urls.append(DeleteEndpoint(substituted_url=test.substituted_url, path=path))
        with open(self.output_file_name, 'a') as file:
            self.test_delete_endpoints(file)

    def test_delete_endpoints(self, file):
        for url in self.delete_urls:
            if not self.session:
                delete_response = requests.delete(url=f'{self.base_url}{url.substituted_url}')
            else:
                delete_response = self.session.delete(url=f'{self.base_url}{url.substituted_url}')
            func = self.check_delete_response_conforms
            try:
                test_result = func(delete_response)
                if not isinstance(test_result, str) and not test_result.passed:
                    length_of_equal_sign = len(f'|| Test fails ---> || {url.path, url.operation}, substituted-url ='
                                               f' {url.substituted_url} ||\n')
                    file.write(f'|| Test fails ---> || {url.path, url.operation}, substituted-url ='
                               f' {url.substituted_url} ||\n')
                elif test_result == BaseTest.error_message:
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

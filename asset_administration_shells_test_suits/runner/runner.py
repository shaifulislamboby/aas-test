import logging as log

import requests

from asset_administration_shells_test_suits.base_classes.base_test import (
    BaseTest, DeleteEndpoint
)
from asset_administration_shells_test_suits.report_writing.report import (
    write_test_results_to_file, write_non_implemented_test_results_to_file
)


class TestRunner(BaseTest):

    def start_test(self, positive=True):
        test_count = 0
        positive_result_count = []
        non_implemented_result_count = []
        failed_result_count = []
        count = {'passed': positive_result_count,
                 'failed': failed_result_count,
                 'non_implemented': non_implemented_result_count
                 }
        for uri in self.aas_schema.paths:
            prepared_instance = self.preparation_class(
                raw_endpoint=self.aas_schema.paths.get(uri),
                base_url=self.base_url,
                full_url_path=uri,
                asset_administration_shells=self.get_asset_administration_shells(positive=positive),
                concept_description=self.get_concept_description(positive=positive),
                packages=None,
                _id=self._id,
                password=self.password
            )
            prepared_instance.set_all_required_attributes(positive=positive)
            sub = prepared_instance.substituted_url
            with open(self.output_file_name, 'a') as file:
                for operation in prepared_instance.operations:
                    if operation != 'delete':
                        # this will get the function from the base class (BaseTest class)
                        # here it is using getattr for dynamically getting the functions based on http verb
                        function = getattr(
                            self, f'check_{operation}_response_conforms'
                        )
                        try:
                            # in this line will get response from AasGETPOSTPUTEndPoint class
                            # getattr has been used for dynamically getting the attributes based on http verb
                            response = getattr(
                                prepared_instance, f'{operation}_response'
                            )
                            test_result = function(response, positive=positive)
                            length_of_dash_sign = write_test_results_to_file(
                                test_result, uri, operation, prepared_instance, file, count
                            )
                            test_count += 1
                        except Exception as error:
                            print(error)
                            log.error(
                                msg='Error occurred during parsing response of this endpoint:'
                                    f' {prepared_instance.substituted_url}'
                            )
                            length_of_dash_sign = write_non_implemented_test_results_to_file(
                                uri, operation, prepared_instance, error, file
                            )
                            test_count += 1
                        if hasattr(prepared_instance, f'{operation}_query_params'):
                            _attr = getattr(prepared_instance, f'{operation}_query_params')
                            if _attr:
                                for param in _attr:
                                    url = uri + param
                                    prepared_instance.substituted_url = sub + param
                                    param = param.replace('?', 'question')
                                    param = param.replace('=', 'equal')
                                    param = param.replace('&', 'and')
                                    res = getattr(
                                        prepared_instance, f'{operation}_{param}_response'
                                    )

                                    try:
                                        test_result = function(res, positive=positive)
                                        length_of_dash_sign = write_test_results_to_file(
                                            test_result, url, operation, prepared_instance, file, count
                                        )
                                        test_count += 1
                                    except Exception as error:
                                        print(error)
                                        length_of_dash_sign = write_non_implemented_test_results_to_file(
                                            uri, operation, prepared_instance, error, file
                                        )
                                        test_count += 1
                                    file.write(
                                        '-' * length_of_dash_sign + '\n'
                                    )

                        file.write(
                            '-' * length_of_dash_sign + '\n'
                        )

                    if operation == 'delete' and len(prepared_instance.operations) > 1:
                        self.delete_urls.append(
                            DeleteEndpoint(
                                substituted_url=prepared_instance.substituted_url, path=uri
                            )
                        )
                file.write(
                    'Test run finished for this endpoint: ' + '\n'
                    f'Test passed till now : {len(count["passed"])} \n'
                    f'Test failed till now : {len(count["failed"])} \n'
                    f'Non implemented endpoints till now : {len(count["non_implemented"])} \n'
                    'Number of total test done till now: ' + str(test_count) + '\n'
                )
        with open(self.output_file_name, 'a') as file:
            self.delete_endpoint_testing(file, positive=positive)

    def delete_endpoint_testing(self, file, positive: bool):
        for url in self.delete_urls:
            if not self.session:
                delete_response = requests.delete(
                    url=f'{self.base_url}{url.substituted_url}'
                )
                get_response_for_deleted_object = requests.get(
                    url=f'{self.base_url}{url.substituted_url}'
                )
            else:
                delete_response = self.session.delete(
                    url=f'{self.base_url}{url.substituted_url}'
                )
                get_response_for_deleted_object = self.session.get(
                    url=f'{self.base_url}{url.substituted_url}'
                )
            try:
                test_result = self.check_delete_response_conforms(
                    delete_response, get_response_for_deleted_object, positive=positive
                )
                length_of_equal_sign = write_test_results_to_file(
                    test_result, url.path, url.operation, url, file, self.positive_result_count
                )
            except Exception as error:
                print(error)
                length_of_equal_sign = write_non_implemented_test_results_to_file(
                    url.path, url.operation, url, error, file
                )
            file.write(
                '-' * length_of_equal_sign + '\n'
            )

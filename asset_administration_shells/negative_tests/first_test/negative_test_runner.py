import requests

from asset_administration_shells.base_classes.test import (
    BaseTest, DeleteEndpoint
)
from asset_administration_shells.test_report_writing.test_report import (
    write_test_results_to_file, write_non_implemented_test_results_to_file
)


class NegativeTestRunner(BaseTest):
    def start_test(self):
        for path in self.aas_schema.paths:
            test = self.preparation_class(
                raw_endpoint=self.aas_schema.paths.get(path), base_url=self.base_url,
                full_url_path=path, asset_administration_shells=self.get_asset_administration_shells(),
                concept_description=self.get_concept_description(),
                packages=None, _id=self._id, password=self.password
            )
            test.set_all_required_attributes()
            with open(self.output_file_name, 'a') as file:
                for operation in test.operations:
                    if operation != 'delete':
                        try:
                            # this will get the function from the base class (BaseTest class)
                            # we are using getattr for dynamically getting the functions based on http verb
                            function = getattr(
                                self, f'check_{operation}_response_conforms'
                            )
                            # in this line we will get response from AasGETPOSTPUTEndPoint class
                            # we are using getattr for dynamically getting the attributes based on http verb
                            response = getattr(
                                test, f'{operation}_response'
                            )
                            test_result = function(response, positive=False)
                            length_of_dash_sign = write_test_results_to_file(
                                test_result, path, operation, test, file
                            )
                        except Exception as error:
                            print(error)
                            length_of_dash_sign = write_non_implemented_test_results_to_file(
                                path, operation, test, error, file
                            )
                        file.write('-' * length_of_dash_sign + '\n')
                    elif operation == 'delete' and len(test.operations) > 1:
                        self.delete_urls.append(
                            DeleteEndpoint(
                                substituted_url=test.substituted_url, path=path
                            )
                        )
        with open(self.output_file_name, 'a') as file:
            self.test_delete_endpoints(file)

    def test_delete_endpoints(self, file):
        for url in self.delete_urls:
            if not self.session:
                delete_response = requests.delete(
                    url=f'{self.base_url}{url.substituted_url}'
                )
            else:
                delete_response = self.session.delete(
                    url=f'{self.base_url}{url.substituted_url}'
                )
            func = self.check_delete_response_conforms
            try:
                test_result = func(
                    delete_response, positive=False
                )
                length_of_equal_sign = write_test_results_to_file(
                    test_result, url.path, url.operation, url, file
                )
            except Exception as error:
                print(error)
                length_of_equal_sign = write_non_implemented_test_results_to_file(
                    url.path, url.operation, url, error, file
                )
            file.write(
                '-' * length_of_equal_sign + '\n'
            )

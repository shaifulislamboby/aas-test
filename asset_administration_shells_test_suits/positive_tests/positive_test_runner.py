import requests

from asset_administration_shells_test_suits.base_classes.test import (
    BaseTest, DeleteEndpoint
)
from asset_administration_shells_test_suits.test_report_writing.test_report import (
    write_test_results_to_file, write_non_implemented_test_results_to_file
)


class TestRunner(BaseTest):
    def start_test(self, positive=True):
        for uri in self.aas_schema.paths:
            prepared_instance = self.preparation_class(
                raw_endpoint=self.aas_schema.paths.get(uri),
                base_url=self.base_url,
                full_url_path=uri,
                asset_administration_shells=self.get_asset_administration_shells(),
                concept_description=self.get_concept_description(),
                packages=None,
                _id=self._id,
                password=self.password
            )
            prepared_instance.set_all_required_attributes()
            with open(self.output_file_name, 'a') as file:
                for operation in prepared_instance.operations:
                    if operation != 'delete':
                        try:
                            # this will get the function from the base class (BaseTest class)
                            # here it is using getattr for dynamically getting the functions based on http verb
                            function = getattr(
                                self, f'check_{operation}_response_conforms'
                            )
                            # in this line will get response from AasGETPOSTPUTEndPoint class
                            # getattr has been used for dynamically getting the attributes based on http verb
                            response = getattr(
                                prepared_instance, f'{operation}_response'
                            )
                            test_result = function(response, positive=positive)
                            length_of_dash_sign = write_test_results_to_file(
                                test_result, uri, operation, prepared_instance, file
                            )
                        except Exception as error:
                            print(error)
                            length_of_dash_sign = write_non_implemented_test_results_to_file(
                                uri, operation, prepared_instance, error, file
                            )
                        file.write(
                            '-' * length_of_dash_sign + '\n'
                        )
                    elif operation == 'delete' and len(prepared_instance.operations) > 1:
                        self.delete_urls.append(
                            DeleteEndpoint(
                                substituted_url=prepared_instance.substituted_url, path=uri
                            )
                        )
        with open(self.output_file_name, 'a') as file:
            self.test_delete_endpoints(file, positive=positive)

    def test_delete_endpoints(self, file, positive: bool):
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
                test_result = func(delete_response, positive=positive)
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

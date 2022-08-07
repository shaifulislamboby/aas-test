from dataclasses import dataclass
import sys

from aas_schema_parser import AasSchemaParser
from shells_endpoints import AasShellEndPoint


@dataclass
class BaseTest:
    aas_schema: AasSchemaParser
    output_file_name: str
    base_url: str

    @staticmethod
    def check_get_response_conforms(response):
        if response.status_code != 200:
            return 'fail'

    @staticmethod
    def check_post_response_conforms(response):
        if response.status_code != 201:
            return 'fail'

    @staticmethod
    def check_put_response_conforms(response):
        if response.status_code not in (200, 204):
            return 'fail'

    @staticmethod
    def check_delete_response_conforms(response):
        if response.status_code != 204:
            return 'fail'

    def start_test(self):
        for path in self.aas_schema.paths:
            if path.startswith('/shells'):
                test = AasShellEndPoint(raw_endpoint=self.aas_schema.paths.get(path),
                                        base_url=base_url,
                                        full_url_path=path)
                test.set_all_required_attributes()
                with open(output_file_name, 'a') as file:
                    for value in test.operations:
                        func = getattr(self, f'check_{value}_response_conforms')
                        response = getattr(test, f'{value}_response')
                        if func(response) == 'fail':
                            file.write(f'test fails ---> {path, value}\n')
                        else:
                            file.write(f'test passed ---> {path, value}\n')


if __name__ == '__main__':
    file_location = 'open_api_specification_aas_v2.json'
    output_file_name = 'output.txt'
    base_url = 'http://0.0.0.0:8080'
    Aas = AasSchemaParser(file_location=file_location)
    BaseTest(Aas, output_file_name, base_url).start_test()

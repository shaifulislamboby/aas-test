from copy import copy

from asset_administration_shells.helpers import convert_to_base64_form
from asset_administration_shells.positive_tests.endpoints_preparation.positive_test import (
    PreparePOSTPUTDataPositiveTest
)


class PreparePOSTPUTDataForFirstNegativeTest(PreparePOSTPUTDataPositiveTest):
    negative_get_response = None

    def create_post_or_put_request_data_from_response(self, put: bool = False, negative: bool = False):
        return {}

    def substitute_path_parameters(self):
        self.substituted_url = copy(self.full_url_path)
        for param in self.general_path_params_in_schema:
            if param in self.full_url_path:
                replacement = convert_to_base64_form('not_available')
                self.replace_(param, replacement=replacement)

from copy import deepcopy
from dataclasses import dataclass

from asset_administration_shells_test_suits.helpers.helpers import (
    convert_to_base64_form,
)
from asset_administration_shells_test_suits.positive_tests.endpoints_preparation.positive_test import (
    PositiveTestExecutor,
)


@dataclass
class NegativeTestExecutor(PositiveTestExecutor):
    positive = False

    def create_post_or_put_request_data_from_response(
            self, put: bool = False, positive: bool = False
    ):
        return {"test": "negative"}

    def substitute_path_parameters(self):
        self.substituted_url = deepcopy(self.full_url_path)
        for param in self.general_path_params_in_schema:
            if param in self.full_url_path:
                replacement = convert_to_base64_form("not_available")
                self.replace_(param, replacement=replacement)
                
    def set_all_required_attributes(self, positive=False, use_links=False):
        super().set_all_required_attributes(positive, use_links)

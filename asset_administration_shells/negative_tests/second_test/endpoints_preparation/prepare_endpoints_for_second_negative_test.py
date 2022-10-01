from dataclasses import dataclass


from asset_administration_shells.positive_tests.endpoints_preparation.prepare_endpoints_for_positive_test import (
    PrepareAASGETPOSTPUTEndPointForPositiveTest as PATT
)


@dataclass
class PrepareAASGETPOSTPUTEndPointForSecondNegativeTest(PATT):
    """
    This is second negative test suit for, which will pass an invalid data
    to check if the server response with a valid status code and can handle
    data that are not conforms with their schema.
    """
    def create_post_and_put_data(self):
        if 'get' in self.operations:
            if 'post' in self.operations:
                self.post_data = self.create_post_or_put_request_data_from_response(negative=True)
            if 'put' in self.operations:
                self.put_data = self.create_post_or_put_request_data_from_response(put=True, negative=True)


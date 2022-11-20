from asset_administration_shells_test_suits.positive_tests.endpoints_preparation.positive_test import (
    PositiveExecutor,
)


class NegativeExecutorThree(PositiveExecutor):
    positive = False
    """
    This is third negative test suit for, which will pass an invalid data
    and invalid query param in all the endpoints
    to check if the server response with a valid status code and can handle
    data that are not conforms with their schema.
    """

    def create_post_and_put_data(self) -> None:
        if "get" in self.operations:
            if "post" in self.operations:
                self.post_data = self.create_post_or_put_request_data_from_response(
                    positive=self.positive
                )
            if "put" in self.operations:
                self.put_data = self.create_post_or_put_request_data_from_response(
                    put=True, positive=self.positive
                )

    def create_query_params(self, operation, positive: bool = False):
        super().create_query_params(operation, positive)

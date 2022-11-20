import logging
import traceback
from dataclasses import dataclass, field
from json import JSONDecodeError
from typing import Type, Union, Optional

import jsonschema
import requests
from jsonschema.exceptions import ValidationError
from requests import Session, Response

from asset_administration_shells_test_suits.base_classes.executor import Executor
from asset_administration_shells_test_suits.helpers.helpers import aas_logger
from asset_administration_shells_test_suits.parsers import (
    AasSchemaParser,
    ConceptDescription,
    AssetAdministrationShell,
)
from asset_administration_shells_test_suits.report_writing.report import (
    write_test_results_to_file,
    write_test_metrics,
)

NOT_IMPLEMENTATION_MSG: str = "not implemented"
SCHEMA_VALIDATION_FAILED_MSG: str = "schema validation failed"
JSON_DECODE_ERROR_MSG = "invalid json response"


# use enum in pass field, instead of passed .

@dataclass
class TestResult:
    passed: bool = False
    message: str = ""
    status_code: int = 1
    schema_conformation: bool = False


@dataclass
class DeleteEndpoint:
    substituted_url: str
    path: str
    operation: str = "delete"


@dataclass
class TestRunner:
    executor_class: Type[Executor]
    aas_schema: AasSchemaParser
    _id: Union[str, None]
    password: Union[str, None]
    output_file_name: str
    base_url: str
    aas_path: str
    sub_model_path: str
    concept_description_path: str
    error_message = (
        "no matching request mapper found for URL",
        "not allowed for",
        "currently not supported",
        "no handler defined",
        "error parsing",
        "invalid output modifier",
    )
    delete_urls: [DeleteEndpoint] = field(default_factory=lambda: [])
    positive_result_count: list = field(default_factory=lambda: [])

    @property
    def session(self) -> Union[Session, bool]:
        if self.password and self._id:
            session = requests.Session()
            session.auth = (self._id, self.password)
            return session
        return False

    def validate_response_body_against_aas_schema(
            self, response: Response
    ) -> TestResult:
        try:
            # we will validate the json schema in case of get verb's response, non-conforming
            # json response will raise an exception
            jsonschema.validate(response.json(), schema=self.aas_schema.raw_schema)
            return TestResult(passed=True, schema_conformation=True, status_code=True)
        except ValidationError:
            return TestResult(
                passed=True,
                schema_conformation=False,
                status_code=response.status_code,
                message=SCHEMA_VALIDATION_FAILED_MSG,
            )
        except JSONDecodeError:
            return TestResult(
                passed=True,
                schema_conformation=False,
                status_code=response.status_code,
                message=JSON_DECODE_ERROR_MSG,
            )

    @aas_logger
    def check_get_response_conforms(
            self, response: Optional[Response], positive: bool = True
    ) -> TestResult:
        if response is None:
            return TestResult(message=NOT_IMPLEMENTATION_MSG)
        response_status_code = 200 if positive else 404
        if response.status_code != response_status_code:
            return self.parse_error_message(response)
        return self.validate_response_body_against_aas_schema(response=response)

    @aas_logger
    def check_post_response_conforms(
            self, response: Optional[Response], positive: bool = True
    ) -> TestResult:
        if response is None:
            return TestResult(message=NOT_IMPLEMENTATION_MSG)
        response_status_code = 201 if positive else 404
        if response.status_code != response_status_code:
            return self.parse_error_message(response)
        return self.validate_response_body_against_aas_schema(response=response)

    @aas_logger
    def check_put_response_conforms(
            self, response: Optional[Response], positive: bool = True
    ) -> TestResult:
        if response is None:
            return TestResult(message=NOT_IMPLEMENTATION_MSG)
        response_status_code = (
            (
                200,
                204,
            )
            if positive
            else (404,)
        )
        if response.status_code not in response_status_code:
            return self.parse_error_message(response)
        return self.validate_response_body_against_aas_schema(response=response)

    @aas_logger
    def check_delete_response_conforms(
            self,
            response: Optional[Response],
            get_response_for_deleted_object: Optional[Response],
            positive: bool = True,
    ) -> TestResult:
        if response is None:
            return TestResult(message=NOT_IMPLEMENTATION_MSG)
        response_status_code = (204,) if positive else (404,)
        if response.status_code not in response_status_code:
            return self.parse_error_message(response)
        # this line is added for checking if the object has been deleted for real or not.
        if get_response_for_deleted_object.status_code != 404:
            return TestResult(status_code=response.status_code)
        return TestResult(passed=True, status_code=response.status_code)

    @staticmethod
    def parse_error_message(response: Optional[Response]) -> TestResult:
        try:
            message = response.json().get("messages")[0]["text"]
            if any(error_m in message for error_m in TestRunner.error_message):
                return TestResult(status_code=response.status_code, message=message)
            return TestResult(status_code=response.status_code)
        except Exception as error:
            logging.log(
                msg=f"error occurred during parsing error message : {error}",
                level=logging.ERROR,
            )
            return TestResult(
                status_code=response.status_code,
                message=f"{traceback.TracebackException}",
            )

    def get_asset_administration_shells(
            self, positive: bool = True
    ) -> list[AssetAdministrationShell]:
        if not positive:
            return []
        if self.session:
            response = self.session.get(url=self.aas_path).json()
        else:
            response = requests.get(url=self.aas_path).json()
        initial_list = []
        for res in response:
            initial_list.append(
                AssetAdministrationShell(
                    raw_asset_administration_shell=res,
                    sub_model_collection_uri=self.sub_model_path,
                    _id=self._id,
                    password=self.password,
                )
            )
        return initial_list

    def get_concept_description(
            self, positive: bool = True
    ) -> Optional[ConceptDescription]:
        if not positive:
            return ""
        try:
            return ConceptDescription(
                raw_concept_description=requests.get(
                    url=self.concept_description_path
                ).json()[0],
                _id=self._id,
                password=self.password,
            )
        except Exception as error:
            print(error)
            return None

    def start_test(self):
        test_count: int = 0
        positive_result_count: list = []
        non_implemented_result_count: list = []
        failed_result_count: list = []
        counts_dict = {
            "passed": positive_result_count,
            "failed": failed_result_count,
            "non_implemented": non_implemented_result_count,
        }
        asset_administration_shells = self.get_asset_administration_shells(
            positive=self.executor_class.positive
        )
        concept_description = self.get_concept_description(
            positive=self.executor_class.positive
        )
        for uri in self.aas_schema.paths:
            executed_instance = self.executor_class(
                raw_endpoint=self.aas_schema.paths.get(uri),
                base_url=self.base_url,
                full_url_path=uri,
                asset_administration_shells=asset_administration_shells,
                concept_description=concept_description,
                packages=None,
                _id=self._id,
                password=self.password,
            )
            executed_instance.set_all_required_attributes(
                positive=self.executor_class.positive
            )
            sub = executed_instance.substituted_url
            for operation in executed_instance.operations:
                if operation == "delete" and len(executed_instance.operations) > 1:
                    self.delete_urls.append(
                        DeleteEndpoint(
                            substituted_url=executed_instance.substituted_url, path=uri
                        )
                    )
                    continue
                response_conformation_function = {
                    "get": self.check_get_response_conforms,
                    "post": self.check_post_response_conforms,
                    "put": self.check_put_response_conforms,
                }[operation]
                response = {
                    "get": executed_instance.get_response,
                    "post": executed_instance.post_response,
                    "put": executed_instance.put_response,
                }[operation]
                test_result = response_conformation_function(
                    response, positive=self.executor_class.positive
                )
                write_test_results_to_file(
                    test_result,
                    uri,
                    operation,
                    executed_instance,
                    self.output_file_name,
                    counts_dict,
                )
                test_count += 1
                if hasattr(executed_instance, f"{operation}_query_params"):
                    _attr = getattr(executed_instance, f"{operation}_query_params")
                    if _attr:
                        for param in _attr:
                            url = uri + param
                            executed_instance.substituted_url = sub + param
                            param = param.replace("?", "question")
                            param = param.replace("=", "equal")
                            param = param.replace("&", "and")
                            res = getattr(
                                executed_instance, f"{operation}_{param}_response"
                            )
                            test_result = response_conformation_function(
                                res, positive=self.executor_class.positive
                            )
                            write_test_results_to_file(
                                test_result,
                                url,
                                operation,
                                executed_instance,
                                self.output_file_name,
                                counts_dict,
                            )
                            test_count += 1
        write_test_metrics(
            test_count=test_count, counts_dict=counts_dict, file=self.output_file_name
        )

        self.delete_endpoint_testing(positive=self.executor_class.positive)

    def delete_endpoint_testing(self, positive: bool):
        for url in self.delete_urls:
            if not self.session:
                delete_response = requests.delete(
                    url=f"{self.base_url}{url.substituted_url}"
                )
                get_response_for_deleted_object = requests.get(
                    url=f"{self.base_url}{url.substituted_url}"
                )
            else:
                delete_response = self.session.delete(
                    url=f"{self.base_url}{url.substituted_url}"
                )
                get_response_for_deleted_object = self.session.get(
                    url=f"{self.base_url}{url.substituted_url}"
                )
            test_result = self.check_delete_response_conforms(
                delete_response, get_response_for_deleted_object, positive=positive
            )
            write_test_results_to_file(
                test_result,
                url.path,
                url.operation,
                url,
                self.output_file_name,
                self.positive_result_count,
            )

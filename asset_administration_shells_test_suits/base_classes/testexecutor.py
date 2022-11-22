from copy import deepcopy
from dataclasses import dataclass
from typing import Union

import requests
from requests import Response, Session

from asset_administration_shells_test_suits.parsers import (
    AssetAdministrationShell,
    ConceptDescription,
    Package,
)
from asset_administration_shells_test_suits.helpers.helpers import (
    convert_to_base64_form,
    create_url_encoded_from_id,
)


@dataclass
class TestExecutor:
    """
    This class is the base class which has all the common attributes and methods in it for the preparation of test
    suit.
    We can extend this class based on our requirements with more functionality
    """

    asset_administration_shells: [AssetAdministrationShell]
    resolved_path_parameters: dict
    base_url: str
    current_aas = None
    current_sub_model = None
    raw_endpoint: dict
    password: Union[str, None]
    _id: Union[str, None]
    concept_description: ConceptDescription
    packages: Union[Package, None]
    full_url_path: str
    substituted_url: str = None
    general_path_params_in_schema = [
        "{aasIdentifier}",
        "{submodelIdentifier}",
        "{idShortPath}",
        "{cdIdentifier}",
        "{packageId}",
        "{handleId}",
    ]
    get_response_json: list = None
    get_response: Response = None
    single_get_response: dict = None
    post_data: dict = None
    put_data: dict = None
    post_response: Response = None
    put_response: Response = None
    delete_response: Response = None
    not_implemented_error_msg: str = "no matching request mapper found"
    is_implemented: bool = True
    positive: bool = True

    @property
    def session(self) -> Union[Session, bool]:
        if self.password and self._id:
            session = requests.Session()
            session.auth = (self._id, self.password)
            return session
        return False

    @property
    def query_params(self) -> dict[str : dict[str:list]]:
        """
        This method will parse all the query params that any verbs have in any endpoint,
        and make a dict of verbs which contains dict where the key is the param and
        the list is the possible, values for the query param.
        Example of a verb get with
        {
        'get': {'content': ['normal', 'trimmed', 'value', 'reference', 'path']}
        }
        """
        operations = self.raw_endpoint
        query_params = {}
        for operation, value in operations.items():
            if "parameters" in value:
                query_params[operation] = {
                    parameter.get("name"): parameter.get("schema").get("enum")
                    for parameter in value.get("parameters")
                    if parameter.get("in") == "query"
                    and parameter.get("schema").get("enum")
                }
        return query_params

    def substitute_path_params_using_resolved_links(self) -> None:
        self.substituted_url = deepcopy(self.full_url_path)
        for operation, value in self.raw_endpoint.items():
            operation_id = value.get("operationId")
            if "parameters" in value:
                parameters = value.get("parameters")
                for parameter in parameters:
                    if parameter.get("in") == "path" and parameter.get("required"):
                        parameter_name = parameter.get("name")
                        parameter_description = parameter.get("description")
                        parameter_values = self.resolved_path_parameters.get(
                            parameter_name, None
                        )
                        # placeholder in case of value not found this will be used as substitution.
                        parameter_value = "Not Found"
                        if parameter_values:
                            for params_operation_id in parameter_values:
                                if params_operation_id.get(operation_id):
                                    parameter_value = params_operation_id.get(
                                        operation_id
                                    )
                                    break
                        if "BASE64" in parameter_description:
                            self.replace_(
                                f"{{{parameter_name}}}",
                                replacement=convert_to_base64_form(parameter_value),
                            )
                        else:
                            self.replace_(
                                f"{{{parameter_name}}}",
                                replacement=create_url_encoded_from_id(parameter_value),
                            )
                break

    def substitute_path_parameters(self) -> None:
        self.substituted_url = deepcopy(self.full_url_path)
        fake_value = convert_to_base64_form("https://www.ovgu.de")
        for param in self.general_path_params_in_schema:
            if param in self.full_url_path:
                replacement = None
                if not self.asset_administration_shells:
                    replacement = fake_value
                if param.startswith("{aas"):
                    for aas in self.asset_administration_shells:
                        for sub_models in aas.sub_models:
                            if sub_models.has_sub_model_elements:
                                self.current_aas = aas
                                replacement = aas.identifier
                                break
                            else:
                                continue
                if param.startswith("{submodel"):
                    for aas in self.asset_administration_shells:
                        for sub_models in aas.sub_models:
                            if sub_models.has_sub_model_elements:
                                self.current_aas = aas
                    try:
                        if hasattr(self.current_aas, "sub_models"):
                            for sub_model in self.current_aas.sub_models:
                                if sub_model.has_sub_model_elements:
                                    replacement = sub_model.identifier
                                    self.current_sub_model = sub_model
                                    break
                                else:
                                    continue
                    except IndexError:
                        print(self.asset_administration_shells)
                        replacement = (
                            self.asset_administration_shells[-1]
                            .sub_models[-1]
                            .identifier
                        )
                if param.startswith("{idShort"):
                    if self.current_sub_model:
                        replacement = (
                            self.current_sub_model.id_short_path_sub_model_elements
                        )
                    else:
                        replacement = fake_value
                if param.startswith("{cdIdentifier"):
                    if self.concept_description:
                        replacement = self.concept_description.identifier
                    else:
                        replacement = fake_value
                if param.startswith("{package"):
                    if self.packages:
                        replacement = self.packages.identifier
                    else:
                        replacement = convert_to_base64_form("not_available")

                if replacement:
                    self.replace_(param, replacement=replacement)

    def replace_(self, param: str, replacement: str) -> None:
        self.substituted_url = self.substituted_url.replace(param, replacement)

    def has_implementation(self, response: Union[list, dict]) -> bool:
        if isinstance(response, list) and response:
            response = response[0]
        if isinstance(response, dict):
            try:
                if (
                    response.get("success") == "false"
                    and response.get("messages").get("text")
                    == self.not_implemented_error_msg
                ):
                    return False
            except Exception as error:
                print(error)
        return True

    @staticmethod
    def get_single_object_from_response(response: Union[list, dict]) -> dict:
        if isinstance(response, list) and len(response) > 0:
            return response[-1]
        return response

    @property
    def operations(self) -> list:
        operations: list = []
        for value in self.raw_endpoint:
            operations.append(value)
        return operations

    @property
    def has_path_parameters(self) -> bool:
        return "{" in self.full_url_path

    @staticmethod
    def get_new_identification(identification: dict) -> dict:
        _id = identification.get("id")
        if _id and _id[-1].isdigit():
            _id_list = list(_id)
            _id_list[-1] = str(int(_id_list[-1]) + 1)
            identification.update({"id": "".join(_id_list)})
        else:
            _id = _id + "something"
            identification.update({"id": _id})
        return identification

    def create_post_or_put_request_data_from_response(
        self, put: bool = False, positive: bool = True
    ) -> dict:
        data = deepcopy(self.single_get_response)
        if "identification" not in data:
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
                if positive:
                    return data
                else:
                    data["test_for_failure"] = {"test": "test for failure"}
                    return data
            if not positive and isinstance(data, dict):
                data["test_for_failure"] = {"test": "test for failure"}
                return data
            return data
        identification = data.get("identification")
        # in case of post which is creating another object, we need to provide a new identification, otherwise
        # the AAS server will complain that several objects can not contain same identification.
        if not put:
            if not positive:
                # for negative test case we are passing an invalid id which is an int value, while
                # the server is expecting a string url in place of id, so that should fail to save and raise
                # an 404.
                updated_identification = {"id": 999_22}
            else:
                updated_identification = self.get_new_identification(identification)
            data.update(updated_identification)
        # in case of put which is updating the object, we are just trying to replace the object with
        # exactly same values, that also should work in case of replacement, this is also necessary as we
        # already have those AAS and Submodels saved in memory, that we will use for other test cases, so it is
        # important that we do not alter the identification, which might cause the other tests to fail.
        else:
            if not positive:
                # in case of negative test case we will try to put or update the object by providing a false
                # or unavailable object, to check if it is still raising a proper error or not.
                updated_identification = self.get_new_identification(identification)
                data.update(updated_identification)
        return data

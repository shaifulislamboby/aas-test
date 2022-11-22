import re
from collections import defaultdict
from dataclasses import dataclass, field
import json

import requests


@dataclass
class AasSchemaParser:
    """
    This class is the main schema parser, which will parse the openapi
    specification from the provided path, and load the necessary information
    for the testing.
    """

    file_location: str

    @property
    def number_of_endpoints(self) -> int:
        return len(self.raw_schema.get("paths"))

    @property
    def raw_schema(self) -> dict:
        return json.load(open(self.file_location))

    @property
    def paths(self) -> dict:
        return self.raw_schema.get("paths")


@dataclass
class AASLinkResolver:
    aas_schema: AasSchemaParser
    base_url: str
    path_params: dict[str:list] = field(default_factory=lambda: defaultdict(list))

    @property
    def paths_with_link(self) -> list[str]:
        return [
            path
            for path, value in self.aas_schema.paths.items()
            if "get" in value
            and value.get("get").get("responses").get("200").get("links", False)
        ]

    def resolve_links(self, response_status: str = "200"):
        for value in self.paths_with_link:
            response = requests.get(url=f"{self.base_url}{value}")
            if response.status_code != 200:
                continue
            response = response.json()
            for operation_id, operation_value in (
                self.aas_schema.paths.get(value)
                .get("get")
                .get("responses")
                .get(response_status)
                .get("links")
                .items()
            ):
                parameter_dict: dict = operation_value["parameters"]
                parameter_dict_keys_list = list(parameter_dict.keys())
                self.path_params[parameter_dict_keys_list[0]].append(
                    {
                        operation_value["operationId"]: self.get_value_by_link_location(
                            response,
                            operation_value["parameters"][parameter_dict_keys_list[0]],
                        )
                    }
                )

    @staticmethod
    def get_value_by_link_location(response, location: str):
        split_location = location.split(".")
        desired_value = response
        for value in split_location:
            if value == "$response":
                continue
            if "body" in value:
                if value.endswith("]"):
                    regex = re.compile("body#\[(\d+)\]")
                    index = regex.findall(value)
                    desired_value = desired_value[int(index[0])]
            elif value.endswith("]"):
                inner_value = value.split("#")
                desired_value = desired_value.get(inner_value[0])
                if desired_value:
                    desired_value = desired_value[
                        int(inner_value[-1].replace("[", "").replace("]", ""))
                    ]
            else:
                desired_value = desired_value.get(value)
        return desired_value

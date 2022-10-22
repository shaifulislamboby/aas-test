from dataclasses import dataclass
import json


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
        return len(self.raw_schema.get('paths'))

    @property
    def raw_schema(self) -> dict:
        return json.load(open(self.file_location))

    @property
    def paths(self) -> dict:
        return self.raw_schema.get('paths')


class Path:
    pass
